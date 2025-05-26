#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/24/2025
#Module:    Bake Utils
#Purpose:   Provide functions used in the auto-baking of X-Plane textures

import bpy
import os
from enum import Enum
from . import file_utils
from .. import material_config
import time
import shutil
import subprocess
import numpy as np

# This file focuses on functions used in the process of baking a high poly model to a low poly model
# Process requirements:
# - Support for multiple source objects
# - Support for multiple source materials
# - Support for a single target object and material
# - Creation of the target material and texture at a targeted resolution
# - High poly models are not modified in any way
#
# Process:
# - Create a new target material
# - For every baking channel (there will be base, normal, roughness, and metalness, lit)
#    - Get all the materials from the source objects and dedup the material list
#    - For every material in the deduped list
#      - Clear all nodes
#      - Use the .xp_material settings to set up channels property (diffuse only, normal only, roughness only, metalness only, or lit only)
#    - Create a new target texture and select it for baking
#    - Set proper bake settings
#    - Bake the texture
# - Create a new final NML material
# - Merge normal metalness and roughness textures into the final NML material
# - Save the baked base and final NML textures to disk
# - Reset the source materials
#
# Functions:
# Enums: BakeType 0 = base, 1 = normal, 2 = roughness, 3 = metalness, 4 = lit
# - get_source_materials() Returns a deduped list of all the materials from the source objects
# - config_source_material(type) Configures the given material for baking based on the type and said materials XPMaterialSettings
# - config_bake_settings(type) Sets the bake settings for the given type
# - config_target_bake_texture(type) Creates a new target texture and selects it for baking
# - bake_texture() Bakes the texture
# - save_baked_textures() Saves the baked base, nml, roughness, metalness, and lit textures to disk. Then invokes standalone exe to merge the normal, metalness, and roughness textures into the final nml texture and removes those temp files
# - reset_source_materials() Resets the source materials

#Enums
class BakeType(Enum):
    BASE = 0
    NORMAL = 1
    ROUGHNESS = 2
    METALNESS = 3
    LIT = 4

def get_source_materials():
    """
    Get's a deduped list of all the materials from the selected objects
    Returns:
        list: A list of materials from the selected objects
    """
    selected_objects = bpy.context.selected_objects

    #Define list of mats
    mats = []

    #For object, get materials, add to list
    for obj in selected_objects:
        for slot in obj.material_slots:
            if slot.material not in mats:
                mats.append(slot.material)

    return mats

