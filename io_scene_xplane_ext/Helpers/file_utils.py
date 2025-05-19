#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/26/2024
#Module:    File Utils
#Purpose:   Provide a single file containing functions for files

import os
import bpy

#Gets an absolute path out of a path that is relative to the blender file.
def rel_to_abs(in_path):
    """Gets an absolute path out of a path that is relative to the blender file."""

    str_out_path = ""

    if in_path != "":
            if in_path.startswith("//"):
                in_path = in_path[2:]

            str_out_path = os.path.join(os.path.dirname(bpy.data.filepath), in_path)

    return str_out_path

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
    :param image_path: Path to the image file.
    :return: Handle to the image.
    """
    # Check if the image is already loaded
    existing_image = bpy.data.images.get(image_path)
    if existing_image:
        # Reload the image if requested
        if do_reload:
            existing_image.reload()
        return existing_image

    # Load the image
    new_image = bpy.data.images.load(image_path)
    return new_image                 