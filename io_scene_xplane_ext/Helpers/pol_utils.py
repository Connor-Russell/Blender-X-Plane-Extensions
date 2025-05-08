#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      5/8/2025
#Module:    Pol Utils
#Purpose:   Provide utility functions for working with polygons in Blender

import bpy

def get_uv_bounds(obj):
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
        raise ValueError("Object must be a mesh.")

    if len(obj.data.vertices) != 4:
        raise ValueError("Object must have exactly 4 vertices.")

    if not obj.data.uv_layers.active:
        raise ValueError("Object is missing UVs.")

    uv_layer = obj.data.uv_layers.active.data

    # Initialize bounds
    min_u, max_u = float('inf'), float('-inf')
    min_v, max_v = float('inf'), float('-inf')

    for loop in obj.data.loops:
        uv = uv_layer[loop.index].uv
        min_u = min(min_u, uv.x)
        max_u = max(max_u, uv.x)
        min_v = min(min_v, uv.y)
        max_v = max(max_v, uv.y)

    return [min_u, max_u, min_v, max_v]