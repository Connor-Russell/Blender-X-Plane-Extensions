#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/23/2025
#Module:    line_utils.py
#Purpose:   Provides functions for working with X-Plane Lines

import bpy # type: ignore
import bmesh # type: ignore

from ..Types import xp_lin # type: ignore
from . import geometery_utils
from . import log_utils

class lin_vertex:
    """
    Simple class to hold the vertex data for a line segment. TODO: Possibly refactor this to use xp_vertex
    """
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.u = 0
        self.v = 0
        self.uv_layer = 0

def get_layer_z(in_object):
     """
     Gets the average Z of the object. This is used to determine the layer height.

    Args:
        in_object (bpy.types.Object): The Blender object to calculate the average Z for.

    Returns:
        float: The average Z coordinate of the object's vertices in world space.
     """
     z_sum = 0
 
     for vert in in_object.data.vertices:
         z_sum += (in_object.matrix_world @ vert.co).z
 
     return z_sum / len(in_object.data.vertices)

def get_layer_from_segment_object(in_object, offset, type):
    """
    Gets the layer from a segment object. This is used to determine the layer height.

    Args:
        in_object (bpy.types.Object): The Blender object to get the layer from.
        offset (float): The offset to apply to the layer. Use the index of this object in a list of objects, sorted off their Z position.
        type (str): The type of layer to get ("SEGMENT", "START", or "END"). Should come from PROP_lin_layer

    Returns:
        float: The layer height.
    """

    #First, make sure this blender object has only 4 vertices
    if len(in_object.data.vertices) != 4:
        raise Exception(f"Error: Object {in_object.name} does not have 4 vertices!")
        return None

    #Attempt to get the uv layer. We look for the first layer. 
    try:
        uv_layer = in_object.data.uv_layers[0]
    except (KeyError, TypeError) as e:
        uv_layer = None

    #If we have no uv layer, we will return None
    if uv_layer is None:
        raise Exception(f"Error: No UV layer found on object {in_object.name}!")
        return None
    
    #Now, we need to find the edge vertices
    verts, indicies = geometery_utils.get_draw_call_from_obj(in_object)

    lowest_x = 1000
    highest_x = -1000
    lowest_y = 1000
    highest_y = -1000

    left_vertex = lin_vertex()
    right_vertex = lin_vertex()
    top_vertex = lin_vertex()
    bottom_vertex = lin_vertex()

    for i, vert in enumerate(verts):
        if vert.loc_x < lowest_x * 1.01:
            lowest_x = vert.loc_x
            left_vertex.x = vert.loc_x
            left_vertex.y = vert.loc_y
            left_vertex.z = vert.loc_z
            left_vertex.u = vert.uv_x
            left_vertex.v = vert.uv_y

        if vert.loc_x > highest_x * 1.01:
            highest_x = vert.loc_x
            right_vertex.x = vert.loc_x
            right_vertex.y = vert.loc_y
            right_vertex.z = vert.loc_z
            right_vertex.u = vert.uv_x
            right_vertex.v = vert.uv_y

        if vert.loc_y < lowest_y * 1.01:
            lowest_y = vert.loc_y
            bottom_vertex.x = vert.loc_x
            bottom_vertex.y = vert.loc_y
            bottom_vertex.z = vert.loc_z
            bottom_vertex.u = vert.uv_x
            bottom_vertex.v = vert.uv_y

        if vert.loc_y > highest_y * 1.01:
            highest_y = vert.loc_y
            top_vertex.x = vert.loc_x
            top_vertex.y = vert.loc_y
            top_vertex.z = vert.loc_z
            top_vertex.u = vert.uv_x
            top_vertex.v = vert.uv_y

    #Now, comes the hard part. We need to find the center coordinate.
    #S = X of UV. T = Y of UV. X = X of object. Y = Y of object.
    #Because we know the X/S of the left and right vertices, we can find a ratio of Xs to Ss
    #With this info, we can then find the S distance of X0 to the left vertex. We then add that to the S of the left to get the center S
    if left_vertex.u == right_vertex.u:
        raise Exception(f"Error: Left and right vertices have the same X texture coordinates! Please check the UVs of {in_object.name}!")
    xs_to_1_s = abs(right_vertex.x - left_vertex.x) / abs(right_vertex.u - left_vertex.u)   #Basically, how wide wide this texture is in meters, in the context of this single layer
    ss_to_x0 = left_vertex.x / xs_to_1_s    #Basically, how much UV space is between the left vertex and the center of the world
    s_at_x0 = left_vertex.u - ss_to_x0  #Basically, we add the UV distance from the left and center of the world to the left, to get the center position

    #At this point we know the left S, the right S, the top T, the bottom T, and the center U.
    #Armed with this info, and the segment type, we can return the text command

    #These are used to go from UV coords (0-1) to texture coords. They don't matter as long as they're consistent. In the future they may be based on the actual texture
    tex_height = 4096
    tex_width = 4096

    if type == "SEGMENT":
        #format: S_OFFSET <layer> <s1> <sm> <s2>
        seg = xp_lin.segment()
        seg.l = left_vertex.u * tex_width
        seg.c = s_at_x0 * tex_width
        seg.r = right_vertex.u * tex_width
        seg.layer = offset
        return seg
    elif type == "START":
        #START_CAP <layer> <s1> <sm> <s2> <t1> <t2>
        cap = xp_lin.cap()
        cap.type = "START"
        cap.l = left_vertex.u * tex_width
        cap.c = s_at_x0 * tex_width
        cap.r = right_vertex.u * tex_width
        cap.bottom = bottom_vertex.v * tex_height
        cap.top = top_vertex.v * tex_height
        cap.layer = offset
        return cap
    else:
        #END_CAP <layer> <s1> <sm> <s2> <t1> <t2>
        cap = xp_lin.cap()
        cap.type = "END"
        cap.l = left_vertex.u * tex_width
        cap.c = s_at_x0 * tex_width
        cap.r = right_vertex.u * tex_width
        cap.bottom = bottom_vertex.v * tex_height
        cap.top = top_vertex.v * tex_height
        cap.layer = offset
        return cap

