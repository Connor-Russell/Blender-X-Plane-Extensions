
#Project: Blender-X-Plane-Extensions
#Author: Connor Russell
#Date: 10/6/2025
#Purpose: Provide simple utility functions to convert X-Plane normals/material maps from one form to another

import os
import bpy
import numpy as np
from . import file_utils

def separate_xp_combined_nml(xp_combined_nml_path):
    """
    Converts a combined X-Plane normal/material map into separate normal and material maps.

    Args:
        xp_combined_nml_path (str): Path to the combined normal/material map image file.

    Returns:
        tuple: (xp_normal_map_path, xp_material_map_path) - Paths to the generated normal and material map PNG files.
        Returns (None, None) if the input file does not exist or an error occurs.
    """
    if not os.path.isfile(xp_combined_nml_path):
        raise FileNotFoundError(f"File not found: {xp_combined_nml_path}")
    
    img_xp_combined_nml = None
    img_xp_normal = None
    img_xp_material = None

    xp_normal_map_path = ""
    xp_material_map_path = ""

    try:
        img_xp_combined_nml = bpy.data.images.load(xp_combined_nml_path)
        img_xp_combined_nml.colorspace_settings.name = 'Non-Color'  # Ensure it's treated as non-color data
        img_xp_combined_nml.name = "CONVERT_BUFFER_XP_Combined_NML_Map"

        width = img_xp_combined_nml.size[0]
        height = img_xp_combined_nml.size[1]
        combined_pixels = np.array(img_xp_combined_nml.pixels[:]).reshape((height, width, 4))

        # Create empty arrays for the separate normal and material maps
        xp_normal_map = np.zeros((height, width, 4), dtype=np.float32)
        xp_material_map = np.zeros((height, width, 4), dtype=np.float32)

        # Convert them via array slicing
        # R -> Nrm R
        # G -> Nrm G
        # B -> Mat R
        # A -> Mat G
        xp_normal_map[:, :, 0] = combined_pixels[:, :, 0]  # R
        xp_normal_map[:, :, 1] = combined_pixels[:, :, 1]  # G
        xp_normal_map[:, :, 2] = 1.0  # B (set to 1.0 for normal maps)
        xp_normal_map[:, :, 3] = 1.0  # A (set to 1.0 for normal maps)

        xp_material_map[:, :, 0] = combined_pixels[:, :, 2]  # R
        xp_material_map[:, :, 1] = combined_pixels[:, :, 3]  # G
        xp_material_map[:, :, 2] = 0.0  # B (set to 0.0 for material maps)
        xp_material_map[:, :, 3] = 1.0  # A (set to 1.0 for material maps)

        # Output paths will be based on the extensions in the preferences
        prefs = bpy.context.preferences.addons['io_scene_xplane_ext'].preferences

        # Define the output paths. Remove the extension and the combined nml suffix, then add the appropriate suffixes
        no_suffix_xp_combined_nml_map_path = os.path.splitext(xp_combined_nml_path)[0]
        if no_suffix_xp_combined_nml_map_path.endswith(prefs.suffix_combined_normal):
            no_suffix_xp_combined_nml_map_path = no_suffix_xp_combined_nml_map_path[:-len(prefs.suffix_combined_normal)]

        xp_normal_map_path = no_suffix_xp_combined_nml_map_path + prefs.suffix_normal + ".png"
        xp_material_map_path = no_suffix_xp_combined_nml_map_path + prefs.suffix_material + ".png"

        #Backup the old files
        file_utils.backup_file(xp_normal_map_path)
        file_utils.backup_file(xp_material_map_path)

        # Create new Blender images for the separate maps, assign the pixel data, and save them
        img_xp_normal = bpy.data.images.new(name="CONVERT_BUFFER_XP_Normal_Map", width=width, height=height)
        img_xp_normal.pixels = xp_normal_map.flatten()
        img_xp_normal.filepath_raw = xp_normal_map_path
        img_xp_normal.file_format = 'PNG'
        img_xp_normal.save()

        img_xp_material = bpy.data.images.new(name="CONVERT_BUFFER_XP_Material_Map", width=width, height=height)
        img_xp_material.pixels = xp_material_map.flatten()
        img_xp_material.filepath_raw = xp_material_map_path
        img_xp_material.file_format = 'PNG'
        img_xp_material.save()

        # Return the paths to the new maps
        return xp_normal_map_path, xp_material_map_path
    except Exception as e:
        raise RuntimeError(f"Error during conversion: {e}")
    finally:
        # Clean up the temporary images from Blender memory
        if img_xp_combined_nml:
            bpy.data.images.remove(img_xp_combined_nml)
        if img_xp_normal:
            bpy.data.images.remove(img_xp_normal)
        if img_xp_material:
            bpy.data.images.remove(img_xp_material)

        return xp_normal_map_path, xp_material_map_path

