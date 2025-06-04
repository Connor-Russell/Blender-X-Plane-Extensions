#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      6/3/2025
#Module:    Agp Utils
#Purpose:   Provide functions to help with generating autogen points

import bpy
from . import geometery_utils

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

    for v in vert_to_edge:
        edges = get_edges_for_vertex(obj, v, vert_to_edge)
        if len(edges) == 1:
            end_vertex.append(v)

    #If there are no end verticies, this is a closed loop, so we'll just find the vertex with the lowest Z and lowest Y
    if len(end_vertex) == 0:
        all_verts = [v for v in obj.data.vertices]

        #Sort by Z then Y
        all_verts.sort(key=lambda v: (v.co.z, v.co.y))

        start_vertex = all_verts[0].index

    def remove_non_flat_edges(obj, edges):
        new_edges = []
        for edge in edges:
            #Get the verts
            v1 = obj.data.verticies[edge.verticies[0]]
            v2 = obj.data.verticies[edge.verticies[0]]

            if abs(v1.co.z - v2.co.z) < 0.001:
                new_edges.append(edge)
        return new_edges
    
    def remove_self_edge(edges, self_edge):
        new_edges = []
        for edge in edges:
            if edge.verticies != self_edge.verticies:
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
        next_edges = remove_non_flat_edges(obj, next_edges)
        next_edges = remove_self_edge(next_edges, cur_edge)

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
            raise ValueError(f"Multiple edges found for vertex at location {obj.data.verticies[next_vertex].co}. Ensure the mesh is a simple polygon.")
        
    #Now we have a list of vertex indicies! So now we get to go through the actual verticies, and get their coords.
    out_coords = []

    for v in out_verts:
        new_pos = obj.data.vertices[v].co
        new_pos.z = 0.0  # Set Z to 0 for flatness
        out_coords.append(new_pos)

    #Return the coords
    return out_coords

def get_translation_ratios(obj):
    """
    Gets multipliers to convert X/Y blender coordinates to pixel X/Y coordinates for the AGP
    Works by finding the left/right/top/bottom verticies of the mesh, their UVs, then calculating the ratio between position and UV
    Returns tuple of (x_ratio, y_ratio)
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

    #Get the UVs for these vertices
    uv_layer = obj.data.uv_layers.active.data
    if uv_layer is None:
        raise ValueError("No active UV layer found on the object.")
    
    left_u = uv_layer[left_vertex.index].uv.x
    right_u = uv_layer[right_vertex.index].uv.x
    top_v = uv_layer[top_vertex.index].uv.y
    bottom_v = uv_layer[bottom_vertex.index].uv.y

    #Calculate the ratios
    x_ratio = (right_vertex.co.x - left_vertex.co.x) / (right_u - left_u)
    y_ratio = (top_vertex.co.y - bottom_vertex.co.y) / (top_v - bottom_v)

    return x_ratio, y_ratio

def to_pixel_coords(x, y, x_ratio, y_ratio, x_anchor, y_anchor):
    """
    Converts the Blender X/Y coordinates relative to a tile to pixel coordinate.
    This is more complex than simply multiplying by the ratio, because the pixel coords are relative to 0/0, but the Blender coords are relative to their parent (the tile, whose origin is the anchor pt)
    Args:
        x (float): The X coordinate in Blender space.
        y (float): The Y coordinate in Blender space.
        x_ratio (float): The ratio to convert Blender X to pixel X.
        y_ratio (float): The ratio to convert Blender Y to pixel Y.
        x_anchor (float): The X coordinate of the anchor point in UV space.
        y_anchor (float): The Y coordinate of the anchor point in UV space.
    Returns:
        tuple: A tuple containing the pixel X and Y coordinates.
    """
    # Calculate the pixel coordinates
    pixel_x = x * x_ratio + x_anchor
    pixel_y = y * y_ratio + y_anchor

    return pixel_x, pixel_y

def to_blender_coords(pixel_x, pixel_y, x_ratio, y_ratio, x_anchor, y_anchor):
    """
    Converts pixel coordinates to Blender X/Y coordinates relative to a tile.
    This is the inverse of the to_pixel_coords function.
    Args:
        pixel_x (float): The X coordinate in pixel space.
        pixel_y (float): The Y coordinate in pixel space.
        x_ratio (float): The ratio to convert Blender X to pixel X.
        y_ratio (float): The ratio to convert Blender Y to pixel Y.
        x_anchor (float): The X coordinate of the anchor point in UV space.
        y_anchor (float): The Y coordinate of the anchor point in UV space.
    Returns:
        tuple: A tuple containing the Blender X and Y coordinates.
    """
    # Calculate the Blender coordinates
    blender_x = (pixel_x - x_anchor) / x_ratio
    blender_y = (pixel_y - y_anchor) / y_ratio

    return blender_x, blender_y

def get_tile_bounds_and_anchor(obj):
    """
    Returns a tuple of left, bottom, right, top, anchor x, and anchor y UVs for the bounding box of the object, and the bounding box

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

    #Get the UVs for these vertices
    uv_layer = obj.data.uv_layers.active.data
    if uv_layer is None:
        raise ValueError("No active UV layer found on the object.")
    
    left_u = uv_layer[left_vertex.index].uv.x
    right_u = uv_layer[right_vertex.index].uv.x
    top_v = uv_layer[top_vertex.index].uv.y
    bottom_v = uv_layer[bottom_vertex.index].uv.y

    #Calculate the ratios
    x_ratio = (right_vertex.co.x - left_vertex.co.x) / (right_u - left_u)
    y_ratio = (top_vertex.co.y - bottom_vertex.co.y) / (top_v - bottom_v)

    #Now that we have the ratios, and the left/bottom coords, we can get the anchor
    # To do so, we will multiply the negative left position and negative bottom postion by the ratios,
    # then add them to the left and bottom UVs to get the anchor UVs
    anchor_u = left_u + (-left_vertex.co.x * x_ratio)
    anchor_v = bottom_v + (-bottom_vertex.co.y * y_ratio)

    #Return the UV bounds
    return left_u, bottom_v, right_u, top_v, anchor_u, anchor_v

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

    return geometery_utils.create_obj_from_draw_call(verts, indicies, "Perimeter Obj")
        
