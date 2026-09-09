# This file provides a single function to get the a color grid for a given set of dimensions
# If a color grid of these dimensions already exists, it will be reused.

import bpy

def get_color_grid_image(width, height):
    image_name = f"_XP_EXT_COLOGRID_{width}x{height}"
    
    # Check if the image already exists
    if image_name in bpy.data.images:
        return bpy.data.images[image_name]

    # Create a generated Color Grid image
    image = bpy.ops.image.new(
        name=image_name,
        width=width,
        height=height,
        alpha=True,
        generated_type='COLOR_GRID',
        float=False,
    )

    return bpy.data.images.get(image_name)

def get_bake_image(width, height, mat_name):
    image_name = f"{mat_name}_BAKE"
    
    # Check if the image already exists
    if image_name in bpy.data.images:
        return bpy.data.images[image_name]

    # Create a new image for baking
    image = bpy.ops.image.new(
        name=image_name,
        width=width,
        height=height,
        alpha=True,
        generated_type='BLANK',
        float=False,
    )

    return bpy.data.images.get(image_name)