def config_source_materials(type, mats):
    """
    Configures the given materials for baking based on the type and said materials XPMaterialSettings
    Args:
        type (BakeType): The type of bake to configure the materials for
        mats (list): The list of materials to configure
    """
    for mat in mats:
        #Remove all nodes from the material
        for node in mat.node_tree.nodes:
            mat.node_tree.nodes.remove(node)

        #Add a diffuse and output node
        if type != BakeType.NORMAL:
            diffuse_node = mat.node_tree.nodes.new('ShaderNodeEmission')
        else:
            diffuse_node = mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        output_node = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        

        #Add an image
        image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')

        #What we do from here is dependant on the type
        if type == BakeType.BASE:
            if mat.xp_materials.alb_texture != "":
                str_resolve_path = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(mat.xp_materials.alb_texture))
                if str_resolve_path != "":
                    image_node.image = file_utils.get_or_load_image(str_resolve_path)
                    image_node.image.colorspace_settings.name = 'sRGB'
                    mat.node_tree.links.new(image_node.outputs[0], output_node.inputs[0])
                else:
                    #Set the diffuse color to black
                    diffuse_node.inputs[0].default_value = (1, 1, 1, 1)
                    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])
            else:
                #Set the diffuse color to black
                diffuse_node.inputs[0].default_value = (1, 1, 1, 1)
                mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

        elif type == BakeType.NORMAL:
            #If there is a normal we do the node setup, otherwise we do nothing (cuz normal defaults to a sane value)
            if mat.xp_materials.normal_texture != "":
                #Now we load the normal image into the image node
                str_resolve_path = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(mat.xp_materials.normal_texture))

                if (str_resolve_path != ""):
                    image_node.image = file_utils.get_or_load_image(str_resolve_path)
                    image_node.image.colorspace_settings.name = 'Non-Color'
                    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

                    #Add a separate RGB node, combine RGB node, and normal map node. Linkage is as follows:
                    #Image to sep node
                    #R of sep to R of combine
                    #G of sep to G of combine
                    #B of combine is 1
                    #Combine to normal map
                    #Normal map to diffuse normal map input (idx 2)
                    sep_node = mat.node_tree.nodes.new('ShaderNodeSeparateRGB')
                    combine_node = mat.node_tree.nodes.new('ShaderNodeCombineRGB')
                    normal_map_node = mat.node_tree.nodes.new('ShaderNodeNormalMap')
                    mat.node_tree.links.new(image_node.outputs[0], sep_node.inputs[0])
                    mat.node_tree.links.new(sep_node.outputs[0], combine_node.inputs[0])
                    mat.node_tree.links.new(sep_node.outputs[1], combine_node.inputs[1])
                    combine_node.inputs[2].default_value = 1
                    mat.node_tree.links.new(combine_node.outputs[0], normal_map_node.inputs[1])
                    mat.node_tree.links.new(normal_map_node.outputs[0], diffuse_node.inputs[2])
                    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

        elif type == BakeType.ROUGHNESS:
            #separate normal and material textures
            if mat.xp_materials.do_separate_material_texture:
                #If there is a normal we do the node setup, otherwise we use full white (aka full roughness)
                if mat.xp_materials.material_texture != "":
                    str_resolve_path = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(mat.xp_materials.material_texture))

                    if (str_resolve_path != ""):
                        image_node.image = file_utils.get_or_load_image(str_resolve_path)
                        image_node.image.colorspace_settings.name = 'Non-Color'

                        #Add a separate RGB node. Linkage is as follows:
                        #Image to sep node
                        #G of sep node to color of diffuse node
                        sep_node = mat.node_tree.nodes.new('ShaderNodeSeparateRGB')
                        mat.node_tree.links.new(image_node.outputs[0], sep_node.inputs[0])
                        mat.node_tree.links.new(sep_node.outputs[1], output_node.inputs[0])
                    #No path found
                    else:
                        diffuse_node.inputs[0].default_value = (1, 1, 1, 1)
                        mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])
                #No path specified
                else:
                    diffuse_node.inputs[0].default_value = (1, 1, 1, 1)
                    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

            #Traditional combined normals/materials
            else:
                #If there is a normal we do the node setup, otherwise we use full black (aka full roughness. Remember, this is XP convention)
                if mat.xp_materials.normal_texture != "":
                    str_resolve_path = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(mat.xp_materials.normal_texture))

                    if (str_resolve_path != ""):
                        image_node.image = file_utils.get_or_load_image(str_resolve_path)
                        image_node.image.colorspace_settings.name = 'Non-Color'

                        mat.node_tree.links.new(image_node.outputs[1], output_node.inputs[0])
                    #No path found
                    else:
                        diffuse_node.inputs[0].default_value = (0, 0, 0, 1)
                        mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])
                #No path specified
                else:
                    diffuse_node.inputs[0].default_value = (1, 1, 1, 1)
                    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

        elif type == BakeType.METALNESS:
            #separate normal and material textures
            if mat.xp_materials.do_separate_material_texture:
                #If there is a normal we do the node setup, otherwise we do nothing
                if mat.xp_materials.material_texture != "":
                    str_resolve_path = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(mat.xp_materials.material_texture))

                    if (str_resolve_path != ""):
                        image_node.image = file_utils.get_or_load_image(str_resolve_path)
                        image_node.image.colorspace_settings.name = 'Non-Color'

                        #Add a separate RGB node. Linkage is as follows:
                        #Image to sep node
                        #R of sep node to color of diffuse node
                        sep_node = mat.node_tree.nodes.new('ShaderNodeSeparateRGB')
                        mat.node_tree.links.new(image_node.outputs[0], sep_node.inputs[0])
                        mat.node_tree.links.new(sep_node.outputs[0], output_node.inputs[0])
                    #No path found
                    else:
                        diffuse_node.inputs[0].default_value = (0, 0, 0, 1)
                        mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])
                #No path specified
                else:
                    diffuse_node.inputs[0].default_value = (0, 0, 0, 1)
                    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])
            #Traditional combined normals/materials
            else:
                if mat.xp_materials.normal_texture != "":
                    str_resolve_path = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(mat.xp_materials.normal_texture))

                    if (str_resolve_path != ""):
                        image_node.image = file_utils.get_or_load_image(str_resolve_path)
                        image_node.image.colorspace_settings.name = 'Non-Color'

                        #Add a separate RGB node. Linkage is as follows:
                        #Image to sep node
                        #B of sep node to color of diffuse node
                        sep_node = mat.node_tree.nodes.new('ShaderNodeSeparateRGB')
                        mat.node_tree.links.new(image_node.outputs[0], sep_node.inputs[0])
                        mat.node_tree.links.new(sep_node.outputs[2], output_node.inputs[0])
                    #No path found
                    else:
                        diffuse_node.inputs[0].default_value = (0, 0, 0, 1)
                        mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])
                #No path specified
                else:
                    #Set the diffuse color to black
                    diffuse_node.inputs[0].default_value = (0, 0, 0, 1)
                    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

        elif type == BakeType.LIT:
            #This is literally just diffuse but we load the lit texture instead. IF there is no lit texture, we just do black diffuse
            if mat.xp_materials.lit_texture != "":
                str_resolve_path = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(mat.xp_materials.lit_texture))
                if str_resolve_path != "":
                    image_node.image = file_utils.get_or_load_image(str_resolve_path)
                    image_node.image.colorspace_settings.name = 'sRGB'
                    mat.node_tree.links.new(image_node.outputs[0], output_node.inputs[0])
                else:
                    #Set the diffuse color to black
                    diffuse_node.inputs[0].default_value = (0, 0, 0, 1)
                    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])
            else:
                #Set the diffuse color to black
                diffuse_node.inputs[0].default_value = (0, 0, 0, 1)
                mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])

