#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Props
#Purpose:   Provide a single file containing functions to configure materials for X-Plane in Blender

import bpy # type: ignore
from .Helpers import file_utils

#Function to update settings when a property is updated:
def update_settings(xp_material_props, selected_object):
    #Now we will update the settings.
            #Set backface culling to TRUE - .use_backface_culling
            #Set alpha blending to ALPHA_CLIP or OPAQUE - .blend_method
            #Set XP draped mode based on the draped property - .xplane.draped
            #Set XP alpha mode based on the blend_alpha property. Alpha Cutoff ("off") or Alpha Blend ("on") - .xplane.blend_v1000
            #Set XP hard mode based on the hard property ("none" or "concrete") - .xplane.surfaceType
                #If hard is true, set "xplane.deck" to true, otherwise set it to false
            #Set XP polygon offset based on the polygon_offset property - xplane.poly_os
    
    #Force a UI update
    bpy.context.view_layer.update()

    material = bpy.context.material

    #Set backface culling to TRUE
    material.use_backface_culling = True

    #Set alpha blending to ALPHA_CLIP or OPAQUE
    if xp_material_props.blend_alpha:
        material.blend_method = 'BLEND'
    else:
        xp_material_props.blend_method = 'CLIP'
        material.xplane.blendRatio = xp_material_props.blend_cutoff

    #Set XP draped mode based on the draped property
    if xp_material_props.draped:
        material.xplane.draped = True
    else:
        material.xplane.draped = False

    #Set XP alpha mode based on the blend_alpha property. Alpha Cutoff ("off") or Alpha Blend ("on")
    if xp_material_props.blend_alpha:
        material.xplane.blend_v1000 = 'on'
    else:
        material.xplane.blend_v1000 = 'off'

    #Set XP hard mode based on the hard property ("none" or "concrete")
    if xp_material_props.hard:
        material.xplane.surfaceType = 'concrete'
        material.xplane.deck = True
    else:
        material.xplane.surfaceType = 'none'
        material.xplane.deck = False

    #Set shadow mode
    material.xplane.shadow_local = xp_material_props.cast_shadow

    #Set XP polygon offset based on the polygon_offset property
    material.xplane.poly_os = xp_material_props.polygon_offset

