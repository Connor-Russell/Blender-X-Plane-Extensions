#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple utility functions (like linear_search) to help with various tasks.

#Linearly searches an list for a value. If a class the class must have an __eq__ method. Returns the index of the value if found, -1 if not.
def linear_search_list(in_list, search_value):
    for i in range(len(in_list)):
        if in_list[i] == search_value:
            return i
    return -1

#Converts a float to a string with a given precision
def ftos(value, precision):
    return "{:.{precision}f}".format(value, precision=precision)

#Converts a Blender heading to an X-Plane heading. positive being to the right vs negative to the right.
def resolve_heading(heading):
    while heading < 0:
        heading += 360

    while heading > 360:
        heading -= 360

    return heading

