#Project: Blender-X-Plane-Extensions
#Author: Connor Russell
#Date: 11/14/2024
#Purpose: Contains the properties for the whole facade in Blender. There can only be one facade per file.

import bpy  # type: ignore
import os
import io_scene_xplane_ext.Types.xp_attached_obj as xp_attached_obj # type: ignore
from . import geometery_utils

def get_roof_data(collection):
    """
    Returns the roof data for the given collection.
    Args:
        collection (bpy.types.Collection): The collection to get roof data from.
    Returns:
        tuple: A tuple containing (roof scale x (float), roof scale y (float), roof objects (xp_attached_obj list), roof heights (float list)).
    Notes:
        - The roof scale is a tuple of (x, y) values.
        - The roof objects are a list of xp_attached_obj objects.
        - The roof heights are a list of z values.
    """
    roof_scale_x = 1
    roof_scale_y = 1
    roof_objs = []
    roof_heights = []

    #Loop through and find the first mesh object
    for obj in collection.objects:
        if obj.type == 'MESH':
            #Get the count of it's vertices. If it is not 4, skip it.
            if len(obj.data.vertices) != 4:
                continue

            #Get this object's dimensions. This will be used to scale the roof
            roof_scale_x = obj.dimensions.x
            roof_scale_y = obj.dimensions.y

            #Get it's Z position. This will be used to determine the roof height
            roof_height = obj.location.z
            roof_heights.append(roof_height)

        elif obj.type == 'EMPTY':
            #Attempt to load this attached object and save it if the results are not None
            roof_obj = xp_attached_obj.xp_attached_obj()
            roof_obj.read_from_obj(obj)

            if roof_obj.valid:
                roof_objs.append(roof_obj)

    #Sort the roof heights
    roof_heights.sort()

    #Return a tuple of the roof scale and the roof objects
    return (roof_scale_x, roof_scale_y, roof_objs, roof_heights)