#Function to update the nodes of a material
def update_nodes(material):
    #Check to make sure teh file is saved, otherwise exit and warn the user in the status bar
        if bpy.data.filepath == "":
            return
        
        #Define variables to hold the imagese
        image_alb = None
        image_nml = None
        image_lit = None
        str_image_alb = ""
        str_image_nml = ""
        str_image_lit = ""

        xp_material_props = material.xp_materials

        #Resolve paths. They are relative to the blender file or relative to one folder back. We assume one folder back first. If the file is not found, we assume it is in the same folder as the blender file.
        str_image_alb = file_utils.resolve_relative_path(xp_material_props.alb_texture, True)
        str_image_nml = file_utils.resolve_relative_path(xp_material_props.normal_texture, True)
        str_image_lit = file_utils.resolve_relative_path(xp_material_props.lit_texture, True)
        print(str_image_alb)
        print(str_image_nml)
        print(str_image_lit)
        
        #Load the images that exist
        if str_image_alb != "":
            image_alb = file_utils.get_or_load_image(str_image_alb)
        if str_image_nml != "":
            image_nml = file_utils.get_or_load_image(str_image_nml)
        if str_image_lit != "":
            image_lit = file_utils.get_or_load_image(str_image_lit)

        #Remove all nodes from the material
        for node in material.node_tree.nodes:
            material.node_tree.nodes.remove(node)

        #Now we need to add the following nodes:
            # Output
            # Principled BSDF
            # For albedo (if present):
                # Image texture
                # Add (for alpha, we need this because emissive is additive)
                # Clamp (0-1 for alpha). This takes from the add, connects to the alpha
            # For normal (if present):
                # Image texture
                # Seperate RGB
                # Combined RGB
                # Normal Map
                # Invert
            # For lit (if present):
                # Image texture

        #Set up the universal nodes            
        node_output = material.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
        node_output.location = (0, 0)
        node_principled = material.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
        node_principled.location = (-500, 0)
        material.node_tree.links.new(node_principled.outputs[0], node_output.inputs[0])

        #This is for the additive alpha between the alb and the lit, since both need it, it needs to be defined in advance
        node_add = None
        node_clamp = None

        #Set up alb nodes
        if image_alb != None:
            node_alb = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_add = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_clamp = material.node_tree.nodes.new(type="ShaderNodeClamp")
            node_alb.location = (-1600, 0)
            node_add.location = (-1250, 0)
            node_clamp.location = (-1000, 0)
            node_alb.image = image_alb
            node_add.operation = 'ADD'
            node_add.inputs[1].default_value = 0
            node_add.inputs[0].default_value = 0
            node_clamp.inputs[1].default_value = 0
            node_clamp.inputs[2].default_value = 1

            #Connect the nodes. Color to base color, alpha to add, add to principled alpha
            material.node_tree.links.new(node_alb.outputs[0], node_principled.inputs[0])
            material.node_tree.links.new(node_alb.outputs[1], node_add.inputs[0])
            material.node_tree.links.new(node_add.outputs[0], node_clamp.inputs[0])
            material.node_tree.links.new(node_clamp.outputs[0], node_principled.inputs[21])

        #Set up nml nodes
        if image_nml != None:
            node_nml = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_seperate_rgb = material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
            node_combine_rgb = material.node_tree.nodes.new(type="ShaderNodeCombineRGB")
            node_normal_map = material.node_tree.nodes.new(type="ShaderNodeNormalMap")
            node_rough_invert = material.node_tree.nodes.new(type="ShaderNodeInvert")
            node_nml.location = (-1600, -250)
            node_seperate_rgb.location = (-1250, -250)
            node_combine_rgb.location = (-1000, -250)
            node_normal_map.location = (-750, -250)
            node_rough_invert.location = (-1250, -375)
            node_nml.image = image_nml
            image_nml.colorspace_settings.name = 'Non-Color'

            #Now connections, this is funky cuz XP doesn't use conventional formats. We need to map channels as follows:
                #NML R to seperate R
                #NML G to seperate G
                #NML B to principled metalness
                #NML alpha to invert
                #Seperate R to combine R
                #Seperate G to combine G
                #The combine B needs to be 1
                #Combine to normal map
                #Normal map to principled normal
                #Invert to principled roughness
            material.node_tree.links.new(node_nml.outputs[0], node_seperate_rgb.inputs[0])
            material.node_tree.links.new(node_seperate_rgb.outputs[0], node_combine_rgb.inputs[0])
            material.node_tree.links.new(node_seperate_rgb.outputs[1], node_combine_rgb.inputs[1])
            material.node_tree.links.new(node_seperate_rgb.outputs[2], node_principled.inputs[6])
            node_combine_rgb.inputs[2].default_value = 1
            material.node_tree.links.new(node_combine_rgb.outputs[0], node_normal_map.inputs[1])
            material.node_tree.links.new(node_normal_map.outputs[0], node_principled.inputs[22])
            material.node_tree.links.new(node_nml.outputs[1], node_rough_invert.inputs[1])
            material.node_tree.links.new(node_rough_invert.outputs[0], node_principled.inputs[9])

        #Set up lit nodes
        if image_lit != None:
            node_lit = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_lit.location = (-1600, -500)
            node_lit.image = image_lit

            #Connect the color to the principled emission
            material.node_tree.links.new(node_lit.outputs[0], node_principled.inputs[19])

            #If there is an alb, connect the alpha to it's add so it can impact the alpha
            if node_add != None:
                material.node_tree.links.new(node_lit.outputs[1], node_add.inputs[1])

#Function to attempt to restore the old properties
def restore_old_plugin_props(in_material, in_new_props):
    try:
        in_new_props.alb_texture = in_material.alb_texture
        in_new_props.normal_texture = in_material.normal_texture
        in_new_props.lit_texture = in_material.lit_texture
        in_new_props.draped = in_material.draped
        in_new_props.hard = in_material.hard
        in_new_props.blend_alpha = in_material.blend_alpha
        in_new_props.blend_cutoff = in_material.blend_cutoff
        in_new_props.polygon_offset = in_material.polygon_offset
        in_new_props.cast_shadow = in_material.cast_shadow
        in_new_props.layer_group = in_material.layer_group
        in_new_props.layer_group_offset = in_material.layer_group_offset

        in_material.alb_texture = ""
        in_material.normal_texture = ""
        in_material.lit_texture = ""
        in_material.draped = False
        in_material.hard = False
        in_material.blend_alpha = False
        in_material.blend_cutoff = 0
        in_material.polygon_offset = 0
        in_material.cast_shadow = True
        in_material.layer_group = ""
        in_material.layer_group_offset = 0
    except:
        pass
