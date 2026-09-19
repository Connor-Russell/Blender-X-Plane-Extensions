#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      12/11/2025
#Module:    xp_attached_obj_preview.py
#Purpose:   Provide a class that allows for importing of simplified X-Plane objects into Blender for previewing purposes.

import bpy
import os
import mathutils
import math

from .. import material_config
from ..Helpers import misc_utils
from ..Helpers import anim_utils
from ..Helpers import geometery_utils
from ..Helpers import anim_utils
from ..Helpers import light_data    #These are defines for the parameter layout of PARAM lights
from ..Helpers import decal_utils
from ..Helpers import log_utils
from ..Helpers import file_utils
from typing import List
from .xp_obj import draw_call
from .xp_obj import draw_call_state
from bpy.app.handlers import persistent # type: ignore

#Lights don't actually use LODs, but if there are LOD buckets, XP2B requires them to be in *one*. But if there's no LOD buckets they can't be in *any*. So we have a single global variable to set what bucket ot put them in
obj_does_use_lods = False
existing_objects = set()
currently_processing = set()

class attached_object_preview:
    """
    Class to represent a lightweight X-Plane object. This class provides functions to import the object into Blender.
    """

    #Define instance variables
    def __init__(self):
        self.verticies = []  #type: List[geometery_utils.xp_vertex]  #List of verticies in the object
        self.indicies = []  #type: List[int]  #List of indices in the object
        self.draw_calls = [] #type: List[draw_call]
        self.name = ""

        #Base material
        self.alb_texture = ""
        self.nml_texture = ""
        self.lit_texture = ""
        self.mat_texture = ""
        self.do_separate_material_texture = False

        #Draped material
        self.draped_alb_texture = ""
        self.draped_nml_tile_rat = 1.0
        self.draped_nml_texture = ""
        self.draped_lit_texture = ""

        self.filepath = ""

    def read(self, in_obj_path):

        log_utils.new_section(f"Read attached .obj {in_obj_path}")

        self.name = os.path.basename(in_obj_path)
        self.filepath = file_utils.to_relative(in_obj_path).replace("\\", "/")

        trans_matrix = [1, -1, 1]

        cur_start_lod = 0
        cur_is_draped_tris = False

        with open(in_obj_path, "r") as f:
            lines = f.readlines()
        
        for line in lines:

            line = line.strip()
            tokens = line.split()

            if len(tokens) == 0:
                continue

            # Defensive: check token count for each command before using tokens
            cmd = tokens[0]
            # Map of command to minimum required tokens (based on usage below)
            min_tokens = {
                'VT': 9,
                'IDX10': 11,
                'IDX': 2,
                'TRIS': 3,
                'PARTICLE_SYSTEM': 2,
                'BLEND_GLASS': 1,
                'GLOBAL_luminance': 2,
                'TEXTURE': 2,
                'TEXTURE_MAP': 3,
                'TEXTURE_NORMAL': 2,
                'TEXTURE_DRAPED': 2,
                'TEXTURE_DRAPED_NORMAL': 3,
                'TEXTURE_DRAPED_LIT': 2,
                'TEXTURE_LIT': 2,
                'GLOBAL_no_blend': 2,
                'GLOBAL_shadow_blend': 2,
                'ATTR_LOD': 3,
            }
            
            # Only check if command is in our map
            if cmd in min_tokens and len(tokens) < min_tokens[cmd]:
                log_utils.warning(f"Not enough tokens for command '{cmd}'! Expected at least {min_tokens[cmd]}, got {len(tokens)}. Line: '{line}'")
                continue

            if tokens[0] == "VT":
                #We flip Y and Z because of the way Blender and X-Plane handle coordinates
                vert = geometery_utils.xp_vertex(
                    float(tokens[1]) * trans_matrix[0], float(tokens[3]) * trans_matrix[1], float(tokens[2]) * trans_matrix[2], 
                    float(tokens[4]) * trans_matrix[0], float(tokens[6]) * trans_matrix[1], float(tokens[5]) * trans_matrix[2], 
                    float(tokens[7]), float(tokens[8])
                )
                self.verticies.append(vert)

            elif tokens[0] == "IDX10":
                #List of 10 indices
                for i in range(10):
                    self.indicies.append(int(tokens[i+1]))

            elif tokens[0] == "IDX":
                #Single index
                self.indicies.append(int(tokens[1]))

            elif tokens[0] == "ATTR_draped":
                cur_is_draped_tris = True
            
            elif tokens[0] == "ATTR_no_draped":
                cur_is_draped_tris = False
            
            elif tokens[0] == "TRIS":
                #Draw call. Start index and length
                dc = draw_call()
                dc.start_index = int(float(tokens[1]))
                dc.length = int(float(tokens[2]))

                #This just let's it grab the right material when it is added
                dc.state = draw_call_state()
                dc.state.draped = cur_is_draped_tris

                if cur_start_lod == 0:
                    self.draw_calls.append(dc)

            elif tokens[0] == "TEXTURE" and len(tokens) >= 2:
                self.alb_texture = tokens[1]
                if self.draped_alb_texture == "":
                    self.draped_alb_texture = tokens[1]
                cur_in_draped_mat = False
            
            elif tokens[0] == "TEXTURE_MAP":
                if tokens[1].lower() == "normal":
                    self.nml_texture = tokens[2]
                elif tokens[1].lower() == "material_gloss":
                    self.mat_texture = tokens[2]
                cur_in_draped_mat = False

            elif tokens[0] == "TEXTURE_NORMAL":
                self.nml_texture = tokens[1]
                if self.draped_nml_texture == "":
                    self.draped_nml_texture = tokens[1]
                cur_in_draped_mat = False

            elif tokens[0] == "TEXTURE_DRAPED":
                self.draped_alb_texture = tokens[1]
                self.obj_mode = "scenery"
                cur_in_draped_mat = True

            elif tokens[0] == "TEXTURE_DRAPED_NORMAL":
                self.draped_nml_tile_rat = float(tokens[1])
                self.draped_nml_texture = tokens[2]
                cur_in_draped_mat = True

            elif tokens[0] == "TEXTURE_DRAPED_LIT":
                self.draped_lit_texture = tokens[1]
                cur_in_draped_mat = True

            elif tokens[0] == "TEXTURE_LIT":
                self.lit_texture = tokens[1]
                if self.draped_lit_texture == "":
                    self.draped_lit_texture = tokens[1]

            elif tokens[0] == "ATTR_LOD":
                #ANIM_lod <start> <end>
                cur_start_lod = float(tokens[1])
                cur_end_lod = float(tokens[2])

        def resolve_texture_path(texture_name):
            #Make the texture absolute (it's currently relative to the .obj path), then make it relative to the .blend file and return that value
            if texture_name == "":
                return ""
            abs_path = os.path.normpath(os.path.dirname(in_obj_path) + os.path.sep + texture_name)
            return file_utils.to_relative(abs_path)
        
        self.alb_texture = resolve_texture_path(self.alb_texture)
        self.nml_texture = resolve_texture_path(self.nml_texture)
        self.lit_texture = resolve_texture_path(self.lit_texture)
        self.mat_texture = resolve_texture_path(self.mat_texture)
        self.draped_alb_texture = resolve_texture_path(self.draped_alb_texture)
        self.draped_nml_texture = resolve_texture_path(self.draped_nml_texture)
        self.draped_lit_texture = resolve_texture_path(self.draped_lit_texture)
            
    def to_scene(self, target_parent, target_collection, make_real=False):
        log_utils.new_section(f"Creating attached .obj object {self.name}")

        #Create the base material
        all_mats = []
        mat = bpy.data.materials.new(name=self.name)
        mat.use_nodes = True
        xp_mat = mat.xp_materials
        xp_mat.alb_texture = self.alb_texture
        xp_mat.normal_texture = self.nml_texture
        if not file_utils.is_empty(self.mat_texture):
            xp_mat.material_texture = self.mat_texture
            xp_mat.do_separate_material_texture = True
        xp_mat.lit_texture = self.lit_texture

        mat.name = self.name

        all_mats.append(mat)

        #Create the draped material if it exists
        any_draped_dcs = False
        for dc in self.draw_calls:
            if dc.state.draped:
                any_draped_dcs = True
                break
        if not file_utils.is_empty(self.draped_alb_texture) and any_draped_dcs:
            draped_mat = mat.copy()
            draped_mat.name = self.name + "_draped"
            draped_mat.use_nodes = True
            xp_draped_mat = draped_mat.xp_materials
            xp_draped_mat.alb_texture = self.draped_alb_texture
            xp_draped_mat.normal_texture = self.draped_nml_texture
            xp_draped_mat.lit_texture = self.draped_lit_texture
            xp_draped_mat.draped = True
            xp_draped_mat.draped_nml_tile_rat = self.draped_nml_tile_rat
            draped_mat.name = self.name + "_draped"

            all_mats.append(draped_mat)

        #Now that we have materials, we need to dedupe them with other materials in the scene. Now, you're probably asking, WHY are we not checking this BEFORE we created the materials? This is SO slow!
        #The reason is, materials aren't *just* data, they are code. They resolve file paths, and who knows what other logic they may have, so, rather than duplicate that logic elsewhere and make it harder to maintain, we just create the material, compare, then if needed, delete after.
        new_mats = []
        for our_mat in all_mats:
            material_config.update_settings(our_mat)
            new_mat = None
            for other_mat in bpy.data.materials:
                if material_config.materials_are_equivalent(our_mat, other_mat) and other_mat != our_mat:
                    new_mat = other_mat
                    break
            #If we end up using our material, we'll update the nodes. Otherwise we swap our material for the existing
            if new_mat is None:
                new_mats.append(our_mat)
                material_config.update_nodes(our_mat)
            else:
                new_mats.append(new_mat)
                bpy.data.materials.remove(our_mat)

        #For the basic draw calls just add 'em to the scene
        all_objs = []
        for dc in self.draw_calls:
            all_objs.append(dc.add_to_scene(self.verticies, self.indicies, new_mats, None))

        #Link all the object to the view layer
        for obj in all_objs:
            target_collection.objects.link(obj)
        
        #Join all objects into one
        joined_obj = geometery_utils.join_objects(all_objs, self.name)
        joined_obj.xp_attached_obj.exportable = False
        joined_obj.xp_agp.exportable = False
        joined_obj.xp_fac_mesh.exportable = False
        joined_obj['xp_ext_preview_object'] = True
        joined_obj['xp_ext_preview_filepath'] = self.filepath
            
        #Link to the collection and set parent
        if not make_real:
            joined_obj.parent = target_parent
            joined_obj.hide_select = True
        else:
            joined_obj.matrix_world = target_parent.matrix_world.copy()  #Copy the location/rotation/scale of the parent, but don't parent it, so it can be edited independently
            joined_obj.parent = None
            joined_obj.hide_select = False

