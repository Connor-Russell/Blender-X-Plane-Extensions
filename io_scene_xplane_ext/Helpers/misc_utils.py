#Project: Blender-X-Plane-Extensions
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple utility functions (like linear_search) to help with various tasks.

import mathutils
import math
import bpy

def linear_search_list(in_list, search_value):
    """
    Searches for a value in a list and returns its index if found, otherwise returns -1.
    Args:
        in_list (list): The list to search.
        search_value: The value to search for.
    Returns:
        int: The index of the value if found, otherwise -1.
    Notes:
        in_list must of course have an __eq__ method defined that works with the search_value type.
    """
    for i in range(len(in_list)):
        if in_list[i] == search_value:
            return i
    return -1

def ftos(value, precision):
    """
    Simple float to string with specified precision.
    Args:
        value (float): The float value to convert.
        precision (int): The number of decimal places to include in the string.
    Returns:
        str: The float value as a string with the specified precision.
    """
    return "{:.{precision}f}".format(value, precision=precision)

def resolve_heading(heading):
    """
    Normalizes a heading to the range 0-360 degrees.
    Args:
        heading (float): The heading in degrees.
    Returns:
        float: The heading in degrees, normalized to the range [0, 360).
    """
    while heading < 0:
        heading += 360

    while heading > 360:
        heading -= 360

    return heading

def dedupe_list(in_list):
    """
    Removes duplicate entries from a list while preserving the order of the first occurrences.
    Args:
        in_list (list): The list to deduplicate.
    Returns:
        list: A new list with duplicates removed.
    """
    lt = in_list.copy()
    lt.sort()

    if len(lt) < 2:
        return lt

    new_list = []

    new_list.append(lt[0])

    for i, item in enumerate(lt):
        if i == 0:
            continue
        if item != lt[i - 1]:
            new_list.append(item)

    return new_list

def winding_is_ccw(verts):
    """
    Determines if a list of 2D mathutils.Vector points is wound counterclockwise.
    Uses the signed area (shoelace formula): positive area = CCW, negative = CW.

    Args:
        verts (list of mathutils.Vector): List of 2D vectors (x, y) or 3D vectors (x, y, z).

    Returns:
        bool: True if the winding is counterclockwise, False if clockwise.
    """
    area = 0.0
    n = len(verts)
    for i in range(n):
        v1 = verts[i]
        v2 = verts[(i + 1) % n]
        # Use only x and y for area calculation
        area += (v2.x - v1.x) * (v2.y + v1.y)
    return area < 0  # CCW if area is negative

def make_winding_ccw(verts):
    """
    Ensures that a list of 2D mathutils.Vector points is wound counterclockwise.
    If the winding is clockwise, it reverses the order of the vertices.

    Args:
        verts (list of mathutils.Vector): List of 2D vectors (x, y) or 3D vectors (x, y, z).

    Returns:
        list of mathutils.Vector: The input list with vertices ordered counterclockwise.
    """
    new_verts = verts
    if not winding_is_ccw(verts):
        new_verts = verts.copy()
        new_verts.reverse()
    return new_verts

def copy_to_clipboard(text):
    bpy.context.window_manager.clipboard = text

def get_from_clipboard():
    return bpy.context.window_manager.clipboard