def combine_xp_separate_maps(xp_normal_map_path, xp_material_map_path):
    """
    Combines separate X-Plane normal and material maps into a single combined normal/material map.

    Args:
        xp_normal_map_path (str): Path to the normal map image file.
        xp_material_map_path (str): Path to the material map image file.

    Returns:
        str: Path to the generated combined normal/material map PNG file.
        Returns None if an error occurs.
    """
    #If neither exists, raise an error. If just one is missing we can fill it with sane blank data
    if not os.path.isfile(xp_normal_map_path) and not os.path.isfile(xp_material_map_path):
        raise FileNotFoundError(f"Neither normal map nor material map found: {xp_normal_map_path}, {xp_material_map_path}")

    #We store these here so if we get an exception, we can still clean them up
    img_xp_normal = None
    img_xp_material = None
    img_xp_combined_nml = None

    xp_combined_nml_map_path = ""

    try:
        #Attempt to load
        if os.path.isfile(xp_normal_map_path):
            img_xp_normal = bpy.data.images.load(xp_normal_map_path)
            img_xp_normal.colorspace_settings.name = 'Non-Color'
            img_xp_normal.name = "CONVERT_BUFFER_XP_Normal_Map"

        if os.path.isfile(xp_material_map_path):
            img_xp_material = bpy.data.images.load(xp_material_map_path)
            img_xp_material.colorspace_settings.name = 'Non-Color'
            img_xp_material.name = "CONVERT_BUFFER_XP_Material_Map"

        #Get the dimensions. If there is a mismatch (and we have both images), resize the smallest to match the largest.
        nrm_width = 0
        nrm_height = 0
        mat_width = 0
        mat_height = 0
        if img_xp_normal:
            nrm_width = img_xp_normal.size[0]
            nrm_height = img_xp_normal.size[1]
        if img_xp_material:
            mat_width = img_xp_material.size[0]
            mat_height = img_xp_material.size[1]

        width = max(nrm_width, mat_width)
        height = max(nrm_height, mat_height)

        if img_xp_normal and img_xp_material:
            #Resize the smaller to match the larger
            if nrm_width != width or nrm_height != height:
                img_xp_normal.scale(width, height)

        # Default the normal pixels to an array of 0.5, 0.5, 1.0, 1.0 (flat normal)
        normal_pixels = np.full((height, width, 4), [0.5, 0.5, 1.0, 1.0], dtype=np.float32)
        
        # Default the material pixels to an array of 0.0, 0.0, 1.0, 1.0 (rough non-metal)
        material_pixels = np.full((height, width, 4), [0.0, 0.0, 1.0, 1.0], dtype=np.float32)

        #Populate the pixel arrays if we have the images
        if img_xp_normal:
            normal_pixels = np.array(img_xp_normal.pixels[:]).reshape((height, width, 4))
        if img_xp_material:
            material_pixels = np.array(img_xp_material.pixels[:]).reshape((height, width, 4))

        # Create combined map: R = Nrm R, G = Nrm G, B = Mat R, A = Mat G
        combined_map = np.zeros((height, width, 4), dtype=np.float32)
        combined_map[:, :, 0] = normal_pixels[:, :, 0]  # R
        combined_map[:, :, 1] = normal_pixels[:, :, 1]  # G
        combined_map[:, :, 2] = material_pixels[:, :, 0]  # B
        combined_map[:, :, 3] = material_pixels[:, :, 1]  # A

        # Output path based on normal map path and preferences
        prefs = bpy.context.preferences.addons['io_scene_xplane_ext'].preferences
        no_suffix_xp_normal_map_path = os.path.splitext(xp_normal_map_path)[0]
        if no_suffix_xp_normal_map_path.endswith(prefs.suffix_normal):
            no_suffix_xp_normal_map_path = no_suffix_xp_normal_map_path[:-len(prefs.suffix_normal)]
        xp_combined_nml_map_path = no_suffix_xp_normal_map_path + prefs.suffix_combined_normal + ".png"

        #Backup the old file
        file_utils.backup_file(xp_combined_nml_map_path)

        # Create new Blender image for the combined map, assign pixel data, and save
        img_xp_combined_nml = bpy.data.images.new(name="CONVERT_BUFFER_XP_Combined_NML_Map", width=width, height=height)
        img_xp_combined_nml.pixels = combined_map.flatten()
        img_xp_combined_nml.filepath_raw = xp_combined_nml_map_path
        img_xp_combined_nml.file_format = 'PNG'
        img_xp_combined_nml.save()

        return xp_combined_nml_map_path
    except Exception as e:
        raise RuntimeError(f"Error during combination: {e}")
    finally:
        # Clean up the temporary images from Blender memory
        if img_xp_normal:
            bpy.data.images.remove(img_xp_normal)
        if img_xp_material:
            bpy.data.images.remove(img_xp_material)
        if img_xp_combined_nml:
            bpy.data.images.remove(img_xp_combined_nml)
            
        return xp_combined_nml_map_path