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
from ..Helpers import collection_utils
from typing import List
from .xp_obj import draw_call
from bpy.app.handlers import persistent # type: ignore

existing_meshes : dict[str, bpy.types.Mesh] = {}

def _copy_prop_group(target, source):
    for prop in source.bl_rna.properties:
        if not prop.is_readonly:
            setattr(target, prop.identifier, getattr(source, prop.identifier))

def is_attached_object(in_obj : bpy.types.Object):
    """
    Returns true if this is an attached object, defined by the appropriate properties set, the dictionary key set if it's a mesh (additional safegaurd if you set the wrong properties on a mesh) and is the right type (mesh or empty)
    """
    if not ((in_obj.xp_agp.exportable and in_obj.xp_agp.type == "ATTACHED_OBJ") or (in_obj.xp_attached_obj.exportable)):
        return False
    if (in_obj.type == "MESH" and not "xp_ext_preview_filepath" in in_obj):
        return False
    return in_obj.type == "MESH" or in_obj.type == "EMPTY"

def get_effective_preview_resource(obj : bpy.types.Object) -> str:
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
        resource = ""

    #Skip empty
    if resource == "" or resource == "//" or not is_relative:
        resource = ""

    resource = file_utils.to_relative(resource).replace("\\", "/")

    return resource

class _attached_object_preview:
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

        self.filepath = ""

    def read(self, in_obj_path):

        log_utils.new_section(f"Read attached .obj {in_obj_path}")

        self.name = os.path.basename(in_obj_path)
        self.filepath = in_obj_path

        trans_matrix = [1, -1, 1]

        cur_start_lod = 0

        with open(file_utils.to_absolute(in_obj_path), "r") as f:
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

            elif tokens[0] == "TRIS":
                #Draw call. Start index and length
                dc = draw_call()
                dc.start_index = int(float(tokens[1]))
                dc.length = int(float(tokens[2]))

                if cur_start_lod == 0:
                    self.draw_calls.append(dc)

            elif tokens[0] == "TEXTURE" and len(tokens) >= 2:
                self.alb_texture = tokens[1]
            
            elif tokens[0] == "TEXTURE_MAP":
                if tokens[1].lower() == "normal":
                    self.nml_texture = tokens[2]
                elif tokens[1].lower() == "material_gloss":
                    self.mat_texture = tokens[2]

            elif tokens[0] == "TEXTURE_NORMAL":
                self.nml_texture = tokens[1]

            elif tokens[0] == "TEXTURE_LIT":
                self.lit_texture = tokens[1]

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
            
    def to_mesh(self) -> bpy.types.Mesh:
        log_utils.new_section(f"Creating attached .obj mesh {self.name}")

        #Create the base material
        mat = bpy.data.materials.new(name=f"~PREVIEW~{self.name}")
        mat.use_nodes = True
        xp_mat = mat.xp_materials
        xp_mat.alb_texture = self.alb_texture
        xp_mat.normal_texture = self.nml_texture
        if not file_utils.is_empty(self.mat_texture):
            xp_mat.material_texture = self.mat_texture
            xp_mat.do_separate_material_texture = True
        xp_mat.lit_texture = self.lit_texture

        #Now that we have materials, we need to dedupe them with other materials in the scene. Now, you're probably asking, WHY are we not checking this BEFORE we created the materials? This is SO slow!
        #The reason is, materials aren't *just* data, they are code. They resolve file paths, and who knows what other logic they may have, so, rather than duplicate that logic elsewhere and make it harder to maintain, we just create the material, compare, then if needed, delete after.
        material_config.update_settings(mat)
        existing_mat = None
        for other_mat in bpy.data.materials:
            if material_config.materials_are_equivalent(mat, other_mat) and other_mat != mat:
                existing_mat = other_mat
                break
        if existing_mat is None:
            material_config.update_nodes(mat)
        else:
            bpy.data.materials.remove(mat)
            mat = existing_mat

        vertices = []
        faces = []
        loop_uvs = []
        loop_normals = []

        for dc in self.draw_calls:
            if dc.is_lod_duplicate:
                log_utils.info(f"Skipping draw call {dc.start_index}-{dc.length} because it is a duplicate of another draw call in a different LOD bucket")
                continue

            draw_call_indices = self.indicies[dc.start_index:dc.start_index + dc.length]
            draw_call_vertices = [self.verticies[index] for index in draw_call_indices]
            draw_call_indices = list(range(len(draw_call_vertices)))
            draw_call_indices.reverse()

            vertex_offset = len(vertices)
            vertices.extend(
                (vertex.loc_x, vertex.loc_y, vertex.loc_z)
                for vertex in draw_call_vertices
            )

            for index in range(0, len(draw_call_indices) - 2, 3):
                triangle_indices = draw_call_indices[index:index + 3]
                faces.append(tuple(vertex_offset + vertex_index for vertex_index in triangle_indices))
                for vertex_index in triangle_indices:
                    vertex = draw_call_vertices[vertex_index]
                    loop_uvs.append((vertex.uv_x, vertex.uv_y))
                    loop_normals.append(
                        mathutils.Vector((vertex.normal_x, vertex.normal_y, vertex.normal_z)).normalized()
                    )

        mesh = bpy.data.meshes.new(self.name)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        mesh.materials.append(mat)

        uv_layer = mesh.uv_layers.new(name="UVMap")
        uv_index = 0
        for polygon in mesh.polygons:
            polygon.use_smooth = True
            for loop_index in polygon.loop_indices:
                uv_layer.data[loop_index].uv = loop_uvs[uv_index]
                uv_index += 1

        if loop_normals:
            mesh.normals_split_custom_set(loop_normals)
            if bpy.app.version < (4, 1, 0):
                mesh.use_auto_smooth = True

        return mesh

