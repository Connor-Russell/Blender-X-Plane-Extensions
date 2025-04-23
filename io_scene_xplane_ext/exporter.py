#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Export
#Purpose:   Provide a single file containing functions for exporting

import bpy #type: ignore
import os

from .Helpers import file_utils
from .Helpers import line_utils
from .Types import xp_line
from .Types import xp_fac

def export_fac(in_col):
    #Create an xp_fac, load it from the collection, and write it to a file
    output = xp_fac.facade()
    output.from_collection(in_col)
    export_path = ""
    if in_col.xp_fac.name != "":
        export_path = file_utils.rel_to_abs(in_col.xp_fac.name + ".fac")
    else:
        export_path = os.path.join(os.path.dirname(bpy.data.filepath), in_col.name + ".fac")

    #Make sure we don't have a duplicate extension
    if export_path.lower().endswith(".fac.fac"):
        export_path = export_path[:-4]

    #Write the file
    output.write(export_path)
    

def export_lin(in_col):
    #First iterate through all the objects in this collection. Here we will determine a list of objects eligable for export
    exportable_objects = []

    for obj in in_col.objects:
        if obj.type == 'MESH':
            #Check if this object is exportable
            if obj.xp_lin.is_exportable:
                exportable_objects.append(obj)

    #TODO: Check that we have objects, and at least one is a segment. If not, throw an error
    if len(exportable_objects) == 0:
        return
    if len([obj for obj in exportable_objects if obj.xp_lin.type == "SEGMENT"]) == 0:
        raise Exception("Error: No segment objects found in collection" + in_col.name)
    
    #Now we want to sort them based on their Z position. While not *necessary*, it makes the output nicer
    exportable_objects.sort(key=lambda x: x.location.z)

    #Now we need to get the scale. We will get this from the bottom object
    scale_x, scale_y = 0, 0
    
    #Find the first non-cap object, and get the scale from it
    for obj in exportable_objects:
        if obj.xp_lin.is_exportable:
            scale_x, scale_y = line_utils.get_scale_from_layer(obj)
            break

    #Define a new XPLin object
    lin = xp_line.XPLin()

    #Start setting params
    lin.scale_x = scale_x
    lin.scale_y = scale_y
    lin.segment_count = in_col.xp_lin.segment_count
    lin.mirror = in_col.xp_lin.mirror

    #Make sure we have a material
    if len(in_col.objects[0].data.materials) == 0:
        raise Exception(f"Error: No material found on object! { in_col.objects[0].name } Please configure material with my X-Plane Material Plugin!")

    #Now we need to get the material params
    mat = in_col.objects[0].data.materials[0].xp_materials

    #Now we can set params based on it
    lin.layer = mat.layer_group
    lin.layer_offset = mat.layer_group_offset
    lin.alb_texture = mat.alb_texture
    lin.nml_texture = mat.normal_texture
    lin.do_blend = mat.blend_alpha
    lin.blend_cutoff = mat.blend_cutoff
    lin.decal_1 = mat.decal_one
    lin.decal_2 = mat.decal_two

    #Now that main properties are set, we can get segment commands. First we need a list of all heights. Then we sort that array
    all_layers = [obj.location.z for obj in exportable_objects]
    all_layers.sort()


    for obj in exportable_objects:
        #Get it's type
        type = obj.xp_lin.type

        #Get it's layer. That is it's index in the all_layers
        offset = all_layers.index(obj.location.z)

        #Get the segment
        if type == "SEGMENT":
            seg = line_utils.get_layer_from_segment_object(obj, offset, type)
            lin.segments.append(seg)
        else:
            cap = line_utils.get_layer_from_cap_object(obj, offset, type)
            lin.caps.append(cap)
    
    #Get the export path. It is relative to the blender file path
    export_path = ""
    if (in_col.xp_lin.export_path == ""):
        export_path = os.path.join(os.path.dirname(bpy.data.filepath), in_col.name + ".lin")
    else:
        export_path = os.path.join(os.path.dirname(bpy.data.filepath), in_col.xp_lin.export_path)


    #Write the file
    lin.write(export_path)