def _get_existing_instance(in_path : str):
    for obj in bpy.data.objects:
        if 'xp_ext_preview_filepath' in obj and obj['xp_ext_preview_filepath'] == in_path:
            return obj
    return None

def process_single_object(obj : bpy.types.Object, make_real):
    if obj.type != 'EMPTY':
        return

    for child in obj.children:
        if 'xp_ext_preview_filepath' in child:
            bpy.data.objects.remove(child, do_unlink=True)
    resource = ""
    is_relative = False
    if not file_utils.is_empty(obj.xp_attached_obj.attached_obj_preview_resource):
        if obj.xp_attached_obj.attached_obj_preview_resource.startswith("//"):
            is_relative = True
        resource = file_utils.to_absolute(obj.xp_attached_obj.attached_obj_preview_resource)
    elif not file_utils.is_empty(obj.xp_agp.attached_obj_resource) and obj.xp_agp.exportable and obj.xp_agp.type == 'ATTACHED_OBJ':
        if obj.xp_agp.attached_obj_resource.startswith("//"):
            is_relative = True
        resource = file_utils.to_absolute(obj.xp_agp.attached_obj_resource)
    elif not file_utils.is_empty(obj.xp_attached_obj.resource) and obj.xp_attached_obj.exportable:
        if obj.xp_attached_obj.resource.startswith("//"):
            is_relative = True
        resource = file_utils.to_absolute(obj.xp_attached_obj.resource)
    else:
        return

    #Skip empty. Warn on missing
    if resource == "" or resource == "//" or not is_relative:
        return
    if not os.path.isfile(resource):
        log_utils.warning(f"Attached object preview resource '{resource}' not found.")
        return

    parent_collection = None

    #Find the parent collection
    for col in obj.users_collection:
        parent_collection = col
        break

    existing_inst = _get_existing_instance(file_utils.to_relative(resource).replace("\\", "/"))

    if existing_inst is not None:
        #Create a new object based on the existing instance, set hide_select, and parent it
        new_obj = bpy.data.objects.new(name=f"{obj.name}_preview", object_data=existing_inst.data)
        new_obj.hide_select = True
        new_obj.parent = obj
        new_obj.xp_fac_mesh.exportable = False
        if parent_collection is not None:
            parent_collection.objects.link(new_obj)
        new_obj['xp_ext_preview_filepath'] = file_utils.to_relative(resource).replace("\\", "/")
    if existing_inst is None:
        #Read and add
        new_obj = attached_object_preview()
        new_obj.read(resource)
        new_obj.to_scene(obj, parent_collection, make_real)


