#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/26/2024
#Module:    file_utils.py
#Purpose:   Provide functions to aid in handling file paths, loading images, and backing up files.

import os
import bpy
import sys
from . import log_utils
import datetime
import time

def sanitize_path(path):
    """
    Sanitizes a file path by removing invalid characters and replacing them with dashes. Also normalizes slashes.

    Args:
        path (str): The file path to sanitize.
    Returns:
        str: The sanitized file path.
    """
    if not path:
        return ""

    path = path.replace("\\", os.sep)  # Normalize slashes    
    path = path.replace("/", os.sep)  # Normalize slashes

    # Replace invalid characters with dashes, OS-specific
    if sys.platform.startswith('win'):
        invalid_chars = '<>"|?*\n\r\t\0'

    sanitized = []
    prev_char = ''
    idx = 0
    for char in path:
        if char in invalid_chars:
            char = "-"

        # Disallow : on anything but the second character in a Windows drive letter (e.g., C:\ or C:/)
        if char == ':':
            # Only allow if at index 1, first char is alpha, and next char is a slash or backslash
            if not sys.platform.startswith('win') or not (idx == 1 and path[0].isalpha() and len(path) > 2 and path[2] in ('\\', '/')):
                char = "-"
        
        # Avoid duplicate separators
        if prev_char == os.sep and char == os.sep:
            idx += 1
            continue
        sanitized.append(char)
        prev_char = char
        idx += 1

    return ''.join(sanitized)

def remove_blender_prefix(path):
    """
    Removes the Blender relative path prefix (//) from a given path if it exists.

    Args:
        path (str): The file path to process.
    Returns:
        str: The path without the Blender prefix.
    """

    if path.startswith("//"):
        return path[2:]
    return path

def _is_relative(in_path):
    """
    Checks if a given path is relative to the current Blender file.

    Args:
        in_path (str): The path to check.
    """

    # Remove Blender relative prefix if present
    if in_path.startswith("//"):
        return True

    # Use os.path.isabs for platform correctness
    return not os.path.isabs(in_path)

def to_absolute(in_path):
    """
    Gets an absolute path out of a path that is relative to the blender file.

    Args:
        in_path (str): The relative path to convert.
    Returns:
        str: The absolute path.    
    """

    if in_path == "":
        return ""

    #We always sanitize the path first
    in_path = remove_blender_prefix(in_path)
    in_path = sanitize_path(in_path)

    if not _is_relative(in_path) or bpy.data.filepath == "":
        return in_path
    
    in_path = os.path.normpath(os.path.join(os.path.dirname(bpy.data.filepath), in_path))

    print(f"Resolved absolute path: {in_path}")

    return in_path

def to_relative(in_path, include_blend_prefix=False):
    """
    Converts an absolute path to a relative path based on the current Blender file location.

    Args:
        in_path (str): The absolute path to convert.
    Returns:
        str: The relative path.
    """

    if in_path == "":
        return ""

    #We always sanitize the path first
    in_path = remove_blender_prefix(in_path)
    in_path = sanitize_path(in_path)

    if _is_relative(in_path):
        #If we need the blender prefix and it's not there, add it
        if include_blend_prefix and not in_path.startswith("//"):
            in_path = "//" + in_path
        return in_path
    
    #Now that we know it is absolute, we need to make sure we have a blender file path, otherwise we just return ourselves
    if bpy.data.filepath == "":
        return in_path
    
    #Otherwise, we need to resolve it. So, since this is an absolute path, we just need to do os.path.relpath
    in_path = os.path.relpath(in_path, os.path.dirname(bpy.data.filepath))

    #Add the blender prefix if needed
    if include_blend_prefix and not in_path.startswith("//"):
        in_path = "//" + in_path

    print(f"Resolved relative path: {in_path}")

    return in_path

