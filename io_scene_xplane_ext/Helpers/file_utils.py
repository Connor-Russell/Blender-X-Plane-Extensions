#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/26/2024
#Module:    File Utils
#Purpose:   Provide a single file containing functions for files

import os
import bpy
from . import log_utils

#Gets an absolute path out of a path that is relative to the blender file.
def rel_to_abs(in_path):
    """
    Gets an absolute path out of a path that is relative to the blender file.

    Args:
        in_path (str): The relative path to convert.
    Returns:
        str: The absolute path.    
    """

    str_out_path = ""

    if in_path != "":
            if in_path.startswith("//"):
                in_path = in_path[2:]

            str_out_path = os.path.join(os.path.dirname(bpy.data.filepath), in_path)

    return str_out_path

def abs_to_rel(in_path):
    """
    Converts an absolute path to a relative path based on the current Blender file location.

    Args:
        in_path (str): The absolute path to convert.
    Returns:
        str: The relative path.
    """

    if in_path == "":
        return ""
    
    try:

        if in_path.startswith("//"):
            in_path = in_path[2:]

        if bpy.data.filepath == "":
            return in_path

        return os.path.relpath(in_path, os.path.dirname(bpy.data.filepath))
    except:
        # If there's an error, return the original path
        return in_path

def check_for_dds_or_png(image_path):
    """
    Checks if the given image path exists, or if a corresponding .dds or .png version exists.

    This function attempts to find a valid file path for an image by checking the provided path,
    then checking for a .dds or .png version of the file (by swapping the extension).
    The search order is:
        1. The original image_path.
        2. The same path with a .png extension.
        3. The same path with a .dds extension.

    Args:
        image_path (str): The file path to check.

    Returns:
        str: The path to the existing image file, or an empty string if none are found.
    """

    path_as_dds = os.path.splitext(image_path)[0] + ".dds"
    path_as_png = os.path.splitext(image_path)[0] + ".png"

    if os.path.exists(image_path):
        return image_path
    elif os.path.exists(path_as_png):
        return path_as_png
    elif os.path.exists(path_as_dds):
        return path_as_dds
    
    return ""
        
def get_or_load_image(image_path, do_reload=False):
    """
    Get an existing image or load a new one if not already loaded.
    Args:
        image_path (str): The file path to the image.
        do_reload (bool): Whether to reload the image if it already exists.
    Returns:
        bpy.types.Image: The loaded or existing image.
    """
    #Get our prefs to determine our reload behavior
    addon_prefs = bpy.context.preferences.addons["io_scene_xplane_ext"].preferences

    #Iterate through the existing images, get their paths, turn them to absolute, and check if they match the given path
    if not addon_prefs.always_fully_reload_images:
        try:
            for image in bpy.data.images:
                if image.filepath == "":
                    continue
                abs_image_path = rel_to_abs(image.filepath)
                if abs_image_path == image_path:
                    # If the image is already loaded and we don't need to reload, return it
                    if not do_reload:
                        return image
                    
                    # If we do need to reload, reload the image
                    image.reload()
                    return image
        except Exception as e:
            log_utils.warning(f"Error checking existing images when trying to find image {image_path}: {e}")

    # Load the image
    new_image = bpy.data.images.load(image_path)
    return new_image                 