def update_preview_for_single_obj(in_obj : bpy.types.Object):
    """
    Processes a single object, updating it's preview based on the resource. Returns 0 for success, 1 for success but this object should be deleted, failures are raised as exception. Logic is as follows:
	
	- If this object has children, fail with message
    - Get the resource and resolve it to an absolute path. Resource must be relative to the blend file. We first check the dedicated preview resource. If it is empty, we check the agp attached object resource IF this is an agp attached object and exportable. Then, we check the facade attached object resource IF it is exportable
    - If we are an empty, we had no preview:
        - If preview resource is empty:
			- Set this object's xp_ext_preview_filepath to ""
			- Return 0
        - If preview resource is valid:
            - lookup this resource in our mesh cache. If it is not there, lookup this mesh in the entire scene
			- If mesh is none:
				- Load the mesh with attached_object_preview.read and .to_mesh, and store it in the cache
			- If we got a mesh:
				- Create new mesh object, set the transform and parent to the same as this empty, set the name to the filename + Preview
				- Set this object's xp_ext_preview_filepath to the *real* path, what is returned by get_effective_preview_resource
				- Return 1
			- Else:
				- Raise exception
    - If we are a mesh, we already had a preview:
        - If preview resource is empty:
			- If this object has children, fail with message
			- Add a new empty with the same transform/parent, and set the name to filename + Preview (if there's a filename that isn't used here), or AGP Attached Object if AGP object, or FAC Attached Object if exportable fac attached object, or Unassigned Attached Object
			- Return 1
		- If preview resource is valid and different:
            - lookup this resource in our mesh cache. If it is not there, lookup this mesh in the entire scene
            - If mesh is none:
				- Load the mesh with attached_object_preview.read and .to_mesh, and store it in the cache
			- If we got a mesh:
				- Create new mesh object, set the transform and parent to the same as this empty, set the name to the filename + Preview
				- Set this object's xp_ext_preview_filepath to the *real* path, what is returned by get_effective_preview_resource
				- Return 0
			- Else:
				- Raise exception
        - If preview resource is valid and same:
            - Return 0
    """
    global existing_meshes

    if len(in_obj.children) > 0:
        raise Exception(f"Attached object must not have children! Obj is {in_obj.name}.")

    # First get the resource
    resource = get_effective_preview_resource(in_obj)
    print(f"Resource {resource}")
    print(f"Type {in_obj.type}")

    # Now we need to check what state the current objetc is 
    if in_obj.type == 'EMPTY':
        # If this is already an empty (aka no preview) and no preview resource is found, do nothing
        if resource == "" or not os.path.exists(file_utils.to_absolute(resource)):
            print(f"Resource {resource}")
            in_obj["xp_ext_preview_filepath"] = ""
            return 0

        #Valid preview resource! If this is not make_real, try to load from cache
        our_mesh = None
        our_mesh = existing_meshes.get(resource, None)

        # If we got a mesh from the cache we need to make sure it's still valid. If not, remove it from the cache
        if our_mesh != None:
            try:
                test_valid = our_mesh.name
            except:
                our_mesh = None
                existing_meshes.pop(resource, None)

        # If we still don't have a mesh we will search all existing objects. Heavy, but still faster than loading, and this will only happen once for each new object per session. And once we implement an on-load cache builder, this will only happen once per new object
        if our_mesh == None:
            for obj in bpy.data.objects:
                if "xp_ext_preview_filepath" in obj and obj["xp_ext_preview_filepath"] == resource:
                    # Update the cache path and set our_mesh
                    existing_meshes[resource] = obj.data
                    our_mesh = obj.data

        # If we STILL don't have a mesh, we need to load it
        if our_mesh == None:
            try:
                obj_loader = _attached_object_preview()
                obj_loader.read(file_utils.to_absolute(resource))
                our_mesh = obj_loader.to_mesh()
            except Exception as e:
                raise Exception(f"Failed to load attached object \"{resource}\". Obj is {in_obj.name}. Error is: {e}") from e

        # Final safety check
        if our_mesh == None:
            raise Exception(f"Failed to load attached object \"{resource}\", no mesh data was returned. Obj is {in_obj.name}.. Perhaps the .obj has no mesh data?") from e

        print(f"Got our mesh {our_mesh}")

        # Create a new object, sync the transform, parent, and the collection
        new_obj : bpy.types.Object = bpy.data.objects.new(f"{resource.split('/')[-1].split('.')[0]} Preview", our_mesh)
        print(f"Made object {new_obj.name}")
        new_obj["xp_ext_preview_filepath"] = resource
        new_obj.parent = in_obj.parent
        new_obj.matrix_parent_inverse = in_obj.matrix_parent_inverse.copy()
        new_obj.matrix_basis = in_obj.matrix_basis.copy()
        _copy_prop_group(new_obj.xp_attached_obj, in_obj.xp_attached_obj)
        _copy_prop_group(new_obj.xp_agp, in_obj.xp_agp)
        for col in in_obj.users_collection:
            print(f"Linking obj to col {col}")
            col.objects.link(new_obj)
        if in_obj.select_get():
            new_obj.select_set(True)
        if bpy.context.active_object == in_obj:
            bpy.context.view_layer.objects.active = new_obj

        if in_obj.select_get():
            new_obj.select_set(True)
        if bpy.context.active_object == in_obj:
            bpy.context.view_layer.objects.active = new_obj

        #Make this objetc not exportable as a mesh
        new_obj.xp_lin.exportable = False
        new_obj.xp_for.exportable = False
        new_obj.xp_fac_mesh.exportable = False

        # Tell the caller we succeeded but delete the old object
        return 1
            
        # If we DID get a resouce now we need to load it
    elif in_obj.type == 'MESH':
        if not is_attached_object(in_obj):
            raise Exception(f"Tried to call update_preview_for_single_obj on obj {in_obj.name} but it is not an attached object!")
        
        # If this is empty, we need to create an empty here
        if resource == "" or not os.path.exists(file_utils.to_absolute(resource)):
            # Create the new empty that matches our mesh data
            new_obj_name = ""
            if resource != "" and resource != "//":
                new_obj_name = f"{resource.split('/')[-1].split('.')[0]} Preview"
            elif in_obj.xp_agp.exportable and in_obj.xp_agp.type == "ATTACHED_OBJ":
                new_obj_name = "Unassigned .agp Attached Object"
            elif in_obj.xp_attached_obj.exportable:
                new_obj_name = "Unassigned .fac Attached Object"
            else:
                #Theoretically should never be called
                new_obj_name = "Unassigned Attached Object"
                raise Exception(f"Just called update_preview for object that is not exportable for facades or agps! Obj is {in_obj.name}")

            new_obj = bpy.data.objects.new(new_obj_name, None)
            new_obj.empty_display_type = "ARROWS"
            new_obj.parent = in_obj.parent
            new_obj.matrix_parent_inverse = in_obj.matrix_parent_inverse.copy()
            new_obj.matrix_basis = in_obj.matrix_basis.copy()
            _copy_prop_group(new_obj.xp_attached_obj, in_obj.xp_attached_obj)
            _copy_prop_group(new_obj.xp_agp, in_obj.xp_agp)
            for col in in_obj.users_collection:
                col.objects.link(new_obj)
            if in_obj.select_get():
                new_obj.select_set(True)
            if bpy.context.active_object == in_obj:
                bpy.context.view_layer.objects.active = new_obj

            #Make this objetc not exportable as a mesh
            new_obj.xp_lin.exportable = False
            new_obj.xp_for.exportable = False
            new_obj.xp_fac_mesh.exportable = False

            # Return 1 so the caller deletes the original mesh
            return 1
        
        #Check for same resource. Since we're already a mesh, if it's the same, there's nothing to do
        if "xp_ext_preview_filepath" in in_obj and resource == in_obj["xp_ext_preview_filepath"]:
            return 0

        # If we got here our resource is valid and different
        our_mesh = None
        our_mesh = existing_meshes.get(resource, None)

        # If we got a mesh from the cache we need to make sure it's still valid. If not, remove it from the cache
        if our_mesh != None:
            try:
                test_valid = our_mesh.name
            except:
                our_mesh = None
                existing_meshes.pop(resource, None)

        # If we still don't have a mesh we will search all existing objects. Heavy, but still faster than loading, and this will only happen once for each new object per session. And once we implement an on-load cache builder, this will only happen once per new object
        if our_mesh == None:
            for obj in bpy.data.objects:
                if "xp_ext_preview_filepath" in obj and obj["xp_ext_preview_filepath"] == resource:
                    # Update the cache path and set our_mesh
                    existing_meshes[resource] = obj.data
                    our_mesh = obj.data

        # If we STILL don't have a mesh, we need to load it
        if our_mesh == None:
            try:
                obj_loader = _attached_object_preview()
                obj_loader.read(resource)
                our_mesh = obj_loader.to_mesh()
            except Exception as e:
                raise Exception(f"Failed to load attached object \"{resource}\". Obj is {in_obj.name}. Error is: {e}") from e

        # Final safety check
        if our_mesh == None:
            raise Exception(f"Failed to load attached object \"{resource}\", no mesh data was returned. Obj is {in_obj.name}. Perhaps the .obj has no mesh data?") from e

        # Create a new object, sync the transform, parent, and the collection
        in_obj.name = f"{resource.split('/')[-1].split('.')[0]} Preview"
        in_obj.data = our_mesh
        in_obj["xp_ext_preview_filepath"] = resource
        
        # Tell the caller we succeeded and to keep this object
        return 0

    raise Exception("Unsupported object type")  

