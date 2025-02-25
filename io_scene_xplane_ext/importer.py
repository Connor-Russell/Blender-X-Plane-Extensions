#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/23/2025
#Module:    Import
#Purpose:   Provide a single file containing functions for importing

import bpy #type: ignore

from .Helpers import line_utils
from .Types import xp_line

def import_lin(in_path):
    #Define just the file name from the path
    in_name = in_path
    in_name = in_path.split("\\")[-1]

    #Define a new collection with the same name as the file
    new_collection = bpy.data.collections.new(name=in_name)
    bpy.context.scene.collection.children.link(new_collection)

    #Read it
    lin = xp_line.XPLin()
    lin.read(in_path)

    #First create a new material for the line
    mat = bpy.data.materials.new(name=in_name)
    mat.xp_materials.alb_texture = lin.alb_texture
    mat.xp_materials.normal_texture = lin.nml_texture
    mat.xp_materials.blend_alpha = lin.do_blend
    mat.xp_materials.blend_cutoff = lin.blend_cutoff
    mat.xp_materials.layer_group = lin.layer.upper()
    mat.xp_materials.layer_group_offset = int(lin.layer_offset)

    #Call operator xp_mats.update_material_nodes
    #bpy.ops.xp_mats.update_material_nodes(mat=mat)

    #Now we will iterate through every segment, and generate a plane for it
    for seg in lin.segments:
        #Create the verticies
        LowerLeft = line_utils.LineVertex()
        LowerRight = line_utils.LineVertex()
        UpperLeft = line_utils.LineVertex()
        UpperRight = line_utils.LineVertex()

        LowerLeft.x = (seg.l - seg.c) * lin.scale_x
        LowerLeft.y = -0.5 * lin.scale_y
        LowerLeft.z = 0
        LowerLeft.u = seg.l
        LowerLeft.v = 0

        LowerRight.x = (seg.r - seg.c) * lin.scale_x
        LowerRight.y = -0.5 * lin.scale_y
        LowerRight.z = 0
        LowerRight.u = seg.r
        LowerRight.v = 0

        UpperLeft.x = (seg.l - seg.c) * lin.scale_x
        UpperLeft.y = 0.5 * lin.scale_y
        UpperLeft.z = 0
        UpperLeft.u = seg.l
        UpperLeft.v = 1

        UpperRight.x = (seg.r - seg.c) * lin.scale_x
        UpperRight.y = 0.5 * lin.scale_y
        UpperRight.z = 0
        UpperRight.u = seg.r
        UpperRight.v = 1

        #Create the faces
        new_plane = line_utils.gen_plane_from_verts([LowerLeft, LowerRight, UpperRight, UpperLeft])
        new_plane.data.materials.append(mat)

        #Link it to the scene and new collection
        new_collection.objects.link(new_plane)

    #Now we will iterate through every cap, and generate a plane for it
    for cap in lin.caps:
        #Create the verticies
        LowerLeft = line_utils.LineVertex()
        LowerRight = line_utils.LineVertex()
        UpperLeft = line_utils.LineVertex()
        UpperRight = line_utils.LineVertex()

        LowerLeft.x = (cap.l - cap.c) * lin.scale_x
        LowerLeft.y = cap.bottom * lin.scale_y
        LowerLeft.z = 0
        LowerLeft.u = cap.l
        LowerLeft.v = cap.bottom

        LowerRight.x = (cap.r - cap.c) * lin.scale_x
        LowerRight.y = cap.bottom * lin.scale_y
        LowerRight.z = 0
        LowerRight.u = cap.r
        LowerRight.v = cap.bottom

        UpperLeft.x = (cap.l - cap.c) * lin.scale_x
        UpperLeft.y = cap.top * lin.scale_y
        UpperLeft.z = 0
        UpperLeft.u = cap.l
        UpperLeft.v = cap.top

        UpperRight.x = (cap.r - cap.c) * lin.scale_x
        UpperRight.y = cap.top * lin.scale_y
        UpperRight.z = 0
        UpperRight.u = cap.r
        UpperRight.v = cap.top

        #Create the faces
        new_plane = line_utils.gen_plane_from_verts([LowerLeft, LowerRight, UpperRight, UpperLeft])
        new_plane.data.materials.append(mat)

        #Link it to the scene and new collection
        new_collection.objects.link(new_plane)

    