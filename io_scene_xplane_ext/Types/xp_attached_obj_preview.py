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

#Lights don't actually use LODs, but if there are LOD buckets, XP2B requires them to be in *one*. But if there's no LOD buckets they can't be in *any*. So we have a single global variable to set what bucket ot put them in
obj_does_use_lods = False

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

    def read(self, in_obj_path):

        log_utils.new_section(f"Read attached .obj {in_obj_path}")

        self.name = os.path.basename(in_obj_path)

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
            print(f"Obj path: {os.path.dirname(in_obj_path)}")
            print(f"Joined path: {os.path.join(os.path.dirname(in_obj_path), texture_name)}")
            print(f"Abs path: {abs_path}")
            return file_utils.to_relative(abs_path)
        
        self.alb_texture = resolve_texture_path(self.alb_texture)
        self.nml_texture = resolve_texture_path(self.nml_texture)
        self.lit_texture = resolve_texture_path(self.lit_texture)
        self.mat_texture = resolve_texture_path(self.mat_texture)
        self.draped_alb_texture = resolve_texture_path(self.draped_alb_texture)
        self.draped_nml_texture = resolve_texture_path(self.draped_nml_texture)
        self.draped_lit_texture = resolve_texture_path(self.draped_lit_texture)
            
    def to_scene(self, target_parent, target_collection):
        log_utils.new_section(f"Creating attached .obj object {self.name}")

        #Create the base material
        all_mats = []
        mat = bpy.data.materials.new(name=self.name)
        mat.use_nodes = True
        xp_mat = mat.xp_materials
        xp_mat.alb_texture = self.alb_texture
        xp_mat.normal_texture = self.nml_texture
        if self.mat_texture != "":
            xp_mat.material_texture = self.mat_texture
            xp_mat.do_separate_material_texture = True
        xp_mat.lit_texture = self.lit_texture

        mat.name = self.name

        all_mats.append(mat)

        material_config.update_nodes(mat)

        #Create the draped material if it exists
        if self.draped_alb_texture != "":
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

            material_config.update_nodes(draped_mat)

        #For the basic draw calls just add 'em to the scene
        all_objs = []
        for dc in self.draw_calls:
            all_objs.append(dc.add_to_scene(self.verticies, self.indicies, all_mats, None))

        #Link all the object to the view layer
        for obj in all_objs:
            target_collection.objects.link(obj)
        
        #Join all objects into one
        joined_obj = geometery_utils.join_objects(all_objs, self.name)
        joined_obj.xp_attached_obj.exportable = False
        joined_obj.xp_agp.exportable = False
        joined_obj.xp_fac_mesh.exportable = False
            
        #Link to the collection and set parent
        joined_obj.parent = target_parent
        joined_obj.hide_select = True