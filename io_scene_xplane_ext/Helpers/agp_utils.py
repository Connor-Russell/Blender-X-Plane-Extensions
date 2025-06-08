#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      6/3/2025
#Module:    Agp Utils
#Purpose:   Provide functions to help with generating autogen points

import bpy
import mathutils
from . import geometery_utils
from . import log_utils

class agp_transform:
    """
    Contains the transform data for the agp tile
    """

    def __init__(self):
        self.x_ratio = 1.0
        self.y_ratio = 1.0
        self.anchor_x = 0.0
        self.anchor_y = 0.0

def build_vertex_to_edge_map(obj):
    """
    Build a lookup table mapping each vertex index to a list of edge indices it is part of.

    Args:
        obj (bpy.types.Object): The Blender object (must be a mesh).

    Returns:
        dict: A dictionary mapping vertex indices to lists of edge indices.
    """
    from collections import defaultdict

    mesh = obj.data
    vertex_to_edges = defaultdict(list)
    for edge in mesh.edges:
        for v in edge.vertices:
            vertex_to_edges[v].append(edge.index)
    return dict(vertex_to_edges)

def get_edges_for_vertex(obj, vertex_index, vertex_to_edges):
    """
    Retrieve a list of edge objects attached to a given vertex index, using a provided lookup table.

    Args:
        obj (bpy.types.Object): The Blender object (must be a mesh).
        vertex_index (int): The index of the vertex.
        vertex_to_edges (dict): A dictionary mapping vertex indices to lists of edge indices.

    Returns:
        list: A list of bpy.types.MeshEdge objects attached to the vertex.
    """
    mesh = obj.data
    edge_indices = vertex_to_edges.get(vertex_index, [])
    return [mesh.edges[i] for i in edge_indices]

def get_perimeter_from_mesh(obj):
    vert_to_edge = build_vertex_to_edge_map(obj)

    #Get a list of edges that have 1 connected edge
    end_vertex = []
    start_vertex = 0

    parent_scale = mathutils.Vector((1, 1, 1))

    if obj.parent is not None:
        parent_scale = obj.parent.scale

    for v in vert_to_edge:
        edges = get_edges_for_vertex(obj, v, vert_to_edge)
        if len(edges) == 1:
            end_vertex.append(v)

    #If there are no end vertices, this is a closed loop, so we'll just find the vertex with the lowest Z and lowest Y
    if len(end_vertex) == 0:
        all_verts = [v for v in obj.data.vertices]

        #Sort by Z then Y
        all_verts.sort(key=lambda v: (v.co.z, v.co.y))

        start_vertex = all_verts[0].index

    def remove_non_flat_edges(obj, edges):
        new_edges = []
        for edge in edges:
            #Get the verts
            v1 = obj.data.vertices[edge.vertices[0]]
            v2 = obj.data.vertices[edge.vertices[1]]

            if abs(v1.co.z - v2.co.z) < 0.001:
                new_edges.append(edge)
        return new_edges
    
    def remove_self_edge(edges, self_edge):
        new_edges = []
        for edge in edges:
            if edge.vertices != self_edge.vertices:
                new_edges.append(edge)
        return new_edges
    
    def get_next_edge_vertex(cur_edge, prior_vertex):
        if cur_edge.vertices[0] == prior_vertex:
            return cur_edge.vertices[1]
        else:
            return cur_edge.vertices[0]

    #Now that we have a starting point, we need to find the starting edge
    all_starting_edges = get_edges_for_vertex(obj, start_vertex, vert_to_edge)
    all_starting_edges = remove_non_flat_edges(obj, all_starting_edges)

    if len(all_starting_edges) == 0:
        raise ValueError("No valid starting edges found. Ensure the mesh has flat edges.")

    #We'll use the first edge
    #These are vertex *indicies*
    out_verts = []
    cur_start_vertex = start_vertex
    cur_edge = all_starting_edges[0]

    while True:
        #Save the current start vertex
        out_verts.append(cur_start_vertex)

        #Get the next vertex
        next_vertex = get_next_edge_vertex(cur_edge, cur_start_vertex)

        #Get the next edges, and remove the current and non-flat edges
        next_edges = get_edges_for_vertex(obj, next_vertex, vert_to_edge)
        print(f"Edges for vertex {len(next_edges)}")
        next_edges = remove_non_flat_edges(obj, next_edges)
        print(f"Edges minus vertical edges {len(next_edges)}")
        next_edges = remove_self_edge(next_edges, cur_edge)
        print(f"Edges minus self {len(next_edges)}")

        #If there are no edges, we've reached an open end, save the last vertex and break
        if len(next_edges) == 0:
            out_verts.append(next_vertex)
            break

        #If there is only one edge, we need to check that the next vertex is not the same as our very first vertex
        #If it's not, we can continue
        #If it is, it's a close loop and we can just break here
        if len(next_edges) == 1:
            if next_vertex == start_vertex:
                break
            else:
                cur_edge = next_edges[0]
                cur_start_vertex = next_vertex
        
        #If there are multiple edges, that is invalid. So we will raise an error
        if len(next_edges) > 1:
            raise ValueError(f"Multiple edges found for vertex at location {obj.data.vertices[next_vertex].co}. Ensure the mesh is a simple polygon.")
        
    #Now we have a list of vertex indicies! So now we get to go through the actual vertices, and get their coords.
    out_coords = []

    for v in out_verts:
        new_pos = obj.data.vertices[v].co
        new_pos.z = 0.0  # Set Z to 0 for flatness
        out_coords.append(new_pos)

    #Now we will iterate over our list of coords and apply the rot/loc/scale of *this* object, but not the parents, to it
    out_coords = [(obj.matrix_local @ coord) * parent_scale for coord in out_coords]

    #Return the coords
    return out_coords