def resolve_file_export_path(in_path, col_name, extension):
    """
    Resolves the export path for a given collection name and extension. Always relative to the .blend file.

    Args:
        in_path (str): The base path to use for export (can be empty, or just a dir, or dir and file name).
        col_name (str): The name of the collection (use as the name if in_path doesn't contain a file name).
        extension (str): The file extension to use (e.g., ".fac", ".lin", ".pol").
    """
    export_path = ""

    #First off, sanitize all paths
    in_path = remove_blender_prefix(in_path)    #This is the only path that'd have a blender prefix
    in_path = sanitize_path(in_path)
    col_name = sanitize_path(col_name)
    extension = sanitize_path(extension)

    #First we get the entered user path, combining the specified name or relative dir and the collection name and extension
    if in_path != "":
            #Check if it ends in just a slash, if so we'll treat the name as a relative directory and still use the collection name as the file name
            if in_path.endswith(("/", "\\")):
                export_path = os.path.join(in_path, col_name + extension)
            else:
                export_path = in_path + extension
    else:
        export_path = col_name + extension

    #Remove the duplicate extension
    if export_path.lower().endswith(extension + extension):
        export_path = export_path[:-len(extension)]

    #Now we have the user specified path. If this is relative, we need to join it with the blender file path
    if _is_relative(export_path):
        export_path = os.path.join(os.path.dirname(bpy.data.filepath), export_path)

    return os.path.normpath(export_path)

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
        
def get_or_load_image(image_path, do_reload=False, copy_append_name=""):
    """
    Get an existing image or load a new one if not already loaded.
    Args:
        image_path (str): The file path to the image.
        do_reload (bool): Whether to reload the image if it already exists.
        copy_append_name (str): Use to specify a string to append if to identify this as a unique copy of this image
    Returns:
        bpy.types.Image: The loaded or existing image.
    """
    #Get our prefs to determine our reload behavior
    addon_prefs = bpy.context.preferences.addons["io_scene_xplane_ext"].preferences

    #Resolve the image path
    image_path = to_absolute(image_path)

    #Get the image extension so that we can append it to the name if needed
    image_extension = os.path.splitext(image_path)[1]
    image_base_name = os.path.splitext(os.path.basename(image_path))[0]
    image_appended_name = image_base_name + copy_append_name + image_extension
    log_utils.info(f"Loading image {image_appended_name} from path {image_path}")

    #Iterate through the existing images, get their paths, turn them to absolute, and check if they match the given path
    if not addon_prefs.always_fully_reload_images:
        try:
            for image in bpy.data.images:
                if image.filepath == "":
                    continue
                if image.filepath == image_path and (copy_append_name == "" or image.name.startswith(image_appended_name)):
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
    new_image.name = image_appended_name
    return new_image                 

def backup_file(in_file_path):
    """
    Generates a backup file name by appending a timestamp to the original file name.

    Args:
        in_file_path (str): The original file path.

    Returns:
        str: The backup file path with a timestamp.
    """

    #If the file doesn't exist, we're done!
    if os.path.isfile(in_file_path) == False:
        return
    
    #We only backup if the preferences say to, so check that
    if not bpy.context.preferences.addons['io_scene_xplane_ext'].preferences.do_backup_on_overwrite:
        return

    #Get the directory and base name
    dir_name = os.path.dirname(in_file_path)
    base_name = os.path.basename(in_file_path)
    name, ext = os.path.splitext(base_name)

    #Get the file modified time, then create a timestamp from it. If we fail to get modified time, just use the current time.
    timestamp = ""
    try:
        mtime = os.path.getmtime(in_file_path)
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(mtime))
    except:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    #Now we get to try to create the full name. HOWEVER, what if two files have the same modified time at the same sec and therefore had the same name? Ok yeah idk how that would happen other than someone manually named the file that but let's be safe
    #If a file exists with this name, we'll append _iter to the name, incrementing iter until we find a name that doesn't exist

    iter = 0
    backup_file_name = ""
    while True:
        if iter == 0:
            backup_file_name = f"{name}_backup_{timestamp}{ext}"
        else:
            backup_file_name = f"{name}_backup_{timestamp}_{iter}{ext}"
        backup_file_path = os.path.join(dir_name, backup_file_name)
        if not os.path.exists(backup_file_path):
            break
        iter += 1

    #Try to rename the file
    try:
        os.rename(in_file_path, backup_file_path)
        log_utils.info(f"Backed up file {in_file_path} to {backup_file_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to back up file {in_file_path} to {backup_file_path}: {e}")
