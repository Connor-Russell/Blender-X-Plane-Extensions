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
    v0 = obj.data.vertices[obj.data.polygons[0].vertices[0]]
    v1 = obj.data.vertices[obj.data.polygons[0].vertices[1]]
    v2 = obj.data.vertices[obj.data.polygons[0].vertices[2]]
    v3 = obj.data.vertices[obj.data.polygons[0].vertices[3]]

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
    v0 = obj.data.vertices[obj.data.polygons[0].vertices[0]]
    uv0 = uv_layer.data[obj.data.polygons[0].loop_indices[0]]
    v1 = obj.data.vertices[obj.data.polygons[0].vertices[1]]
    uv1 = uv_layer.data[obj.data.polygons[0].loop_indices[1]]
    v2 = obj.data.vertices[obj.data.polygons[0].vertices[2]]
    uv2 = uv_layer.data[obj.data.polygons[0].loop_indices[2]]
    v3 = obj.data.vertices[obj.data.polygons[0].vertices[3]]
    uv3 = uv_layer.data[obj.data.polygons[0].loop_indices[3]]

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
    min_u = min(uv0.x, uv1.x, uv2.x, uv3.x)
    max_u = max(uv0.x, uv1.x, uv2.x, uv3.x)
    min_v = min(uv0.y, uv1.y, uv2.y, uv3.y)
    max_v = max(uv0.y, uv1.y, uv2.y, uv3.y)

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
    quad.bottom_x = min_u
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
    bl = geometery_utils.xp_vertex()
    br = geometery_utils.xp_vertex()
    ul = geometery_utils.xp_vertex()
    ur = geometery_utils.xp_vertex()

    #First we need to know the scale of the texture
    tex_height = in_tree_quad.height_meters / in_tree_quad.height
    tex_width = tex_height * in_x_to_y_ratio

    #With this, we can set positions
    bl.loc_x = -in_tree_quad.offset_to_center * tex_width
    ul.loc_x = bl.loc_x
    br.loc_x = bl.loc_x + in_tree_quad.width * tex_width
    ur.loc_x = br.loc_x
    #Height is 0-height meters
    bl.loc_z = 0
    br.loc_z = 0
    ul.loc_z = in_tree_quad.height_meters
    ur.loc_z = in_tree_quad.height_meters
    #Y is alwas 0
    bl.loc_y = 0
    br.loc_y = 0
    ul.loc_y = 0
    ur.loc_y = 0
    #UVs
    bl.uv_x = in_tree_quad.left_x
    ul.uv_x = in_tree_quad.left_x
    br.uv_x = in_tree_quad.left_x + in_tree_quad.width
    ur.uv_x = in_tree_quad.left_x + in_tree_quad.width
    bl.uv_y = in_tree_quad.bottom_y
    br.uv_y = in_tree_quad.bottom_y
    ul.uv_y = in_tree_quad.bottom_y + in_tree_quad.height
    ur.uv_y = in_tree_quad.bottom_y + in_tree_quad.height
    #Normals
    bl.normal_x = 0
    bl.normal_y = 1
    bl.normal_z = 0
    br.normal_x = 0
    br.normal_y = 1
    br.normal_z = 0
    ul.normal_x = 0
    ul.normal_y = 1
    ul.normal_z = 0
    ur.normal_x = 0
    ur.normal_y = 1
    ur.normal_z = 0

    return geometery_utils.create_obj_from_draw_call([bl, br, ur, ul], [0, 1, 3, 1, 2, 3])