def clear_preview_for_single_obj(in_obj : bpy.types.Object):
    """
    Clears the preview for a single object. If the object was a mesh, it reverts it back to an empty. Returns 0 on success, 1 if success but the caller needs to remove this object. Exceptions propagate up
    """

    # First get the resource
    resource = get_effective_preview_resource(in_obj)

    # Now we need to check what state the current objetc is 
    if in_obj.type == 'EMPTY':
        in_obj["xp_ext_preview_filepath"] = ""
        return 0

    elif in_obj.type == 'MESH':
        if not is_attached_object(in_obj):
            raise Exception(f"Tried to call clear_preview_for_single_obj on obj {in_obj.name} but it is not an attached object!")
        # Create the new empty that matches our mesh data
        new_obj_name = ""
        if resource != "" and resource != "//":
            new_obj_name = f"{resource.split('/')[-1].split('.')[0]} Preview"
        elif in_obj.xp_agp.exportable and in_obj.xp_agp.type == "ATTACHED_OBJ":
            new_obj_name = "Unassigned .agp Attached Object"
        elif in_obj.xp_attached_obj.exportable:
            new_obj_name = "Unassigned .fac Attached Object"
        else:
            new_obj_name = "Unassigned Attached Object"

        new_obj = bpy.data.objects.new(new_obj_name, None)
        new_obj.empty_display_type = "ARROWS"
        new_obj.parent = in_obj.parent
        new_obj.matrix_parent_inverse = in_obj.matrix_parent_inverse.copy()
        new_obj.matrix_basis = in_obj.matrix_basis.copy()
        _copy_prop_group(new_obj.xp_attached_obj, in_obj.xp_attached_obj)
        _copy_prop_group(new_obj.xp_agp, in_obj.xp_agp)
        for col in in_obj.users_collection:
            col.objects.link(new_obj)
        if in_obj.select_get():
            new_obj.select_set(True)
        if bpy.context.active_object == in_obj:
            bpy.context.view_layer.objects.active = new_obj

        # Return 1 so the caller deletes the original mesh
        return 1

    raise Exception("Unsupported object type")  

