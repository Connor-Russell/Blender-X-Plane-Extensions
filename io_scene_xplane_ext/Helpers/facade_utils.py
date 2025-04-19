#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/14/2024
#Purpose: Contains the properties for the whole facade in Blender. There can only be one facade per file.

import bpy  # type: ignore
import os
import io_scene_xplane_ext.Types.attached_obj as attached_obj # type: ignore
from . import geometery_utils

def read_roof_from_collection(self, collection):
        roof_scale_x = 1
        roof_scale_y = 1
        self.roof_objs = []

        #Loop through and find the first mesh object
        for obj in collection.objects:
            if obj.type == 'MESH':
                #Get this object's dimensions. This will be used to scale the roof
                self.roof_scale_x = obj.dimensions.x
                self.roof_scale_y = obj.dimensions.y

            elif obj.type == 'EMPTY':
                #Attempt to load this attached object and save it if the results are not None
                roof_obj = attached_obj.xp_attached_obj()
                roof_obj.read_from_obj(obj)

                if roof_obj.valid:
                    self.roof_objs.append(roof_obj)

        #Return a tuple of the roof scale and the roof objects
        return (roof_scale_x, roof_scale_y, self.roof_objs)

