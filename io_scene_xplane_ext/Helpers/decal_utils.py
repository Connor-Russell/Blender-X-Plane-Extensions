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
        index: The index of the decal. 1-2 for alb, and 1-2 for nml
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

    if not dcl.is_normal:
        #Clear file paths if disabled
        if not dcl.enabled:
            if in_material.xp_materials.draped:
                setattr(in_collection.xplane.layer, "file_draped_" + dcl_name, "")
            else:
                setattr(in_collection.xplane.layer, "file_" + dcl_name, "")
        else:
            if in_material.xp_materials.draped:
                setattr(in_collection.xplane.layer, "file_draped_" + dcl_name, dcl.texture)
                setattr(in_collection.xplane.layer, "draped_" + dcl_name + "_projected", dcl.projected)

                if dcl.projected:
                    setattr(in_collection.xplane.layer, "draped_" + dcl_name + "_x_scale", dcl.scale_x)
                    setattr(in_collection.xplane.layer, "draped_" + dcl_name + "_y_scale", dcl.scale_y)
                else:
                    setattr(in_collection.xplane.layer, "draped_" +  dcl_name + "_scale", dcl.tile_ratio)

                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_red_key", dcl.strength_key_red)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_green_key", dcl.strength_key_green)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_blue_key", dcl.strength_key_blue)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_alpha_key", dcl.strength_key_alpha)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_constant", dcl.rgb_strength_constant)
                setattr(in_collection.xplane.layer, "draped_rgb_" + dcl_name + "_modulator", dcl.rgb_strength_modulator)

                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_red_key", dcl.strength2_key_red)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_green_key", dcl.strength2_key_green)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_blue_key", dcl.strength2_key_blue)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_alpha_key", dcl.strength2_key_alpha)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_constant", dcl.alpha_strength_constant)
                setattr(in_collection.xplane.layer, "draped_alpha_" + dcl_name + "_modulator", dcl.alpha_strength_modulator)
            else:
                setattr(in_collection.xplane.layer, "file_" + dcl_name, dcl.texture)
                setattr(in_collection.xplane.layer, dcl_name + "_projected", dcl.projected)

                if dcl.projected:
                    setattr(in_collection.xplane.layer, dcl_name + "_x_scale", dcl.scale_x)
                    setattr(in_collection.xplane.layer, dcl_name + "_y_scale", dcl.scale_y)
                else:
                    setattr(in_collection.xplane.layer, dcl_name + "_scale", dcl.tile_ratio)

                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_red_key", dcl.strength_key_red)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_green_key", dcl.strength_key_green)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_blue_key", dcl.strength_key_blue)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_alpha_key", dcl.strength_key_alpha)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_constant", dcl.rgb_strength_constant)
                setattr(in_collection.xplane.layer, "rgb_" + dcl_name + "_modulator", dcl.rgb_strength_modulator)

                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_red_key", dcl.strength2_key_red)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_green_key", dcl.strength2_key_green)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_blue_key", dcl.strength2_key_blue)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_alpha_key", dcl.strength2_key_alpha)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_constant", dcl.alpha_strength_constant)
                setattr(in_collection.xplane.layer, "alpha_" + dcl_name + "_modulator", dcl.alpha_strength_modulator)
                    
    #Clear the file path if disabled
    if not dcl.enabled:
        setattr(in_collection.xplane.layer, "file_" + dcl_name_nml, "")
    else:
        setattr(in_collection.xplane.layer, "file_" + dcl_name_nml, dcl.texture)
        setattr(in_collection.xplane.layer, dcl_name_nml + "_projected", dcl.projected)

        if dcl.projected:
            setattr(in_collection.xplane.layer, dcl_name_nml + "_x_scale", dcl.scale_x)
            setattr(in_collection.xplane.layer, dcl_name_nml + "_y_scale", dcl.scale_y)
        else:
            setattr(in_collection.xplane.layer, dcl_name_nml + "_scale", dcl.tile_ratio)

        setattr(in_collection.xplane.layer, dcl_name_nml + "_red_key", dcl.strength_key_red)
        setattr(in_collection.xplane.layer, dcl_name_nml + "_green_key", dcl.strength_key_green)
        setattr(in_collection.xplane.layer, dcl_name_nml + "_blue_key", dcl.strength_key_blue)
        setattr(in_collection.xplane.layer, dcl_name_nml + "_alpha_key", dcl.strength_key_alpha)
        setattr(in_collection.xplane.layer, dcl_name_nml + "_constant", dcl.rgb_strength_constant)
        setattr(in_collection.xplane.layer, dcl_name_nml + "_modulator", dcl.rgb_strength_modulator)
            