def reload_previews_for_asset(resource: str):
    global existing_meshes
    """
    Clears the cache for a given object, resets each object's resource flag, then reloads them so that they reload the asset and recreate the cache
    """

    log_utils.new_section(f"Reloading previews for {resource}")

    if file_utils.is_empty(resource):
        return

    objs_to_reload : list[bpy.types.Object] = []

    for obj in bpy.data.objects:
        if "xp_ext_preview_filepath" in obj and obj["xp_ext_preview_filepath"] == resource:
            obj["xp_ext_preview_filepath"] = ""
            objs_to_reload.append(obj)

    existing_meshes.pop(resource, None)

    for obj in objs_to_reload:
        result = 2
        try:
            result = update_preview_for_single_obj(obj)

            if result == 1:
                bpy.data.objects.remove(obj, do_unlink=True)
        except Exception as e:
            log_utils.warning(f"Failed to reload object: {e}")

@persistent
def load_existing_mesh_cache_on_file_load(unused, unused2):
    for in_obj in bpy.data.objects:
        if "xp_ext_preview_filepath" in in_obj and in_obj["xp_ext_preview_filepath"] != "" and in_obj["xp_ext_preview_filepath"] != "//":
            # Update the cache path and set our_mesh
            existing_meshes[in_obj["xp_ext_preview_filepath"]] = in_obj.data
