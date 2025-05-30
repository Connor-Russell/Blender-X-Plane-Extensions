#Project: Blender-X-Plane-Extensions
#Author: Connor Russell
#Date: 11/20/2024
#Purpose: Provide a class that contains all the data for a decal

import bpy # type: ignore
import os
from . import file_utils # type: ignore

def set_xp_decal_prop(in_collection, in_material, in_decal_prop, index):
    """
    Sets the X-Plane decal properties for a given collection and material.
    Args:
        in_collection: The collection we are setting the decal properties for.
        in_material: The material we are setting the decal properties from.
        in_decal_prop: The decal property we are setting the properties from.
        index: The index of the decal.
    """
    #Get the decal field
    dcl = in_decal_prop

    #Define the names
    dcl_name = "decal" + str(index)
    dcl_name_nml = "normal_" + dcl_name

    print("file_" + dcl_name)

    #If we are draped, we need to alter the names
    if in_material.xp_materials.draped:
        dcl_name_nml = "draped_" + dcl_name_nml

    if dcl.alb != "":

        if not dcl.enabled:
            if in_material.xp_materials.draped:
                setattr(in_collection.xplane.layer, "file_draped_" + dcl_name, "")
            else:
                setattr(in_collection.xplane.layer, "file_" + dcl_name, "")
        else:
            if in_material.xp_materials.draped:
                setattr(in_collection.xplane.layer, "file_draped_" + dcl_name, dcl.alb)
                setattr(in_collection.xplane.layer, "draped_" + dcl_name + "_projected", dcl.projected)

                if dcl.projected:
                    setattr(in_collection.xplane.layer, "draped_" + dcl_name + "_x_scale", dcl.scale_x)
                    setattr(in_collection.xplane.layer, "draped_" + dcl_name + "_y_scale", dcl.scale_y)
                else:
                    setattr(in_collection.xplane.layer, "draped_" +  dcl_name + "_scale", dcl.tile_ratio)

                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_red_key", dcl.rgb_decal_key_red)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_green_key", dcl.rgb_decal_key_green)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_blue_key", dcl.rgb_decal_key_blue)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_alpha_key", dcl.rgb_decal_key_alpha)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_constant", dcl.rgb_strength_constant)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_modulator", dcl.rgb_strength_modulator)

                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_red_key", dcl.alpha_decal_key_red)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_green_key", dcl.alpha_decal_key_green)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_blue_key", dcl.alpha_decal_key_blue)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_alpha_key", dcl.alpha_decal_key_alpha)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_constant", dcl.alpha_strength_constant)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_modulator", dcl.alpha_strength_modulator)
            else:
                setattr(in_collection.xplane.layer, "file_" + dcl_name, dcl.alb)
                setattr(in_collection.xplane.layer, dcl_name + "_projected", dcl.projected)

                if dcl.projected:
                    setattr(in_collection.xplane.layer, dcl_name + "_x_scale", dcl.scale_x)
                    setattr(in_collection.xplane.layer, dcl_name + "_y_scale", dcl.scale_y)
                else:
                    setattr(in_collection.xplane.layer, dcl_name + "_scale", dcl.tile_ratio)

                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_red_key", dcl.rgb_decal_key_red)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_green_key", dcl.rgb_decal_key_green)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_blue_key", dcl.rgb_decal_key_blue)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_alpha_key", dcl.rgb_decal_key_alpha)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_constant", dcl.rgb_strength_constant)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_modulator", dcl.rgb_strength_modulator)

                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_red_key", dcl.alpha_decal_key_red)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_green_key", dcl.alpha_decal_key_green)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_blue_key", dcl.alpha_decal_key_blue)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_alpha_key", dcl.alpha_decal_key_alpha)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_constant", dcl.alpha_strength_constant)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_modulator", dcl.alpha_strength_modulator)
                    
    if dcl.nml != "":

        if not dcl.enabled:
            setattr(in_collection.xplane.layer, "file_" + dcl_name_nml, "")
        else:
            if dcl.normal_follows_albedo:
                setattr(in_collection.xplane.layer, "file_" + dcl_name_nml, dcl.nml)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_projected", dcl.projected)

                if dcl.projected:
                    setattr(in_collection.xplane.layer, dcl_name_nml + "_x_scale", dcl.scale_x)
                    setattr(in_collection.xplane.layer, dcl_name_nml + "_y_scale", dcl.scale_y)
                else:
                    setattr(in_collection.xplane.layer, dcl_name_nml + "_scale", dcl.tile_ratio)

                setattr(in_collection.xplane.layer, dcl_name_nml + "_red_key", dcl.rgb_decal_key_red)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_green_key", dcl.rgb_decal_key_green)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_blue_key", dcl.rgb_decal_key_blue)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_alpha_key", dcl.rgb_decal_key_alpha)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_constant", dcl.rgb_strength_constant)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_modulator", dcl.rgb_strength_modulator)
            else:
                setattr(in_collection.xplane.layer, "file_" + dcl_name_nml, dcl.nml)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_projected", dcl.nml_projected)

                if dcl.nml_projected:
                    setattr(in_collection.xplane.layer, dcl_name_nml + "_x_scale", dcl.nml_scale_x)
                    setattr(in_collection.xplane.layer, dcl_name_nml + "_y_scale", dcl.nml_scale_y)
                else:
                    setattr(in_collection.xplane.layer, dcl_name_nml + "_scale", dcl.nml_tile_ratio)

                setattr(in_collection.xplane.layer, dcl_name_nml + "_red_key", dcl.nml_decal_key_red)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_green_key", dcl.nml_decal_key_green)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_blue_key", dcl.nml_decal_key_blue)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_alpha_key", dcl.nml_decal_key_alpha)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_constant", dcl.nml_strength_constant)
                setattr(in_collection.xplane.layer, dcl_name_nml + "_modulator", dcl.nml_strength_modulator)