def get_decal_command(in_decal, in_output_folder):
    """
    Returns the command for the decal
    Args:
        in_decal: The decal object we are trying to get the command for.
        in_output_folder: The output folder to use for relative paths.
    Returns:
        str: The command for the decal.
    """

    out_cmd = ""

    if not in_decal.enabled:
        return ""

    if not in_decal.is_normal:
        if in_decal.projected:
            #Format: DECAL_PARAMS_PROJ <x> <y> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <alpha r key> <alpha g key> <alpha b key> <alpha alpha key> <alpha modulator> <alpha constant> <file>
            out_cmd = f"DECAL_PARAMS_PROJ {in_decal.scale_x} {in_decal.scale_y} {in_decal.dither_ratio} {in_decal.strength_key_red} {in_decal.strength_key_green} {in_decal.strength_key_blue} {in_decal.strength_key_alpha} {in_decal.strength_modulator} {in_decal.strength_constant} {in_decal.strength2_key_red} {in_decal.strength2_key_green} {in_decal.strength2_key_blue} {in_decal.strength2_key_alpha} {in_decal.strength2_modulator} {in_decal.strength2_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.texture), in_output_folder)}\n"
        else:
            #Format: DECAL_PARAMS <tile ratio> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <alpha r key> <alpha g key> <alpha b key> <alpha alpha key> <alpha modulator> <alpha constant> <file>
            out_cmd = f"DECAL_PARAMS {in_decal.tile_ratio} {in_decal.dither_ratio} {in_decal.strength_key_red} {in_decal.strength_key_green} {in_decal.strength_key_blue} {in_decal.strength_key_alpha} {in_decal.strength_modulator} {in_decal.strength_constant} {in_decal.strength2_key_red} {in_decal.strength2_key_green} {in_decal.strength2_key_blue} {in_decal.strength2_key_alpha} {in_decal.strength2_modulator} {in_decal.strength2_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.texture), in_output_folder)}\n"

    else:
        if in_decal.projected:
            #Format: NORMAL_DECAL_PARAMS <tile ratio> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <file>
            out_cmd = f"NORMAL_DECAL_PARAMS_PROJ {in_decal.scale_x} {in_decal.scale_y} {in_decal.strength_key_red} {in_decal.strength_key_green} {in_decal.strength_key_blue} {in_decal.strength_key_alpha} {in_decal.strength_modulator} {in_decal.strength_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.texture), in_output_folder)}\n"
        else:
            #Format: NORMAL_DECAL_PARAMS <tile ratio> <dither> <r key> <g key> <b key> <alpha key> <modulator> <constant> <file>
            out_cmd = f"NORMAL_DECAL_PARAMS {in_decal.tile_ratio} {in_decal.strength_key_red} {in_decal.strength_key_green} {in_decal.strength_key_blue} {in_decal.strength_key_alpha} {in_decal.strength_modulator} {in_decal.strength_constant} {os.path.relpath(file_utils.rel_to_abs(in_decal.texture), in_output_folder)}\n"
    
    return out_cmd