def to_pixel_coords(x, y, transform: agp_transform):
    """
    Converts the Blender X/Y coordinates relative to a tile to pixel coordinate.
    This is more complex than simply multiplying by the ratio, because the pixel coords are relative to 0/0, but the Blender coords are relative to their parent (the tile, whose origin is the anchor pt)
    Args:
        x (float): The X coordinate in Blender space.
        y (float): The Y coordinate in Blender space.
        transform (agp_transform): The transform object containing the ratios and anchors.
    Returns:
        tuple: A tuple containing the pixel X and Y coordinates.
    """
    #return x, y
    # Calculate the pixel coordinates
    pixel_x = x * transform.x_ratio + transform.anchor_x
    pixel_y = y * transform.y_ratio + transform.anchor_y

    return pixel_x, pixel_y

def to_blender_coords(pixel_x, pixel_y, transform: agp_transform):
    """
    Converts pixel coordinates to Blender X/Y coordinates relative to a tile.
    This is the inverse of the to_pixel_coords function.
    Args:
        pixel_x (float): The X coordinate in pixel space.
        pixel_y (float): The Y coordinate in pixel space.
        transform (agp_transform): The transform object containing the ratios and anchors.
    Returns:
        tuple: A tuple containing the Blender X and Y coordinates.
    """
    # Calculate the Blender coordinates
    blender_x = (pixel_x - transform.anchor_x) / transform.x_ratio
    blender_y = (pixel_y - transform.anchor_y) / transform.y_ratio

    return blender_x, blender_y

def get_tile_bounds_and_transform(obj):
    """
    Returns a tuple of left, bottom, right, top, UVs for the bounding box of the object, and the bounding box, and an agp_transform for this tile

    """

    left_vertex = None
    right_vertex = None
    top_vertex = None
    bottom_vertex = None

    left_u = 0
    right_u = 1
    top_v = 1
    bottom_v = 0

    for v in obj.data.vertices:
        if left_vertex is None or v.co.x < left_vertex.co.x:
            left_vertex = v
        if right_vertex is None or v.co.x > right_vertex.co.x:
            right_vertex = v
        if top_vertex is None or v.co.y > top_vertex.co.y:
            top_vertex = v
        if bottom_vertex is None or v.co.y < bottom_vertex.co.y:
            bottom_vertex = v

    left_vertex_pos = obj.scale * left_vertex.co
    right_vertex_pos = obj.scale * right_vertex.co
    top_vertex_pos = obj.scale * top_vertex.co
    bottom_vertex_pos = obj.scale * bottom_vertex.co

    #Get the UVs for these vertices
    uv_layer = obj.data.uv_layers.active.data
    if uv_layer is None:
        log_utils.error(f"No UV layer on BASE_TILE object! {obj.name}")
        return None
    
    left_u = uv_layer[left_vertex.index].uv.x
    right_u = uv_layer[right_vertex.index].uv.x
    top_v = uv_layer[top_vertex.index].uv.y
    bottom_v = uv_layer[bottom_vertex.index].uv.y

    #Calculate the ratios. We always use 4096 as our pixel size
    x_ratio = ((right_u - left_u) / (right_vertex_pos.x - left_vertex_pos.x)) * 4096
    y_ratio = ((top_v - bottom_v) / (top_vertex_pos.y - bottom_vertex_pos.y)) * 4096

    #Now that we have the ratios, and the left/bottom coords, we can get the anchor
    # To do so, we will multiply the negative left position and negative bottom postion by the ratios,
    # then add them to the left and bottom UVs to get the anchor UVs
    anchor_u = left_u + (-left_vertex_pos.x * x_ratio)
    anchor_v = bottom_v + (-bottom_vertex_pos.y * y_ratio)

    transform = agp_transform()
    transform.x_ratio = x_ratio
    transform.y_ratio = y_ratio
    transform.anchor_x = anchor_u
    transform.anchor_y = anchor_v

    #Return the UV bounds
    return left_u, bottom_v, right_u, top_v, transform

def create_obj_from_perimeter(perimeter, extrude_height=0.0):
    """
    Creates a new object from the given perimeter points.
    """

    verts = []
    indicies = []

    for i, pt in enumerate(perimeter):
        if i == len(perimeter) - 1:
            return
        cur_vert = geometery_utils.xp_vertex(pt.x, pt.y, pt.z, 0, 0, 1, 0, 0) 
        next_vert = geometery_utils.xp_vertex(perimeter[i + 1].x, perimeter[i + 1].y, perimeter[i + 1].z, 0, 0, 1, 0, 0)
        top_cur_vert = geometery_utils.xp_vertex(pt.x, pt.y, pt.z + extrude_height, 0, 0, 1, 0, 0)
        top_next_vert = geometery_utils.xp_vertex(perimeter[i + 1].x, perimeter[i + 1].y, perimeter[i + 1].z + extrude_height, 0, 0, 1, 0, 0)

        verts.append(cur_vert)
        verts.append(next_vert)
        verts.append(top_cur_vert)

        verts.append(next_vert)
        verts.append(top_next_vert)
        verts.append(top_cur_vert)
    
    for i in range(0, len(verts)):
        indicies.append(i)

    new_obj = geometery_utils.create_obj_from_draw_call(verts, indicies, "Perimeter Obj")

    #Remove doubles from the new object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = new_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None

    return new_obj
