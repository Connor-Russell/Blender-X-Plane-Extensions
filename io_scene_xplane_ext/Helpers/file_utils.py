
import os
import bpy

#Utility file functions
def resolve_relative_path(in_path, check_back_first=True):
    """Resolves a path (namely a texture path) that is relative to the blender file to an absolute path. Returns "" if the file is not found."""

    str_out_path = ""

    if in_path != "":
            if in_path.startswith("//"):
                in_path = in_path[2:]

            back_one = os.path.join(os.path.join(os.path.dirname(bpy.data.filepath), ".."), in_path)
            here = os.path.join(os.path.dirname(bpy.data.filepath), in_path)

            if check_back_first:
                if os.path.exists(back_one):
                    str_out_path = back_one
                elif os.path.exists(here):
                    str_out_path = here
                else:
                    str_out_path = ""
            
            else:
                if os.path.exists(here):
                    str_out_path = here
                elif os.path.exists(back_one):
                    str_out_path = back_one
                else:
                    str_out_path = ""

    return str_out_path

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