def get_scale_from_layer(in_object):
    """
    Gets the scale of the *texture* base on the scale of the object and it's UVs. I.e. if this object uses half the texture and is 1m wide, the scale will be 2m.
    Args:
        in_object (bpy.types.Object): The Blender object to get the scale from.
    Returns:
        tuple: (x_scale, y_scale) The scale of the layer in meters.
    """

    #First, make sure this blender object has only 4 vertices
    if len(in_object.data.vertices) != 4:
        raise Exception(f"Error: Object {in_object.name} does not have 4 vertices")
    
    #Next, get the X size in meters of this object
    x_size = in_object.dimensions.x

    #Now, get the UVs of this object. We will assume the UVs are square, so we will get the lowest X and highest X and store them
    lowest_x = 1
    highest_x = 0

    for uv in in_object.data.uv_layers.active.data:
        if uv.uv.x < lowest_x:
            lowest_x = uv.uv.x
        if uv.uv.x > highest_x:
            highest_x = uv.uv.x

    #Now that we have our edge UVs, and X, we can calculate the scale
    uv_width = abs(highest_x - lowest_x)
    actual_width = x_size / uv_width

    #If there is no material, we will assume the texture is square
    if len(in_object.data.materials) == 0:
        return actual_width, actual_width
    
    try:
        #If there is a material, we will get the texture from the material
        mat_texture = in_object.data.materials[0].node_tree.nodes.get("Image Texture")

        #Get the X and Y dimensions
        if mat_texture is None:
            
            #Throw an error if there is no texture
            raise Exception(f"Error: No texture found on object { in_object.name }! Please configure material with my X-Plane Material Plugin!")

            return actual_width, actual_width
        
        x_dim = mat_texture.image.size[0]
        y_dim = mat_texture.image.size[1]

        #Calculate the height based on the ratio
        y_scale = actual_width * (y_dim / x_dim)
    except Exception as e:
        log_utils.warning(f"Error getting texture dimensions for {in_object.name}, assuming square texture: {e}")
        y_scale = actual_width  # If we can't get the texture dimensions, assume it's square
        pass

    return actual_width, y_scale

#Generates a plane from a list of LineVertex objects
#Arguments:
#verts: List of LineVertex objects
#Returns: The plane object
def gen_plane_from_verts(in_verts):
    """
    TODO: Get rid of this function and replace it with geometry_utils.create_obj_from_draw_call
    """
    xs = []
    ys = []
    zs = []
    us = []
    vs = []

    for vert in in_verts:
        xs.append(vert.x)
        ys.append(vert.y)
        zs.append(vert.z)
        us.append(vert.u)
        vs.append(vert.v)

    #Create a new bmesh
    bm = bmesh.new()

    verts = [bm.verts.new([x, y, z]) for x, y, z in zip(xs, ys, zs)]
    face = bm.faces.new(verts)

    # Create a UV layer
    uv_layer = bm.loops.layers.uv.verify()

    # Assign UV coordinates to each vertex of the face
    for loop, u, v in zip(face.loops, us, vs):
        loop[uv_layer].uv = (u, v)

    # Finish up, write the bmesh into a new mesh
    mesh = bpy.data.meshes.new("Plane")
    bm.to_mesh(mesh)
    bm.free()

    # Create an object with that mesh
    obj = bpy.data.objects.new("Plane", mesh)
    return obj
