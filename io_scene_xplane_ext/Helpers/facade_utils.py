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

class FacSpelling:
    def __init__(self):
        self.is_ui_expanded = False
        self.entries = []

    def to_prop(self, prop: bpy.types.PropertyGroup):
        prop.is_ui_expanded = self.is_ui_expanded
        prop.entries.clear()
        for entry in self.entries:
            entry_prop = prop.entries.add()
            entry_prop.collection = entry   #Collection is just a string

    def from_prop(self, prop):
        self.is_ui_expanded = prop.is_ui_expanded
        self.entries = [entry.collection for entry in prop.entries]
        return self


class FacWall:
    def __init__(self):
        self.min_length = 0.0
        self.max_length = 1000.0
        self.min_heading = 0.0
        self.max_heading = 360.0
        self.name = ""
        self.spellings = []
        self.is_ui_expanded = False

    def to_prop(self, prop):
        prop.min_length = self.min_length
        prop.max_length = self.max_length
        prop.min_heading = self.min_heading
        prop.max_heading = self.max_heading
        prop.name = self.name
        prop.is_ui_expanded = self.is_ui_expanded
        prop.spellings.clear()
        for spelling in self.spellings:
            spelling_prop = prop.spellings.add()
            spelling.to_prop(spelling_prop)

    def from_prop(self, prop):
        for spelling in prop.spellings:
            spelling_obj = FacSpelling()
            spelling_obj.from_prop(spelling)
            self.spellings.append(spelling_obj)
        
        self.min_length = prop.min_length
        self.max_length = prop.max_length
        self.min_heading = prop.min_heading
        self.max_heading = prop.max_heading
        self.name = prop.name
        self.is_ui_expanded = prop.is_ui_expanded

class FacFloor:
    def __init__(self):
        self.name = ""
        self.roof_collection = ""
        self.walls = []
        self.is_ui_expanded = False 
        self.roof_collisions = False
        self.roof_two_sided = False
    
    def to_prop(self, prop):
        prop.name = self.name
        prop.roof_collection = self.roof_collection
        prop.is_ui_expanded = self.is_ui_expanded
        prop.roof_collisions = self.roof_collisions
        prop.roof_two_sided = self.roof_two_sided
        prop.walls.clear()
        for wall in self.walls:
            wall_prop = prop.walls.add()
            wall.to_prop(wall_prop)

    def from_prop(self, prop):
        self.name = prop.name
        self.roof_collection = prop.roof_collection
        self.is_ui_expanded = prop.is_ui_expanded
        self.roof_collisions = prop.roof_collisions
        self.roof_two_sided = prop.roof_two_sided
        for wall in prop.walls:
            wall_obj = FacWall()
            wall_obj.from_prop(wall)
            self.walls.append(wall_obj)
        return self