def config_bake_settings(type):
    """
    Configures the bake settings for the given type
    Args:
        type (BakeType): The type of bake to configure the settings for
    """
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.use_clear = False
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.engine = 'CYCLES'

    #Base lit roughness and metalness all just bake from diffuse channel to diffuse
    if type == BakeType.BASE or type == BakeType.LIT or type == BakeType.ROUGHNESS or type == BakeType.METALNESS:
        bpy.context.scene.cycles.bake_type = 'EMIT'
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    elif type == BakeType.NORMAL:
        bpy.context.scene.cycles.bake_type = 'NORMAL'
        bpy.context.scene.render.bake.normal_space = 'TANGENT'
        bpy.context.scene.render.bake.normal_r = 'POS_X'
        bpy.context.scene.render.bake.normal_g = 'POS_Y'
        bpy.context.scene.render.bake.normal_b = 'POS_Z'
    
def config_target_bake_texture(target_obj, type, resolution):
    """
    Creates a new target texture and selects it for baking
    Args:
        target_obj (bpy.types.Object): The target object to bake to
        type (BakeType): The type of bake to configure the texture for
        resolution (int): The resolution of the texture to create
    """
    #Define a name for the texture based on the name
    create_name = ""
    if type == BakeType.BASE:
        create_name = "BAKE_BUFFER_Base"
    elif type == BakeType.NORMAL:
        create_name = "BAKE_BUFFER_Normal"
    elif type == BakeType.ROUGHNESS:
        create_name = "BAKE_BUFFER_Roughness"
    elif type == BakeType.METALNESS:
        create_name = "BAKE_BUFFER_Metalness"
    elif type == BakeType.LIT:
        create_name = "BAKE_BUFFER_Lit"

    #If there is already a texture, use it (this allows us to sequentially bake textures for different textures that use the same sheet, without post bake merging)
    new_image = None
    if bpy.data.images.get(create_name):
        new_image = bpy.data.images.get(create_name)
        
        #Resize the image if it isn't the target size already
        if new_image.size[0] != int(resolution) or new_image.size[1] != int(resolution):
            new_image.scale(int(resolution), int(resolution))
    else:
        #Create a new image
        new_image = bpy.data.images.new(name=create_name, width=int(resolution), height=int(resolution), alpha=True)

    #Set color space settings
    if type == BakeType.ROUGHNESS or type == BakeType.METALNESS:
        new_image.colorspace_settings.name = 'Non-Color'
    else:
        new_image.colorspace_settings.name = 'sRGB'

    #Check if the target object has a material, if not, create one
    mat = None
    if len(target_obj.data.materials) > 0:
        mat = target_obj.data.materials[0]
    else:
        mat = bpy.data.materials.new(name="BAKE_BUFFER_MAT")
        mat.use_nodes = True
        target_obj.data.materials.append(mat)

    #Clear all the nodes of the current material
    for node in mat.node_tree.nodes:
        mat.node_tree.nodes.remove(node)

    #Add output, diffuse, and image nodes. Linkage as follows:
    #Image to diffuss
    #Diffuse to output
    diffuse_node = mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    output_node = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    mat.node_tree.links.new(image_node.outputs[0], diffuse_node.inputs[0])
    mat.node_tree.links.new(diffuse_node.outputs[0], output_node.inputs[0])
    image_node.image = new_image

    #Set the active node to the image node (so this is the one that gets baked to)
    mat.node_tree.nodes.active = image_node
    
