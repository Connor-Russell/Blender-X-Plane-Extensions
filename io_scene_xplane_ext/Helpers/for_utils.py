#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      5/8/2025
#Module:    pol_utils.py
#Purpose:   Provide utility functions for working with polygons in Blender

import bpy

from ..Helpers import misc_utils
from ..Helpers import geometery_utils

class TreeQuad():
    def __init__(self):
        self.left_x = 0.0
        self.bottom_y = 0.0
        self.width = 0.0
        self.height = 0.0
        self.offset_to_center = 0.0
        self.height_meters = 0.0

def is_forest_quad_obj(obj : bpy.types.Object) -> bool:
    """
    Get the lowest and highest U and V values from an object in Blender.

    Args:
        obj (bpy.types.Object): The Blender object to analyze.

    Returns:
        list: A list containing [min_u, max_u, min_v, max_v].

    Raises:
        ValueError: If the object does not have exactly 4 vertices or UVs are missing.
    """
    if obj.type != 'MESH':
        return False

    if len(obj.data.vertices) != 4:
        return False
    
    if len(obj.data.polygons) != 1:
        return False

    uv_layer = misc_utils.get_uv_layer(obj)

    if uv_layer is None:
        return False
    
    #Extract the verticies and UVs
    v0 = obj.data.vertices[obj.data.polygons[0].vertices[0]].co
    v1 = obj.data.vertices[obj.data.polygons[0].vertices[1]].co
    v2 = obj.data.vertices[obj.data.polygons[0].vertices[2]].co
    v3 = obj.data.vertices[obj.data.polygons[0].vertices[3]].co

    #Now that we have verticies, we need to apply the *object's* loc/scale. We don't really care about it's rotation
    v0 -= obj.location
    v0 *= obj.scale
    v1 -= obj.location
    v1 *= obj.scale
    v2 -= obj.location
    v2 *= obj.scale
    v3 -= obj.location
    v3 *= obj.scale

    #Now that we have the real verticies, we need to make sure that the face is flat on either the X or Y axis
    is_flat_x = True
    is_flat_y = True
    if abs(v0.x - v1.x) > 0.01 or abs(v0.x - v2.x) > 0.01 or abs(v0.x - v3.x) > 0.01:
        is_flat_x = False
    if abs(v0.y - v1.y) > 0.01 or abs(v0.y - v2.y) > 0.01 or abs(v0.y - v3.y) > 0.01:
        is_flat_y = False

    if not is_flat_x and not is_flat_y:
        return False
    
    return True