def get_decal_from_command(in_command, out_decal_prop):
    """
    Parses a decal command and sets the properties of the decal property.
    Args:
        in_command: The command to parse.
        out_decal_prop: The decal property to set.
    """
    #Split the command
    cmd_parts = in_command.split()

    if len(cmd_parts) == 0:
        raise ValueError("Empty decal command provided")

    if cmd_parts[0] == "DECAL_PARAMS_PROJ":
        out_decal_prop.enabled = True
        out_decal_prop.projected = True
        out_decal_prop.scale_x = float(cmd_parts[1])
        out_decal_prop.scale_y = float(cmd_parts[2])
        out_decal_prop.dither_ratio = float(cmd_parts[3])
        out_decal_prop.strength_key_red = float(cmd_parts[4])
        out_decal_prop.strength_key_green = float(cmd_parts[5])
        out_decal_prop.strength_key_blue = float(cmd_parts[6])
        out_decal_prop.strength_key_alpha = float(cmd_parts[7])
        out_decal_prop.strength_modulator = float(cmd_parts[8])
        out_decal_prop.strength_constant = float(cmd_parts[9])
        out_decal_prop.strength2_key_red = float(cmd_parts[10])
        out_decal_prop.strength2_key_green = float(cmd_parts[11])
        out_decal_prop.strength2_key_blue = float(cmd_parts[12])
        out_decal_prop.strength2_key_alpha = float(cmd_parts[13])
        out_decal_prop.strength2_modulator = float(cmd_parts[14])
        out_decal_prop.strength2_constant = float(cmd_parts[15])
        out_decal_prop.texture = file_utils.abs_to_rel(cmd_parts[16])

    elif cmd_parts[0] == "DECAL_PARAMS":
        out_decal_prop.enabled = True
        out_decal_prop.projected = False
        out_decal_prop.tile_ratio = float(cmd_parts[1])
        out_decal_prop.dither_ratio = float(cmd_parts[2])
        out_decal_prop.strength_key_red = float(cmd_parts[3])
        out_decal_prop.strength_key_green = float(cmd_parts[4])
        out_decal_prop.strength_key_blue = float(cmd_parts[5])
        out_decal_prop.strength_key_alpha = float(cmd_parts[6])
        out_decal_prop.strength_modulator = float(cmd_parts[7])
        out_decal_prop.strength_constant = float(cmd_parts[8])
        out_decal_prop.strength2_key_red = float(cmd_parts[9])
        out_decal_prop.strength2_key_green = float(cmd_parts[10])
        out_decal_prop.strength2_key_blue = float(cmd_parts[11])
        out_decal_prop.strength2_key_alpha = float(cmd_parts[12])
        out_decal_prop.strength2_modulator = float(cmd_parts[13])
        out_decal_prop.strength2_constant = float(cmd_parts[14])
        out_decal_prop.texture = file_utils.abs_to_rel(cmd_parts[15])

    elif cmd_parts[0] == "NORMAL_DECAL_PARAMS_PROJ":
        out_decal_prop.enabled = True
        out_decal_prop.is_normal = True
        out_decal_prop.projected = True
        out_decal_prop.scale_x = float(cmd_parts[1])
        out_decal_prop.scale_y = float(cmd_parts[2])
        out_decal_prop.strength_key_red = float(cmd_parts[3])
        out_decal_prop.strength_key_green = float(cmd_parts[4])
        out_decal_prop.strength_key_blue = float(cmd_parts[5])
        out_decal_prop.strength_key_alpha = float(cmd_parts[6])
        out_decal_prop.strength_modulator = float(cmd_parts[7])
        out_decal_prop.strength_constant = float(cmd_parts[8])
        out_decal_prop.texture = file_utils.abs_to_rel(cmd_parts[9])

    elif cmd_parts[0] == "NORMAL_DECAL_PARAMS":
        out_decal_prop.enabled = True
        out_decal_prop.is_normal = True
        out_decal_prop.projected = False
        out_decal_prop.tile_ratio = float(cmd_parts[1])
        out_decal_prop.strength_key_red = float(cmd_parts[2])
        out_decal_prop.strength_key_green = float(cmd_parts[3])
        out_decal_prop.strength_key_blue = float(cmd_parts[4])
        out_decal_prop.strength_key_alpha = float(cmd_parts[5])
        out_decal_prop.strength_modulator = float(cmd_parts[6])
        out_decal_prop.strength_constant = float(cmd_parts[7])
        out_decal_prop.texture = file_utils.abs_to_rel(cmd_parts[8])
    else:
        raise ValueError(f"Unknown decal command: {in_command}")
    