@persistent
def clear_existing_objects(in_file_path, in_startup_file_path):
    global existing_objects
    existing_objects = set(obj.session_uid for obj in bpy.data.objects)

@persistent
def update_attached_obj_previews(scene, depsgraph):
    global existing_objects
    global currently_processing
    #Short circuit check, if the size of the objects is the same we can just exit
    if len(bpy.data.objects) == len(existing_objects):
        return

    # Get current objects and diffs
    current_objects = set(obj.session_uid for obj in bpy.data.objects)
    removed_objects = existing_objects - current_objects
    added_objects = current_objects - existing_objects

    # If there were removed objects, we need to check *every* object to look for orphaned attached object previews
    if len(removed_objects) > 0:
        for obj in bpy.data.objects:
            if 'xp_ext_preview_object' in obj:
                if obj.parent == None:
                    existing_objects.discard(obj.session_uid)
                    bpy.data.objects.remove(obj)

    # Store the currently selected and active objects as creating preview objects will shift this around
    selected_objects = bpy.context.selected_objects
    original_active_object = bpy.context.active_object
    # If we have added objects, we need to check every new object to try to set it's previeww object
    if len(added_objects) > 0:
        current_objects_to_bpy = {obj.session_uid: obj for obj in bpy.data.objects}
        for uid in added_objects:
            
            obj = current_objects_to_bpy[uid]
            if obj.session_uid in currently_processing:
                continue
            currently_processing.add(obj.session_uid)
            process_single_object(obj, False)
            currently_processing.remove(obj.session_uid)

    #Re-select the original active object
    for obj in selected_objects:
        obj.select_set(True)
    if original_active_object is not None:
        bpy.context.view_layer.objects.active = original_active_object

    existing_objects = current_objects - removed_objects