def get_forest_quad_from_obj(obj : bpy.types.Object):
    """
    Get the lowest and highest U and V values from an object in Blender.

    Args:
        obj (bpy.types.Object): The Blender object to analyze.

    Returns:
        list: A list containing [min_u, max_u, min_v, max_v].

    Raises:
        ValueError: If the object does not have exactly 4 vertices or UVs are missing.
    """
    if obj.type != 'MESH':
        raise ValueError("Forest quad must be a mesh.")

    if len(obj.data.vertices) != 4:
        raise ValueError("Forest quad must have exactly 4 vertices.")
    
    if len(obj.data.polygons) != 1:
        raise ValueError("Forest quad must have exactly one face")

    uv_layer = misc_utils.get_uv_layer(obj)

    if uv_layer is None:
        raise ValueError("Object is missing UVs.")
    
    #Extract the verticies and UVs
    v0 = obj.data.vertices[obj.data.polygons[0].vertices[0]].co
    uv0 = uv_layer.data[obj.data.polygons[0].loop_indices[0]].uv
    v1 = obj.data.vertices[obj.data.polygons[0].vertices[1]].co
    uv1 = uv_layer.data[obj.data.polygons[0].loop_indices[1]].uv
    v2 = obj.data.vertices[obj.data.polygons[0].vertices[2]].co
    uv2 = uv_layer.data[obj.data.polygons[0].loop_indices[2]].uv
    v3 = obj.data.vertices[obj.data.polygons[0].vertices[3]].co
    uv3 = uv_layer.data[obj.data.polygons[0].loop_indices[3]].uv

    #Now that we have verticies, we need to apply the *object's* loc/scale. We don't really care about it's rotation
    v0 -= obj.location
    v0 *= obj.scale
    v1 -= obj.location
    v1 *= obj.scale
    v2 -= obj.location
    v2 *= obj.scale
    v3 -= obj.location
    v3 *= obj.scale

    #Now that we have the real verticies, we need to make sure that the face is flat on either the X or Y axis
    is_flat_x = True
    is_flat_y = True
    if abs(v0.x - v1.x) > 0.01 or abs(v0.x - v2.x) > 0.01 or abs(v0.x - v3.x) > 0.01:
        is_flat_x = False
    if abs(v0.y - v1.y) > 0.01 or abs(v0.y - v2.y) > 0.01 or abs(v0.y - v3.y) > 0.01:
        is_flat_y = False

    if not is_flat_x and not is_flat_y:
        raise ValueError("Forest quad must be flat on either the x or y axis")
    
    # If you (probably me in a few months actually) are reading this and wondering
    # *why not just get the bounds of the UV's like we do for polygons?*
    # The answer is, forests need an *offset* from left to set their center. Now, we *could* just center it halfway,
    # between out U's, but that's not really correct, we *really* want to treat the parent empty as the center
    # That is why we apply this object's location and scale, so it effectively has no transform,
    # and x (or y) 0 corresponds to where the tree quad should be centered, which allows us to get the offset

    # Get the UV min/max first
    min_u = min(uv0[0], uv1[0], uv2[0], uv3[0])
    max_u = max(uv0[0], uv1[0], uv2[0], uv3[0])
    min_v = min(uv0[1], uv1[1], uv2[1], uv3[1])
    max_v = max(uv0[1], uv1[1], uv2[1], uv3[1])

    #Now get the lateral min/max
    height_min = min(v0.z, v1.z, v2.z, v3.z)
    height_max = max(v0.z, v1.z, v2.z, v3.z)
    lat_min, lat_max = float('inf'), float('-inf')
    if is_flat_x:
        lat_min = min(v0.x, v1.x, v2.x, v3.x)
        lat_max = max(v0.x, v1.x, v2.x, v3.x)
    elif is_flat_y:
        lat_min = min(v0.y, v1.y, v2.y, v3.y)
        lat_max = max(v0.y, v1.y, v2.y, v3.y)

    # This gives us the u offset per meter. 
    uv_x_scale_to_real_scale = (max_u - min_u) / (lat_max - lat_min)

    # We can now take that, multiply by the min x to get the u offset needed to set the center
    center_offset = uv_x_scale_to_real_scale * lat_min

    # At least, we have all the UVs! Last thing is to get the height and store it in the data structure and export, this is self explanatory
    quad = TreeQuad()
    quad.left_x = min_u
    quad.bottom_y = min_v
    quad.width = max_u - min_u
    quad.height = max_v - min_v
    quad.height_meters = height_max - height_min
    quad.offset_to_center = center_offset
    
    return quad

#Generates a plane from a list of LineVertex objects
#Arguments:
#verts: List of LineVertex objects
#Returns: The plane object
def create_obj_from_forest_quad(in_tree_quad : TreeQuad, in_x_to_y_ratio : float):
    #First we need to know the scale of the texture
    tex_height = in_tree_quad.height_meters / in_tree_quad.height
    tex_width = tex_height * in_x_to_y_ratio

    #Positions
    bl_loc_x = -in_tree_quad.offset_to_center * tex_width
    br_loc_x = bl_loc_x + in_tree_quad.width * tex_width
    ul_loc_x = bl_loc_x
    ur_loc_x = br_loc_x

    bl_loc_z = 0
    br_loc_z = 0
    ul_loc_z = in_tree_quad.height_meters
    ur_loc_z = in_tree_quad.height_meters

    #Y is always 0
    loc_y = 0

    #UVs
    bl_uv_x = in_tree_quad.left_x
    br_uv_x = in_tree_quad.left_x + in_tree_quad.width
    ul_uv_x = bl_uv_x
    ur_uv_x = br_uv_x

    bl_uv_y = in_tree_quad.bottom_y
    br_uv_y = in_tree_quad.bottom_y
    ul_uv_y = in_tree_quad.bottom_y + in_tree_quad.height
    ur_uv_y = in_tree_quad.bottom_y + in_tree_quad.height

    #Normals (all the same)
    nx, ny, nz = 0, -1, 0

    #Create xp_vertex instances using the constructor
    bl = geometery_utils.xp_vertex(bl_loc_x, loc_y, bl_loc_z, nx, ny, nz, bl_uv_x, bl_uv_y)
    br = geometery_utils.xp_vertex(br_loc_x, loc_y, br_loc_z, nx, ny, nz, br_uv_x, br_uv_y)
    ur = geometery_utils.xp_vertex(ur_loc_x, loc_y, ur_loc_z, nx, ny, nz, ur_uv_x, ur_uv_y)
    ul = geometery_utils.xp_vertex(ul_loc_x, loc_y, ul_loc_z, nx, ny, nz, ul_uv_x, ul_uv_y)

    return geometery_utils.create_obj_from_draw_call([bl, br, ur, ul], [0, 1, 3, 1, 2, 3], "Quad")