def save_baked_textures(target_obj):
    """
    Saves the baked base and lit textures to the disk, and merges the normal, metalness, and roughness textures into the final nml texture which is also saved to the disk.
    Args:
        target_obj (bpy.types.Object): The target object to save the textures for
    Notes:
        Texture names are <collectio_name>_LOD01_<suffix>.png, where suffix is nothing for base, _NML for normal, _LIT for lit
        TODO: Add Blender plugin preferences to change conventions for suffixes. I use NML because of a mistake and I'm grandfathered in. Most devs use _NRM.
    """
    #Get the base, combined normal, and lit textures
    base_image = bpy.data.images.get("BAKE_BUFFER_Base")
    nml_image = bpy.data.images.get("BAKE_BUFFER_Normal")
    roughness_image = bpy.data.images.get("BAKE_BUFFER_Roughness")
    metalness_image = bpy.data.images.get("BAKE_BUFFER_Metalness")
    lit_image = bpy.data.images.get("BAKE_BUFFER_Lit")

    #Resize all the images to their current size / bpy.context.scene.xp_ext.low_poly_bake_ss_factor
    base_image.scale(int(base_image.size[0] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor), int(base_image.size[1] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor))
    nml_image.scale(int(nml_image.size[0] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor), int(nml_image.size[1] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor))
    roughness_image.scale(int(roughness_image.size[0] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor), int(roughness_image.size[1] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor))
    metalness_image.scale(int(metalness_image.size[0] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor), int(metalness_image.size[1] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor))
    lit_image.scale(int(lit_image.size[0] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor), int(lit_image.size[1] / bpy.context.scene.xp_ext.low_poly_bake_ss_factor))

    #Get the file path. This is the file path of the current blend file + the name of the collection of the target object + _low_poly_<type>.png
    file_path = bpy.data.filepath
    
    #Get the collection the current object is in
    parent_collections = None
    try:
        parent_collections = target_obj.users_collection
    except:
        print("Parent collection not found for object " + target_obj.name + ". What!?")
        return

    #Get the width and height of the nml
    width = nml_image.size[0]
    height = nml_image.size[1]

    #Iterate through every pixel in the normal image. Set it's blue to the metalness value, and it's alpha to roughness * -1 + 255

    # Convert Blender images to numpy arrays
    nml_pixels = np.array(nml_image.pixels[:]).reshape((height, width, 4))
    metalness_pixels = np.array(metalness_image.pixels[:]).reshape((height, width, 4))
    roughness_pixels = np.array(roughness_image.pixels[:]).reshape((height, width, 4))

    # Create an empty array for the final pixels
    final_pixels = np.zeros((height, width, 4), dtype=np.float32)

    # Assign the pixel values using array slicing
    final_pixels[:, :, 0] = nml_pixels[:, :, 0]  # Red channel from nml_image
    final_pixels[:, :, 1] = nml_pixels[:, :, 1]  # Green channel from nml_image
    final_pixels[:, :, 2] = metalness_pixels[:, :, 2]  # Blue channel from metalness_image
    final_pixels[:, :, 3] = roughness_pixels[:, :, 2]  # Alpha channel from roughness_image

    # Flatten the final_pixels array to match the original shape
    final_pixels = final_pixels.flatten()

    # Assign the final pixels back to the nml_image
    nml_image.pixels = final_pixels.tolist()
    
    #Define the output paths
    base_output_path = ""
    nml_output_path = ""
    lit_output_path = ""
    adjusted_name = parent_collections[0].name
    if adjusted_name.endswith("_LOD01"):
        adjusted_name = adjusted_name[:-6]
    base_output_path = os.path.join(os.path.dirname(file_path), adjusted_name + "_LOD01.png")
    nml_output_path = os.path.join(os.path.dirname(file_path), adjusted_name + "_LOD01_NML.png")
    lit_output_path = os.path.join(os.path.dirname(file_path), adjusted_name + "_LOD01_LIT.png")

    #Save the images
    print("Saving base image to " + base_output_path)
    print("Saving nml image to " + nml_output_path)
    print("Saving lit image to " + lit_output_path)
    base_image.filepath_raw = base_output_path
    base_image.file_format = 'PNG'
    base_image.save()
    nml_image.filepath_raw = nml_output_path
    nml_image.file_format = 'PNG'
    nml_image.save()
    lit_image.filepath_raw = lit_output_path
    lit_image.file_format = 'PNG'
    lit_image.save()

    #Remove the temp images from Blender
    bpy.data.images.remove(base_image)
    bpy.data.images.remove(nml_image)
    bpy.data.images.remove(lit_image)
    bpy.data.images.remove(roughness_image)
    bpy.data.images.remove(metalness_image)

def reset_source_materials(mats):
    """
    Resets the source materials to their original state by calling the update_nodes function, which is what's called when the user presses the button in the panel
    Args:
        mats (list): The list of materials to reset
    """
    for mat in mats:
        material_config.update_nodes(mat)

def config_target_object_with_new_textures(target_obj):
    """
    Configures the target object with the new textures by setting the material properties and updating the nodes. Use after baking is complete
    Args:
        target_obj (bpy.types.Object): The target object to configure
    """

    #Get the material
    mat = None
    if len(target_obj.data.materials) > 0:
        mat = target_obj.data.materials[0]

    #Get the collection the current object is in
    parent_collections = None
    try:
        parent_collections = target_obj.users_collection
    except:
        print("Parent collection not found for object " + target_obj.name + ". What!?")
        return

    #Set the material properties
    mat.xp_materials.alb_texture = parent_collections[0].name + "_LOD01.png"
    mat.xp_materials.normal_texture = parent_collections[0].name + "_LOD01_NML.png"
    mat.xp_materials.lit_texture = parent_collections[0].name + "_LOD01_LIT.png"

    #Set the active material, then call the update material nodes operator
    material_config.update_nodes(mat)