def get_decal_command(in_decal, in_output_folder):
    """
    Returns the command for the decal
    Args:
        in_decal: The decal object we are trying to get the command for.
        in_output_folder: The output folder to use for relative paths.
    Returns:
        str: The command for the decal.
    """

    #Albedo
    alb_decal = ""
    
    if in_decal.alb != "":
        if in_decal.projected:
            #Format: DECAL_PARAMS_PROJ <x> <y> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <alpha r key> <alpha g key> <alpha b key> <alpha alpha key> <alpha modulator> <alpha constant> <file>
            alb_decal = f"DECAL_PARAMS_PROJ {in_decal.scale_x} {in_decal.scale_y} {in_decal.dither_ratio} {in_decal.rgb_decal_key_red} {in_decal.rgb_decal_key_green} {in_decal.rgb_decal_key_blue} {in_decal.rgb_decal_key_alpha} {in_decal.rgb_strength_modulator} {in_decal.rgb_strength_constant} {in_decal.alpha_decal_key_red} {in_decal.alpha_decal_key_green} {in_decal.alpha_decal_key_blue} {in_decal.alpha_decal_key_alpha} {in_decal.alpha_strength_modulator} {in_decal.alpha_strength_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.alb), in_output_folder)}"
        else:
            #Format: DECAL_PARAMS <tile ratio> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <alpha r key> <alpha g key> <alpha b key> <alpha alpha key> <alpha modulator> <alpha constant> <file>
            alb_decal = f"DECAL_PARAMS {in_decal.tile_ratio} {in_decal.dither_ratio} {in_decal.rgb_decal_key_red} {in_decal.rgb_decal_key_green} {in_decal.rgb_decal_key_blue} {in_decal.rgb_decal_key_alpha} {in_decal.rgb_strength_modulator} {in_decal.rgb_strength_constant} {in_decal.alpha_decal_key_red} {in_decal.alpha_decal_key_green} {in_decal.alpha_decal_key_blue} {in_decal.alpha_decal_key_alpha} {in_decal.alpha_strength_modulator} {in_decal.alpha_strength_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.alb), in_output_folder)}"

        if in_decal.nml != "":
            alb_decal += "\n"
    #Normal

    nml_decal = ""

    if in_decal.normal_follows_albedo and in_decal.nml != "":
        if in_decal.projected:
            #Format: NORMAL_DECAL_PARAMS <tile ratio> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <file>
            nml_decal = f"NORMAL_DECAL_PARAMS_PROJ {in_decal.scale_x} {in_decal.scale_y} {in_decal.rgb_decal_key_red} {in_decal.rgb_decal_key_green} {in_decal.rgb_decal_key_blue} {in_decal.rgb_decal_key_alpha} {in_decal.rgb_strength_modulator} {in_decal.rgb_strength_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.nml), in_output_folder)}"
        else:
            #Format: NORMAL_DECAL_PARAMS <tile ratio> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <file>
            nml_decal = f"NORMAL_DECAL_PARAMS {in_decal.tile_ratio} {in_decal.rgb_decal_key_red} {in_decal.rgb_decal_key_green} {in_decal.rgb_decal_key_blue} {in_decal.rgb_decal_key_alpha} {in_decal.rgb_strength_modulator} {in_decal.rgb_strength_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.nml), in_output_folder)}"
    elif in_decal.nml != "":
        if in_decal.projected:
            #Format: NORMAL_DECAL_PARAMS <tile ratio> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <file>
            nml_decal = f"NORMAL_DECAL_PARAMS_PROJ {in_decal.nml_scale_x} {in_decal.nml_scale_y} {in_decal.nml_decal_key_red} {in_decal.nml_decal_key_green} {in_decal.nml_decal_key_blue} {in_decal.nml_decal_key_alpha} {in_decal.nml_strength_modulator} {in_decal.nml_strength_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.nml), in_output_folder)}"
        else:
            #Format: NORMAL_DECAL_PARAMS <tile ratio> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <file>
            nml_decal = f"NORMAL_DECAL_PARAMS {in_decal.nml_tile_ratio} {in_decal.nml_decal_key_red} {in_decal.nml_decal_key_green} {in_decal.nml_decal_key_blue} {in_decal.nml_decal_key_alpha} {in_decal.nml_strength_modulator} {in_decal.nml_strength_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.nml), in_output_folder)}"
    
    return alb_decal + nml_decal

