#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/14/2024
#Purpose: Contains the properties for the whole facade in Blender. There can only be one facade per file.

import bpy  # type: ignore
import os
import io_scene_xplane_ext.Types.attached_obj as attached_obj # type: ignore
from . import geometery_utils

class spelling_entry(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("WALL", "Wall", "Wall definition"),
            ("WALL_RULE ", "Wall Rule", "Second wall rule"),
            ("SPELLING", "Spelling", "Wall spelling")
        ],
        update=update_ui)# type: ignore
    min_width: bpy.props.FloatProperty(name="Min Width", description="The minimum width of the wall")# type: ignore
    max_width: bpy.props.FloatProperty(name="Max Width", description="The maximum width of the wall")# type: ignore
    min_heading: bpy.props.FloatProperty(name="Min Heading", description="The minimum heading of the wall")# type: ignore
    max_heading: bpy.props.FloatProperty(name="Max Heading", description="The maximum heading of the wall")# type: ignore
    spellings: bpy.props.StringProperty(name="Spellings", default="", update=update_ui)# type: ignore
    wall_name: bpy.props.StringProperty(name="Wall Name", default="", update=update_ui)# type: ignore

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

#Gets the geometry of a segment, and attached objects, from a layer in a blender scene. Returns the all data in a string, formatted for an X-Plane Facade
def get_segment(layer):

    #Define an empty array of attached objects
    attached_objects = []

    #Define a string to hold output
    output = ""

    #Iterate through the objects in the layer
    for obj in layer.objects:
        #If the object is a segment, get its geometry
        if obj.type == "MESH":
            #Get the geometry of this object. Tuple of (verts, indicies)
            geometry = geometery_utils.get_draw_call_from_obj(obj)

            #add the mesh header (MESH <group> <far LOD> <cuts> <vertex_count> <idx_count>)
            output += "MESH\t" + str(obj.facade_object.group) + "\t" + str(obj.facade_object.far_lod) + "\t" + str(obj.facade_object.cuts) + "\t" + str(len(geometry[0])) + "\t" + str(len(geometry[1])) + "\n"

            #Add the verticies
            for v in geometry[0]:
                output += v.to_string() + "\n"

            #Add the indicies
            for i in range(0, len(geometry[1])):
                #Add the newline idx
                if (i + 1) % 10 == 1:
                    output += "IDX "

                #Add the index
                output += str(geometry[1][i]) + " "

                #Add the newline every 10 indicies
                if (i + 1) % 10 == 0 and i != 0:
                    output += "\n"
            output += "\n"

        #If this is an empty, these typically are an attached object. We will check and handle that here.
        if obj.type == "EMPTY":
            attached_obj = attached_obj.xp_attached_obj()
            attached_obj.read_from_obj(obj)

            if attached_obj.valid:
                attached_objects.append(attached_obj)

    #Add the attached objects
    for obj in attached_objects:
        output += obj.get_string() + "\n"

    #Return the output
    return output