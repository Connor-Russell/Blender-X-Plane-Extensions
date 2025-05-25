#Project: Blender-X-Plane-Extensions
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple utility functions (like linear_search) to help with various tasks.

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

#Converts a float to a string with a given precision
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

#Converts a Blender heading to an X-Plane heading. positive being to the right vs negative to the right.
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