def get_decal_from_command(in_command, in_decal_prop):
    """
    TODO: This function does not work yet!!!
    """
    #Split the command into parts
    parts = in_command.split(" ")

    #Get the type of decal
    if parts[0] == "DECAL_PARAMS":
        #Get the parameters
        in_decal_prop.tile_ratio = float(parts[1])
        in_decal_prop.dither_ratio = float(parts[2])
        in_decal_prop.rgb_decal_key_red = float(parts[3])
        in_decal_prop.rgb_decal_key_green = float(parts[4])
        in_decal_prop.rgb_decal_key_blue = float(parts[5])
        in_decal_prop.rgb_decal_key_alpha = float(parts[6])
        in_decal_prop.rgb_strength_modulator = float(parts[7])
        in_decal_prop.rgb_strength_constant = float(parts[8])
        in_decal_prop.alpha_decal_key_red = float(parts[9])
        in_decal_prop.alpha_decal_key_green = float(parts[10])
        in_decal_prop.alpha_decal_key_blue = float(parts[11])
        in_decal_prop.alpha_decal_key_alpha = float(parts[12])
        in_decal_prop.alpha_strength_modulator = float(parts[13])
        in_decal_prop.alpha_strength_constant = float(parts[14])
        in_decal_prop.alb = parts[15]
        in_decal_prop.projected = False

    elif parts[0] == "DECAL_PARAMS_PROJ":
        #Get the parameters
        in_decal_prop.scale_x = float(parts[1])
        in_decal_prop.scale_y = float(parts[2])
        in_decal_prop.dither_ratio = float(parts[3])
        in_decal_prop.rgb_decal_key_red = float(parts[4])
        in_decal_prop.rgb_decal_key_green = float(parts[5])
        in_decal_prop.rgb_decal_key_blue = float(parts[6])
        in_decal_prop.rgb_decal_key_alpha = float(parts[7])
        in_decal_prop.rgb_strength_modulator = float(parts[8])
        in_decal_prop.rgb_strength_constant = float(parts[9])
        in_decal_prop.alpha_decal_key_red = float(parts[10])
        in_decal_prop.alpha_decal_key_green = float(parts[11])
        in_decal_prop.alpha_decal_key_blue = float(parts[12])
        in_decal_prop.alpha_decal_key_alpha = float(parts[13])
        in_decal_prop.alpha_strength_modulator = float(parts[14])
        in_decal_prop.alpha_strength_constant = float(parts[15])
        in_decal_prop.alb = parts[16]
        in_decal_prop.projected = True

    elif parts[0] == "NORMAL_DECAL_PARAMS":
        #Get the parameters
        in_decal_prop.nml_tile_ratio = float(parts[1])
        in_decal_prop.nml_decal_key_red = float(parts[2])
        in_decal_prop.nml_decal_key_green = float(parts[3])
        in_decal_prop.nml_decal_key_blue = float(parts[4])
        in_decal_prop.nml_decal_key_alpha = float(parts[5])
        in_decal_prop.nml_strength_modulator = float(parts[6])
        in_decal_prop.nml_strength_constant = float(parts[7])
        in_decal_prop.nml = parts[8]
        in_decal_prop.projected = False

    elif parts[0] == "NORMAL_DECAL_PARAMS_PROJ":
        #Get the parameters
        in_decal_prop.nml_scale_x = float(parts[1])
        in_decal_prop.nml_scale_y = float(parts[2])
        in_decal_prop.nml_decal_key_red = float(parts[3])
        in_decal_prop.nml_decal_key_green = float(parts[4])
        in_decal_prop.nml_decal_key_blue = float(parts[5])
        in_decal_prop.nml_decal_key_alpha = float(parts[6])
        in_decal_prop.nml_strength_modulator = float(parts[7])
        in_decal_prop.nml_strength_constant = float(parts[8])
        in_decal_prop.nml = parts[9]
        in_decal_prop.projected = True
    