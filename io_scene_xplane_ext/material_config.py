#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Props
#Purpose:   Provide a single file containing functions to configure materials for X-Plane in Blender

import bpy # type: ignore
from .Helpers import file_utils
from .Helpers import decal_utils
from .Helpers import log_utils

def operator_wrapped_update_settings(self = None, context = None):
    if bpy.context.active_object == None:
        return
    
    if context != None and context.area != None:
        #Force a UI update
        context.area.tag_redraw()

    #This function is called when the user updates a property in the UI. It will call the update_settings function to update the material settings.
    #Get the material from the context
    in_material = bpy.context.active_object.active_material

    #Check to make sure the material is not None
    if in_material == None:
        return

    #Call the update_settings function to update the material settings
    update_settings(in_material)

def operator_wrapped_update_nodes(self = None, context = None):
    if bpy.context.active_object == None:
        return

    if context != None and context.area != None:
        #Force a UI update
        context.area.tag_redraw()
    
    #This function is called when the user updates a property in the UI. It will call the update_nodes function to update the material nodes.
    #Get the material from the context
    in_material = bpy.context.active_object.active_material

    #Check to make sure the material is not None
    if in_material == None:
        return

    #Call the update_nodes function to update the material nodes
    update_nodes(in_material)

#Function to update the X-Plane Collection material settings:
def update_xplane_collection_settings(col):
    #Define flag
    updated = False

    #Get all the objects in the collection
    for obj in col.objects:
        mat = obj.active_material

        if mat != None:
            xp_props = mat.xp_materials

            #Check for textures
            if xp_props.alb_texture != "":

                #If we haven't updated yet, update
                if not updated:
                    
                    if xp_props.lit_texture != "":
                        if xp_props.brightness > 0:
                            col.xplane.layer.luminance_override = True
                            col.xplane.layer.luminance = int(xp_props.brightness)
                        else:
                            col.xplane.layer.luminance_override = False
                            col.xplane.layer.luminance = 1000

                        if xp_props.normal_texture != "":
                            col.xplane.layer.normal_metalness_draped = xp_props.normal_texture != ""
                    else:
                        col.xplane.layer.luminance_override = False
                        col.xplane.layer.luminance = 1000

                    col.xplane.layer.texture = xp_props.alb_texture
                    col.xplane.layer.texture_lit = xp_props.lit_texture
                    if xp_props.do_separate_material_texture:
                        col.xplane.layer.texture_map_normal = xp_props.normal_texture
                        col.xplane.layer.texture_map_material_gloss = xp_props.material_texture
                    else:
                        col.xplane.layer.texture_normal = xp_props.normal_texture
                    col.xplane.layer.normal_metalness = xp_props.normal_texture != ""

                    if xp_props.draped:
                        col.xplane.layer.texture_draped = xp_props.alb_texture
                        col.xplane.layer.texture_draped_normal = xp_props.normal_texture
                        col.xplane.layer.normal_metalness_draped = xp_props.normal_texture != ""
                        try:
                            col.xplane.layer.layer_group_draped = xp_props.layer_group.lower()
                            col.xplane.layer.layer_group_offset_draped = xp_props.layer_group_offset
                        except:
                            if xp_props.layer_group == 'BLENDED':
                                log_utils.warn("The 'Blended' layer group is only supported by custom XP2B exporters. There is a pending pull request, so tell your Local X-Plane Representative to merge it ;)")
                            pass
                    else:
                        col.xplane.layer.texture_draped = ""
                        col.xplane.layer.texture_draped_normal = ""
                        col.xplane.layer.normal_metalness_draped = xp_props.normal_texture != ""

                    #Now we need to set the decal properties
                    #Reset decal properties
                    col.xplane.layer.file_decal1 = ""
                    col.xplane.layer.file_decal2 = ""
                    col.xplane.layer.file_draped_decal1 = ""
                    col.xplane.layer.file_draped_decal2 = ""
                    col.xplane.layer.file_normal_decal1 = ""
                    col.xplane.layer.file_normal_decal2 = ""
                    col.xplane.layer.file_draped_normal_decal1 = ""
                    col.xplane.layer.file_draped_normal_decal2 = ""
                    col.xplane.layer.texture_modulator = ""
                    col.xplane.layer.texture_draped_modulator = ""

                    col.xplane.layer.texture_modulator = xp_props.decal_modulator

                    if xp_props.draped:
                        col.xplane.layer.texture_draped_modulator = xp_props.decal_modulator

                    if len(xp_props.decals) == 4:
                        decal_utils.set_xp_decal_prop(col, mat, xp_props.decals[0], 1)
                        decal_utils.set_xp_decal_prop(col, mat, xp_props.decals[1], 2)
                        decal_utils.set_xp_decal_prop(col, mat, xp_props.decals[2], 1)
                        decal_utils.set_xp_decal_prop(col, mat, xp_props.decals[3], 2)
                    else:
                        #Set the correct number of decals
                        while len(xp_props.decals) < 4:
                            #Add a new decal
                            xp_props.decals.add()
                        while len(xp_props.decals) > 4:
                            #Remove the last decal
                            xp_props.decals.remove(xp_props.decals.count - 1)

                    updated = True

                #If we have updated, but this one is draped, update with this one. Then we can skip the rest of the objects in this collection
                if xp_props.draped:
                    col.xplane.layer.texture = xp_props.alb_texture
                    col.xplane.layer.texture_lit = xp_props.lit_texture
                    col.xplane.layer.texture_normal = xp_props.normal_texture
                    col.xplane.layer.texture_draped = xp_props.alb_texture
                    col.xplane.layer.texture_draped_normal = xp_props.normal_texture
                    col.xplane.layer.normal_metalness = xp_props.normal_texture != ""
                    col.xplane.layer.normal_metalness_draped = xp_props.normal_texture != ""

                    col.xplane.layer.layer_group_draped = xp_props.layer_group.lower()
                    col.xplane.layer.layer_group_offset_draped = xp_props.layer_group_offset

                    col.xplane.layer.texture_draped_modulator = xp_props.decal_modulator

                    if len(xp_props.decals) == 4:
                        decal_utils.set_xp_decal_prop(col, mat, xp_props.decals[0], 1)
                        decal_utils.set_xp_decal_prop(col, mat, xp_props.decals[1], 2)
                        decal_utils.set_xp_decal_prop(col, mat, xp_props.decals[2], 1)
                        decal_utils.set_xp_decal_prop(col, mat, xp_props.decals[3], 2)
                    else:
                        #Set the correct number of decals
                        while len(xp_props.decals) < 4:
                            #Add a new decal
                            xp_props.decals.add()
                        while len(xp_props.decals) > 4:
                            #Remove the last decal
                            xp_props.decals.remove(xp_props.decals.count - 1)
    
    log_utils.display_messages()

#Function to update settings when a property is updated:
def update_settings(in_material):
    #Now we will update the settings.
            #Set backface culling to TRUE - .use_backface_culling
            #Set alpha blending to ALPHA_CLIP or OPAQUE - .blend_method
            #Set XP draped mode based on the draped property - .xplane.draped
            #Set XP alpha mode based on the blend_alpha property. Alpha Cutoff ("off") or Alpha Blend ("on") - .xplane.blend_v1000
            #Set XP hard mode based on the hard property ("none" or "concrete") - .xplane.surfaceType
                #If hard is true, set "xplane.deck" to true, otherwise set it to false
            #Set XP polygon offset based on the polygon_offset property - xplane.poly_os

    xp_mat = in_material.xp_materials

    #When we change our own settings for sync purposes, we will get called again. SO we need to check that, if that's the case, we set that we weren't programmatically updated and return since we're already up to datre
    if xp_mat.was_programmatically_updated:
        xp_mat.was_programmatically_updated = False
        return

    #Set backface culling to TRUE
    in_material.use_backface_culling = True
    in_material.show_transparent_back = False

    #Set XP draped mode based on the draped property
    if xp_mat.draped:
        in_material.xplane.draped = True
    else:
        in_material.xplane.draped = False

    # Set the separate material textures mode based on draped. If we are a CHANGE we need to change the other setting accordingly.
    # We will also check to make sure that the 'was' property is in sync. If it's not, we need to make sure it's in sync, then we'll
    #    update the other settign accordingly. THey SHOULDN'T get out of sync from user input, but other addons can cause this

    #Change in draped mode (or mismatch in settings)
    if xp_mat.draped != xp_mat.was_draped_last_update:
        #If it's enabled
        if xp_mat.draped:
            xp_mat.was_programmatically_updated = True
            xp_mat.do_separate_material_texture = False
            xp_mat.was_separate_material_texture_last_update = False
        xp_mat.was_draped_last_update = xp_mat.draped
    
    #Change in separate material texture mode (or mismatch in settings)
    if xp_mat.do_separate_material_texture != xp_mat.was_separate_material_texture_last_update:
        #If it's enabled
        if xp_mat.do_separate_material_texture:
            xp_mat.was_programmatically_updated = True
            xp_mat.draped = False
            xp_mat.was_draped_last_update = False
        xp_mat.was_separate_material_texture_last_update = xp_mat.do_separate_material_texture

    #Set XP alpha mode based on the blend_alpha property. Alpha Cutoff ("off") or Alpha Blend ("on")
    if xp_mat.blend_mode == "BLEND":
        in_material.xplane.blend_v1000 = 'on'
        in_material.xplane.blendRatio = xp_mat.blend_cutoff
        in_material.blend_method = 'BLEND'
    elif xp_mat.blend_mode == "SHADOW":
        in_material.xplane.blend_v1000 = 'shadow'
        in_material.xplane.blendRatio = xp_mat.blend_cutoff
        in_material.blend_method = 'BLEND'
    else:
        in_material.xplane.blend_v1000 = 'off'
        in_material.blend_method = 'CLIP'
        in_material.alpha_threshold = xp_mat.blend_cutoff
        in_material.xplane.blendRatio = xp_mat.blend_cutoff

    #Set XP hard mode based on the hard property ("none" or "concrete")
    in_material.xplane.surfaceType = xp_mat.surface_type.lower()
    in_material.xplane.deck = xp_mat.surface_is_deck

    #Set camera and aicraft specific properties
    in_material.xplane.solid_camera = xp_mat.camera_collision_enabled
    in_material.xplane.draw = xp_mat.drawing_enabled

    #Set shadow mode
    in_material.xplane.shadow_local = xp_mat.cast_shadow

    #Set XP polygon offset based on the polygon_offset property
    in_material.xplane.poly_os = xp_mat.polygon_offset

    #Set light level override
    if in_material.xplane:
        in_material.xplane.lightLevel = xp_mat.light_level_override
        in_material.xplane.lightLevel_v1 = xp_mat.light_level_v1
        in_material.xplane.lightLevel_v2 = xp_mat.light_level_v2
        in_material.xplane.lightLevel_photometric = xp_mat.light_level_photometric
        in_material.xplane.lightLevel_brightness = xp_mat.light_level_brightness
        in_material.xplane.lightLevel_dataref = xp_mat.light_level_dataref

    #Set cockpit device params
    if xp_mat.use_2d_panel_texture:
        in_material.xplane.cockpit_feature = 'panel'
        in_material.xplane.cockpit_region = str(xp_mat.panel_texture_region)
    if xp_mat.cockpit_device != "NONE":
        in_material.xplane.cockpit_feature = 'device'
        in_material.xplane.device_name = xp_mat.cockpit_device
        in_material.xplane.plugin_device = xp_mat.custom_cockpit_device
        in_material.xplane.device_bus_0 = xp_mat.cockpit_device_use_bus_1
        in_material.xplane.device_bus_1 = xp_mat.cockpit_device_use_bus_2
        in_material.xplane.device_bus_2 = xp_mat.cockpit_device_use_bus_3
        in_material.xplane.device_bus_3 = xp_mat.cockpit_device_use_bus_4
        in_material.xplane.device_bus_4 = xp_mat.cockpit_device_use_bus_5
        in_material.xplane.device_bus_5 = xp_mat.cockpit_device_use_bus_6
        in_material.xplane.device_lighting_channel = xp_mat.cockpit_device_lighting_channel
    elif not xp_mat.use_2d_panel_texture:
        in_material.xplane.cockpit_feature = 'none'

    #Set the correct number of decals
    while len(xp_mat.decals) < 4:
        #Add a new decal
        xp_mat.decals.add()
    while len(xp_mat.decals) > 4:
        #Remove the last decal
        xp_mat.decals.remove(xp_mat.decals.count - 1)

    xp_mat.decals[0].is_normal = False
    xp_mat.decals[1].is_normal = False
    xp_mat.decals[2].is_normal = True
    xp_mat.decals[3].is_normal = True

#Internal function to create the node setup for the keying of a decal
def create_decal_key_nodes(material, x, y, mod_connection, alb_node, key_r, key_g, key_b, key_a, key_base, key_mod):
    # Yeah, it's alot...
    # Basically the idea is we have keys. Keys are an arbitrary weight assigned to a certain factor (channels of the albedo, modulator texture, constant base key, etc). 
    # These keys are multiplied by their respective inputs, then normalized based on the max key value.
    # Then we add them all together, clamp them, then that is the mix factor for the shader node that mixes a given decal and given base.
    x_col_1 = x
    x_col_2 = x_col_1 + 100
    x_col_3 = x_col_2 + 100
    x_col_4 = x_col_3 + 100
    x_col_5 = x_col_4 + 100
    x_col_6 = x_col_5 + 100
    x_col_7 = x_col_6 + 100
    x_col_8 = x_col_7 + 100
    x_col_9 = x_col_8 + 100
    y_row_1 = y
    y_row_2 = y_row_1 + 100
    y_row_3 = y_row_2 + 100
    y_row_4 = y_row_3 + 100
    y_row_5 = y_row_4 + 100
    y_row_6 = y_row_5 + 100
    y_row_7 = y_row_6 + 100
    y_row_8 = y_row_7 + 100
    y_row_9 = y_row_8 + 100

    #Get the split RGB of the albedo, and the split RGB of the modulator
    node_alb_split_rgb = material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
    node_alb_split_rgb.location = (x_col_1, y_row_1)
    node_alb_split_rgb.label = "Alb Split RGB"
    node_alb_split_rgb.hide = True
    if alb_node != None:
        material.node_tree.links.new(alb_node.outputs[0], node_alb_split_rgb.inputs[0])

    #Now we can get the base keys. This is a math multiply node, multiplying the key by the respective channel.
    node_key_r = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_key_r.location = (x_col_1, y_row_2)
    node_key_r.label = "Key R"
    node_key_r.operation = 'MULTIPLY'
    node_key_r.inputs[0].default_value = key_r
    node_key_r.hide = True
    material.node_tree.links.new(node_alb_split_rgb.outputs[0], node_key_r.inputs[1])

    node_key_g = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_key_g.location = (x_col_1, y_row_3)
    node_key_g.label = "Key G"
    node_key_g.operation = 'MULTIPLY'
    node_key_g.inputs[0].default_value = key_g
    node_key_g.hide = True
    material.node_tree.links.new(node_alb_split_rgb.outputs[1], node_key_g.inputs[1])

    node_key_b = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_key_b.location = (x_col_1, y_row_4)
    node_key_b.label = "Key B"
    node_key_b.operation = 'MULTIPLY'
    node_key_b.inputs[0].default_value = key_b
    node_key_b.hide = True
    material.node_tree.links.new(node_alb_split_rgb.outputs[2], node_key_b.inputs[1])

    node_key_a = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_key_a.location = (x_col_1, y_row_5)
    node_key_a.label = "Key A"
    node_key_a.operation = 'MULTIPLY'
    node_key_a.inputs[0].default_value = key_a
    node_key_a.hide = True
    if alb_node != None:
        material.node_tree.links.new(alb_node.outputs[1], node_key_a.inputs[1])

    node_key_mod = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_key_mod.location = (x_col_1, y_row_6)
    node_key_mod.label = "Key Mod"
    node_key_mod.operation = 'MULTIPLY'
    node_key_mod.inputs[0].default_value = key_mod
    node_key_mod.hide = True
    if mod_connection != None:
        material.node_tree.links.new(mod_connection, node_key_mod.inputs[1])
    else:
        node_key_mod.inputs[1].default_value = 0

    node_key_base = material.node_tree.nodes.new(type="ShaderNodeValue")
    node_key_base.location = (x_col_1, y_row_7)
    node_key_base.label = "Key Base"
    node_key_base.outputs[0].default_value = key_base
    node_key_base.hide = True

    #Now that we have the base keys, we need to normalize them. We do this by dividing each key by the max key value (which we enter as a constant here)
    max_key_value = max(max(key_r, key_g, key_b, key_a, key_mod, key_base), 1)

    node_norm_r = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_norm_r.location = (x_col_2, y_row_2)
    node_norm_r.label = "Norm A"
    node_norm_r.operation = 'DIVIDE'
    material.node_tree.links.new(node_key_r.outputs[0], node_norm_r.inputs[0])
    node_norm_r.inputs[1].default_value = max_key_value
    node_norm_r.hide = True

    node_norm_g = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_norm_g.location = (x_col_2, y_row_3)
    node_norm_g.label = "Norm G"
    node_norm_g.operation = 'DIVIDE'
    material.node_tree.links.new(node_key_g.outputs[0], node_norm_g.inputs[0])
    node_norm_g.inputs[1].default_value = max_key_value
    node_norm_g.hide = True

    node_norm_b = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_norm_b.location = (x_col_2, y_row_4)
    node_norm_b.label = "Norm B"
    node_norm_b.operation = 'DIVIDE'
    material.node_tree.links.new(node_key_b.outputs[0], node_norm_b.inputs[0])
    node_norm_b.inputs[1].default_value = max_key_value
    node_norm_b.hide = True

    node_norm_a = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_norm_a.location = (x_col_2, y_row_5)
    node_norm_a.label = "Norm A"
    node_norm_a.operation = 'DIVIDE'
    material.node_tree.links.new(node_key_a.outputs[0], node_norm_a.inputs[0])
    node_norm_a.inputs[1].default_value = max_key_value
    node_norm_a.hide = True

    node_norm_mod = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_norm_mod.location = (x_col_2, y_row_6)
    node_norm_mod.label = "Norm Mod"
    node_norm_mod.operation = 'DIVIDE'
    material.node_tree.links.new(node_key_mod.outputs[0], node_norm_mod.inputs[0])
    node_norm_mod.inputs[1].default_value = max_key_value
    node_norm_mod.hide = True

    node_norm_base = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_norm_base.location = (x_col_2, y_row_7)
    node_norm_base.label = "Norm Base"
    node_norm_base.operation = 'DIVIDE'
    material.node_tree.links.new(node_key_base.outputs[0], node_norm_base.inputs[0])
    node_norm_base.inputs[1].default_value = max_key_value
    node_norm_base.hide = True

    # Add nodes to sum the normalized keys
    node_sum_rg = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_sum_rg.location = (x_col_3, y_row_2)
    node_sum_rg.label = "Sum RG"
    node_sum_rg.operation = 'ADD'
    material.node_tree.links.new(node_norm_r.outputs[0], node_sum_rg.inputs[0])
    material.node_tree.links.new(node_norm_g.outputs[0], node_sum_rg.inputs[1])
    node_sum_rg.hide = True

    node_sum_ba = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_sum_ba.location = (x_col_3, y_row_3)
    node_sum_ba.label = "Sum BA"
    node_sum_ba.operation = 'ADD'
    material.node_tree.links.new(node_norm_b.outputs[0], node_sum_ba.inputs[0])
    material.node_tree.links.new(node_norm_a.outputs[0], node_sum_ba.inputs[1])
    node_sum_ba.hide = True

    node_sum_mod_base = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_sum_mod_base.location = (x_col_3, y_row_4)
    node_sum_mod_base.label = "Sum Mod Base"
    node_sum_mod_base.operation = 'ADD'
    material.node_tree.links.new(node_norm_mod.outputs[0], node_sum_mod_base.inputs[0])
    material.node_tree.links.new(node_norm_base.outputs[0], node_sum_mod_base.inputs[1])
    node_sum_mod_base.hide = True

    # Add nodes to sum RG and BA
    node_sum_rg_ba = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_sum_rg_ba.location = (x_col_4, y_row_2)
    node_sum_rg_ba.label = "Sum RG+BA"
    node_sum_rg_ba.operation = 'ADD'
    material.node_tree.links.new(node_sum_rg.outputs[0], node_sum_rg_ba.inputs[0])
    material.node_tree.links.new(node_sum_ba.outputs[0], node_sum_rg_ba.inputs[1])
    node_sum_rg_ba.hide = True

    # Add nodes to sum RG+BA and Mod+Base
    node_sum_final = material.node_tree.nodes.new(type="ShaderNodeMath")
    node_sum_final.location = (x_col_5, y_row_2)
    node_sum_final.label = "Sum Final"
    node_sum_final.operation = 'ADD'
    material.node_tree.links.new(node_sum_rg_ba.outputs[0], node_sum_final.inputs[0])
    material.node_tree.links.new(node_sum_mod_base.outputs[0], node_sum_final.inputs[1])
    node_sum_final.hide = True

    # Add a clamp node
    node_clamp_final = material.node_tree.nodes.new(type="ShaderNodeClamp")
    node_clamp_final.location = (x_col_6, y_row_2)
    node_clamp_final.label = "Clamp Final"
    material.node_tree.links.new(node_sum_final.outputs[0], node_clamp_final.inputs[0])
    node_clamp_final.hide = True

    #Return the output of the clamp node
    return node_clamp_final.outputs[0]

#Function to update the nodes of a material
def update_nodes(material):
    #Check to make sure teh file is saved, otherwise exit and warn the user in the status bar
        if bpy.data.filepath == "":
            raise Exception("Please save the file before attempting to update materials. Textures are relative to the blender file, so if the file isn't saved I can't find your textures!")
            return
        
        #Check to make sure the material is set to use nodes, otherwise exit and warn the user in the status bar
        if material.use_nodes == False:
            material.use_nodes = True
            #raise Exception("Please set the material to use nodes before attempting to update materials.")
            #return
        
        #Define variables to hold the imagese
        image_alb = None
        image_alb_linear = None
        image_nml = None
        image_mat = None
        image_lit = None
        image_mod = None
        image_decal_1_alb = None
        image_decal_1_nml = None
        image_decal_2_alb = None
        image_decal_2_nml = None

        xp_material_props = material.xp_materials

        #If we have no decals we need to update the material settings to populate this data
        if len(xp_material_props.decals) == 0:
            update_settings(material)

        #Resolve paths. They are relative to the blender file or relative to one folder back. We assume one folder back first. If the file is not found, we assume it is in the same folder as the blender file.
        str_image_alb = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.alb_texture))
        str_image_nml = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.normal_texture))
        str_image_mat = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.material_texture))
        str_image_lit = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.lit_texture))
        str_image_mod = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.decal_modulator))
        str_image_decal_1_alb = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.decals[0].texture))
        str_image_decal_2_alb = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.decals[1].texture))
        str_image_decal_1_nml = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.decals[2].texture))
        str_image_decal_2_nml = file_utils.check_for_dds_or_png(file_utils.rel_to_abs(xp_material_props.decals[3].texture))

        if not xp_material_props.decals[0].enabled:
            str_image_decal_1_alb = ""

        if not xp_material_props.decals[1].enabled:
            str_image_decal_2_alb = ""

        if not xp_material_props.decals[2].enabled:
            str_image_decal_1_nml = ""

        if not xp_material_props.decals[3].enabled:
            str_image_decal_2_nml = ""
        
        #Load the images that exist
        if str_image_alb != "":
            image_alb = file_utils.get_or_load_image(str_image_alb, True)
            image_alb.colorspace_settings.name = 'sRGB' # Set colorspace to sRGB for albedo
            image_alb_linear = file_utils.get_or_load_image(str_image_alb, True, "_non-color")
            image_alb_linear.colorspace_settings.name = 'Non-Color' # Set colorspace to Non-Color for albedo linear
        else:
            #Disable alb decals if we don't have an alb
            str_image_decal_1_alb = ""
            str_image_decal_2_alb = ""
        if str_image_nml != "":
            image_nml = file_utils.get_or_load_image(str_image_nml, True)
            image_nml.colorspace_settings.name = 'sRGB' # Set colorspace to sRGB for normal
        else:
            #Disable nml decals if we don't have a nml
            str_image_decal_1_nml = ""
            str_image_decal_2_nml = ""
        if str_image_mat != "":
            image_mat = file_utils.get_or_load_image(str_image_mat, True)
            image_mat.colorspace_settings.name = 'sRGB' # Set colorspace to sRGB
        if str_image_lit != "":
            image_lit = file_utils.get_or_load_image(str_image_lit, True)
            image_lit.colorspace_settings.name = 'sRGB' # Set colorspace to sRGB
        if str_image_mod != "":
            image_mod = file_utils.get_or_load_image(str_image_mod, True)
            image_mod.colorspace_settings.name = 'sRGB' # Set colorspace to sRGB for modulator
        if str_image_decal_1_alb != "":
            image_decal_1_alb = file_utils.get_or_load_image(str_image_decal_1_alb, True)
        if str_image_decal_1_nml != "":
            image_decal_1_nml = file_utils.get_or_load_image(str_image_decal_1_nml, True)
        if str_image_decal_2_alb != "":
            image_decal_2_alb = file_utils.get_or_load_image(str_image_decal_2_alb, True)
        if str_image_decal_2_nml != "":
            image_decal_2_nml = file_utils.get_or_load_image(str_image_decal_2_nml, True)

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
                # separate RGB
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

        node_uv = material.node_tree.nodes.new(type="ShaderNodeUVMap")
        node_uv.location = (-5000, -500)
        node_uv.label = "UV Map"

        #We need to define the alb/nml node in advance since it will later be used for decals
        node_alb = None
        node_alb_linear = None
        node_nml_out = None

        #This is for the additive alpha between the alb and the lit, since both need it, it needs to be defined in advance
        node_alpha_add_lit = None
        node_alpha_clamp = None

        #Set up alb nodes
        if image_alb != None:
            node_alb = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_alb.label = "Albedo Texture"
            node_alpha_add_lit = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_alpha_clamp = material.node_tree.nodes.new(type="ShaderNodeClamp")
            node_alb.location = (-2600, 0)
            node_alpha_add_lit.location = (-2250, 0)
            node_alpha_clamp.location = (-2000, -0)
            node_alb.image = image_alb
            node_alpha_add_lit.operation = 'ADD'
            node_alpha_add_lit.inputs[1].default_value = 0
            node_alpha_add_lit.inputs[0].default_value = 0
            node_alpha_clamp.inputs[1].default_value = 0
            node_alpha_clamp.inputs[2].default_value = 1

            #Add a linear version of the alb for decal keying purposes
            node_alb_linear = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_alb_linear.label = "Albedo Texture Linear"
            node_alb_linear.location = (-2600, 250)
            node_alb_linear.image = image_alb_linear

            #Connect the nodes. Color to base color, alpha to add, add to principled alpha
            material.node_tree.links.new(node_alb.outputs[0], node_principled.inputs[0])    #Alb color to alb
            material.node_tree.links.new(node_alb.outputs[1], node_alpha_add_lit.inputs[0])
            material.node_tree.links.new(node_alpha_add_lit.outputs[0], node_alpha_clamp.inputs[0])
            
            if bpy.app.version < (3, 0, 0):
                material.node_tree.links.new(node_alpha_clamp.outputs[0], node_principled.inputs[19]) #Clamped alpha to alpha
            elif bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(node_alpha_clamp.outputs[0], node_principled.inputs[21]) #Clamped alpha to alpha
            else:
                material.node_tree.links.new(node_alpha_clamp.outputs[0], node_principled.inputs[4]) #Clamped alpha to alpha

        #Set up nml nodes
        if image_nml != None:

            node_nml = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_nml.label = "Normal Map"
            node_separate_rgb = material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
            node_combine_rgb = material.node_tree.nodes.new(type="ShaderNodeCombineRGB")
            node_normal_map = material.node_tree.nodes.new(type="ShaderNodeNormalMap")
            node_rough_invert = material.node_tree.nodes.new(type="ShaderNodeInvert")
            node_nml.location = (-2600, -250)
            node_separate_rgb.location = (-2250, -250)
            node_combine_rgb.location = (-2000, -250)
            node_normal_map.location = (-1750, -250)
            node_rough_invert.location = (-2250, -375)
            node_nml.image = image_nml
            image_nml.colorspace_settings.name = 'Non-Color'

            node_nml_out = node_normal_map

            #If we are not in separate material textures node, and are draped, we need to set the normal map's tiled UVs
            if not xp_material_props.do_separate_material_texture and xp_material_props.draped:
                node_uv_nml = material.node_tree.nodes.new(type="ShaderNodeVectorMath")
                node_uv_nml.location = (-3000, -250)
                node_uv_nml.label = "UV Scale Normal"
                node_uv_nml.operation = 'MULTIPLY'
                node_uv_nml.inputs[1].default_value = (xp_material_props.normal_tile_ratio, xp_material_props.normal_tile_ratio, xp_material_props.normal_tile_ratio)
                material.node_tree.links.new(node_uv.outputs[0], node_uv_nml.inputs[0])
                material.node_tree.links.new(node_uv_nml.outputs[0], node_nml.inputs[0])

            #Now connections, this is funky cuz XP doesn't use conventional formats. We need to map channels as follows:
                #NML R to separate R
                #NML G to separate G
                #NML B to principled metalness
                #NML alpha to invert
                #separate R to combine R
                #separate G to combine G
                #The combine B needs to be 1
                #Combine to normal map
                #Normal map to principled normal
                #Invert to principled roughness
            material.node_tree.links.new(node_nml.outputs[0], node_separate_rgb.inputs[0])
            material.node_tree.links.new(node_separate_rgb.outputs[0], node_combine_rgb.inputs[0])
            material.node_tree.links.new(node_separate_rgb.outputs[1], node_combine_rgb.inputs[1])
            
            node_combine_rgb.inputs[2].default_value = 1
            material.node_tree.links.new(node_combine_rgb.outputs[0], node_normal_map.inputs[1])
            
            material.node_tree.links.new(node_nml.outputs[1], node_rough_invert.inputs[1])

            if bpy.app.version < (3, 0, 0):
                material.node_tree.links.new(node_normal_map.outputs[0], node_principled.inputs[20])    #Reconstructed normal to normal
                if not xp_material_props.do_separate_material_texture:
                    material.node_tree.links.new(node_rough_invert.outputs[0], node_principled.inputs[7])   #Inverted normal roughness to roughness
                    material.node_tree.links.new(node_separate_rgb.outputs[2], node_principled.inputs[4])   #separate normal B to metalness
            elif bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(node_normal_map.outputs[0], node_principled.inputs[22])    #Reconstructed normal to normal
                if not xp_material_props.do_separate_material_texture:
                    material.node_tree.links.new(node_rough_invert.outputs[0], node_principled.inputs[9])   #Inverted normal roughness to roughness
                    material.node_tree.links.new(node_separate_rgb.outputs[2], node_principled.inputs[6])   #separate normal B to metalness
            else:
                material.node_tree.links.new(node_normal_map.outputs[0], node_principled.inputs[5])    #Reconstructed normal to normal
                if not xp_material_props.do_separate_material_texture:
                    material.node_tree.links.new(node_rough_invert.outputs[0], node_principled.inputs[2])   #Inverted normal roughness to roughness
                    material.node_tree.links.new(node_separate_rgb.outputs[2], node_principled.inputs[1])   #separate normal B to metalness
            
        #If we are in separate material textures mode, we need to set the normal map's tiled UVs
        if xp_material_props.do_separate_material_texture and image_mat != None:
            node_mat = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_mat.label = "Material Texture"
            node_mat.location = (-2600, -500)
            node_mat.image = image_mat
            image_mat.colorspace_settings.name = 'Non-Color'
            node_mat_separate_rgb = material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
            node_mat_separate_rgb.location = (-2300, -500)
            node_mat_invert_rough = material.node_tree.nodes.new(type="ShaderNodeInvert")
            node_mat_invert_rough.location = (-2000, -500)

            #For material textures, R is metalness, G is inverted roughness
            material.node_tree.links.new(node_mat.outputs[0], node_mat_separate_rgb.inputs[0])  #Mat color to mat split rgb
            material.node_tree.links.new(node_mat_separate_rgb.outputs[1], node_mat_invert_rough.inputs[1]) #G (roughness) to invert
            if bpy.app.version < (3, 0, 0):
                material.node_tree.links.new(node_mat_invert_rough.outputs[0], node_principled.inputs[7]) #Inverted roughness to roughness
                material.node_tree.links.new(node_mat_separate_rgb.outputs[0], node_principled.inputs[4]) #Mat R to metalness
            elif bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(node_mat_separate_rgb.outputs[0], node_principled.inputs[6]) #Mat R to metalness
                material.node_tree.links.new(node_mat_invert_rough.outputs[0], node_principled.inputs[9]) #Inverted roughness to roughness
            else:
                material.node_tree.links.new(node_mat_separate_rgb.outputs[0], node_principled.inputs[1])
                material.node_tree.links.new(node_mat_invert_rough.outputs[0], node_principled.inputs[2]) #Inverted roughness to roughness

        #Set up lit nodes
        if image_lit != None:
            node_lit = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_lit.label = "Lit Texture"
            node_lit.location = (-2600, -750)
            node_lit.image = image_lit

            #Connect the color to the principled emission
            if bpy.app.version < (3, 0, 0):
                material.node_tree.links.new(node_lit.outputs[0], node_principled.inputs[17])   #Lit color to emission
            elif bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(node_lit.outputs[0], node_principled.inputs[19])   #Lit color to emission
            elif bpy.app.version < (4, 2, 0):
                material.node_tree.links.new(node_lit.outputs[0], node_principled.inputs[26])   #Lit color to emission
                node_principled.inputs[27].default_value = (1) #Set the emission intensity to 1
            else:
                material.node_tree.links.new(node_lit.outputs[0], node_principled.inputs[27])   #Lit color to emission
                node_principled.inputs[28].default_value = (1) #Set the emission intensity to 1

            #If there is an alb, connect the alpha to it's add so it can impact the alpha
            if node_alpha_add_lit != None:
                material.node_tree.links.new(node_lit.outputs[1], node_alpha_add_lit.inputs[1])

        # Now we have the absolute joy of setting up decals! By joy I mean utter INSANITY *evil laughter*
        # We can have up to 2 decal sets. Each decal set can have an albedo rgb portion, albedo alpha portion, and a normal map portion.
        # Each portion can be keyed differently, so we will have to call create_decal_key_nodes for the alb rgb, the alb alpha, the normal if not normal follows alpha. And do that for each decal (if they're present of course).
        #
        # Keying also relies on a modulator, or none. So we need to check if the mod is present, and if so add an image node with it, and add a split node for it.
        #
        # Once we have all our keying figured out, we then need to mix it in with the main textures.
        # For the albedo, that means mixing in the alb rgb and alpha portions of the decal (cascading mix nodes, with the factor being the appropriate key, difference mode)
        # For dithering, this means mixing in the alpha portion of the alb decal (cascading mix nodes, with the factor being the appropriate key, blend mode being difference)
        # For the normal, that means mixing in the normal map portion of the decal (cascading mix nodes, with the factor being the appropriate key, add mode)

        # Before we do anything, we're going to define all the outputs we'll need here. They'll default to None, and we'll set them as we go
        output_mod_r = None
        output_mod_g = None
        output_src_1_alb_rgb = None
        output_src_1_alb_alpha = None
        output_src_1_dither = None
        output_src_1_nml = None
        output_src_2_alb_rgb = None
        output_src_2_alb_alpha = None
        output_src_2_dither = None
        output_src_2_nml = None
        output_key_1_alb_rgb = None
        output_key_1_alb_alpha = None
        output_key_1_nml = None
        output_key_2_alb_rgb = None
        output_key_2_alb_alpha = None
        output_key_2_nml = None
        output_uv_decal_alb_1 = None
        output_uv_decal_nml_1 = None
        output_uv_decal_alb_2 = None
        output_uv_decal_nml_2 = None

        #Add the modulator
        if image_mod != None:
            node_mod = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_mod.location = (-4600, 0)
            node_mod.image = image_mod
            image_mod.colorspace_settings.name = 'Non-Color'
            node_mod.image.colorspace_settings.name = 'Non-Color'
            node_mod.label = "Modulator"

            node_mod_split_rgb = material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
            node_mod_split_rgb.location = (-4250, 0)
            node_mod_split_rgb.label = "Mod Split RGB"
            material.node_tree.links.new(node_mod.outputs[0], node_mod_split_rgb.inputs[0])
            output_mod_r = node_mod_split_rgb.outputs[0]
            output_mod_g = node_mod_split_rgb.outputs[1]

        #Now we will add out keying nodes.
        if image_decal_1_alb != None:
            output_key_1_alb_rgb = create_decal_key_nodes(material, -4000, 6000, output_mod_r, node_alb_linear, \
                xp_material_props.decals[0].strength_key_red, xp_material_props.decals[0].strength_key_green, \
                xp_material_props.decals[0].strength_key_blue, xp_material_props.decals[0].strength_key_alpha, \
                xp_material_props.decals[0].strength_constant, xp_material_props.decals[0].strength_modulator)
            
            output_key_1_alb_alpha = create_decal_key_nodes(material, -4000, 5000, output_mod_r, node_alb_linear, \
                xp_material_props.decals[0].strength2_key_red, xp_material_props.decals[0].strength2_key_green, \
                xp_material_props.decals[0].strength2_key_blue, xp_material_props.decals[0].strength2_key_alpha, \
                xp_material_props.decals[0].strength2_constant, xp_material_props.decals[0].strength2_modulator)

        if image_decal_1_nml != None:
            output_key_1_nml = create_decal_key_nodes(material, -4000, 4000, output_mod_r, node_alb_linear, \
                xp_material_props.decals[2].strength_key_red, xp_material_props.decals[2].strength_key_green, \
                xp_material_props.decals[2].strength_key_blue, xp_material_props.decals[2].strength_key_alpha, \
                xp_material_props.decals[2].strength_constant, xp_material_props.decals[2].strength_modulator)
                
        if image_decal_2_alb != None:
            output_key_2_alb_rgb = create_decal_key_nodes(material, -4000, 3000, output_mod_g, node_alb_linear, \
                xp_material_props.decals[1].strength_key_red, xp_material_props.decals[1].strength_key_green, \
                xp_material_props.decals[1].strength_key_blue, xp_material_props.decals[1].strength_key_alpha, \
                xp_material_props.decals[1].strength_constant, xp_material_props.decals[1].strength_modulator)
            
            output_key_2_alb_alpha = create_decal_key_nodes(material, -4000, 2000, output_mod_g, node_alb_linear, \
                xp_material_props.decals[1].strength2_key_red, xp_material_props.decals[1].strength2_key_green, \
                xp_material_props.decals[1].strength2_key_blue, xp_material_props.decals[1].strength2_key_alpha, \
                xp_material_props.decals[1].strength2_constant, xp_material_props.decals[1].strength2_modulator)
            
        if image_decal_2_nml != None:
            output_key_2_nml = create_decal_key_nodes(material, -4000, 1000, output_mod_g, node_alb_linear, \
                xp_material_props.decals[3].strength_key_red, xp_material_props.decals[3].strength_key_green, \
                xp_material_props.decals[3].strength_key_blue, xp_material_props.decals[3].strength_key_alpha, \
                xp_material_props.decals[3].strength_constant, xp_material_props.decals[3].strength_modulator)
                
        # Keying nodes are DONE!!!
        # Next up we need to start working on setting up the decal source UVs
        # So first off, we'll need to get the UV map, then we need vector math nodes to multiply the UVs by the decal scale. We'll need a single UV node, and up to 4 vector math nodes (alb 1, nml1, alb2, nml2)

        if image_decal_1_alb != None:
            node_uv_decal_alb_1 = material.node_tree.nodes.new(type="ShaderNodeVectorMath")
            node_uv_decal_alb_1.location = (-4750, -500)
            node_uv_decal_alb_1.label = "UV Scale Alb 1"
            node_uv_decal_alb_1.operation = 'MULTIPLY'
            node_uv_decal_alb_1.inputs[1].default_value = (xp_material_props.decals[0].tile_ratio, xp_material_props.decals[0].tile_ratio, xp_material_props.decals[0].tile_ratio)
            material.node_tree.links.new(node_uv.outputs[0], node_uv_decal_alb_1.inputs[0])

            output_uv_decal_alb_1 = node_uv_decal_alb_1.outputs[0]
        
        if image_decal_1_nml != None:
            node_uv_decal_nml_1 = material.node_tree.nodes.new(type="ShaderNodeVectorMath")
            node_uv_decal_nml_1.location = (-4750, -750)
            node_uv_decal_nml_1.label = "UV Scale Nml 1"
            node_uv_decal_nml_1.operation = 'MULTIPLY'
            node_uv_decal_nml_1.inputs[1].default_value = (xp_material_props.decals[2].tile_ratio, xp_material_props.decals[2].tile_ratio, xp_material_props.decals[2].tile_ratio)
            material.node_tree.links.new(node_uv.outputs[0], node_uv_decal_nml_1.inputs[0])

            output_uv_decal_nml_1 = node_uv_decal_nml_1.outputs[0]

        if image_decal_2_alb != None:
            node_uv_decal_alb_2 = material.node_tree.nodes.new(type="ShaderNodeVectorMath")
            node_uv_decal_alb_2.location = (-4750, -1000)
            node_uv_decal_alb_2.label = "UV Scale Alb 2"
            node_uv_decal_alb_2.operation = 'MULTIPLY'
            node_uv_decal_alb_2.inputs[1].default_value = (xp_material_props.decals[1].tile_ratio, xp_material_props.decals[1].tile_ratio, xp_material_props.decals[1].tile_ratio)
            material.node_tree.links.new(node_uv.outputs[0], node_uv_decal_alb_2.inputs[0])

            output_uv_decal_alb_2 = node_uv_decal_alb_2.outputs[0]

        if image_decal_2_nml != None:
            node_uv_decal_nml_2 = material.node_tree.nodes.new(type="ShaderNodeVectorMath")
            node_uv_decal_nml_2.location = (-4750, -1250)
            node_uv_decal_nml_2.label = "UV Scale Nml 2"
            node_uv_decal_nml_2.operation = 'MULTIPLY'
            node_uv_decal_nml_2.inputs[1].default_value = (xp_material_props.decals[3].tile_ratio, xp_material_props.decals[3].tile_ratio, xp_material_props.decals[3].tile_ratio)
            material.node_tree.links.new(node_uv.outputs[0], node_uv_decal_nml_2.inputs[0])

            output_uv_decal_nml_2 = node_uv_decal_nml_2.outputs[0]

        # Now that we have the UVs, we need to set up the actual source nodes.
        # Basically for Alb, we have just an image node, with the appropriate UV
        # For Normals, we need an image node, we split it's RGB, merge R G and B as 1, then connect it to a normal map.

        if image_decal_1_alb != None:
            node_decal_1_alb = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_decal_1_alb.location = (-4000, 0)
            node_decal_1_alb.label = "Decal 1 Alb"
            node_decal_1_alb.image = image_decal_1_alb
            node_decal_1_alb.image.colorspace_settings.name = 'Non-Color'
            material.node_tree.links.new(output_uv_decal_alb_1, node_decal_1_alb.inputs[0])

            #Now we need to subtract 0.5 from the rgb and the alpha
            node_decal_1_subtract_rgb = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_decal_1_subtract_rgb.location = (-3750, 0)
            node_decal_1_subtract_rgb.label = "Decal 1 Subtract RGB"
            node_decal_1_subtract_rgb.operation = 'SUBTRACT'
            node_decal_1_subtract_rgb.inputs[1].default_value = 0.5
            material.node_tree.links.new(node_decal_1_alb.outputs[0], node_decal_1_subtract_rgb.inputs[0])

            node_decal_1_subtract_alpha = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_decal_1_subtract_alpha.location = (-3750, -250)
            node_decal_1_subtract_alpha.label = "Decal 1 Subtract Alpha"
            node_decal_1_subtract_alpha.operation = 'SUBTRACT'
            node_decal_1_subtract_alpha.inputs[1].default_value = 0.5
            material.node_tree.links.new(node_decal_1_alb.outputs[1], node_decal_1_subtract_alpha.inputs[0])

            #Now for the dither, we need to add a math node to multiply the alpha by the dither ratio
            node_decal_1_dither = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_decal_1_dither.location = (-3500, -250)
            node_decal_1_dither.label = "Decal 1 Dither"
            node_decal_1_dither.operation = 'MULTIPLY'
            node_decal_1_dither.inputs[1].default_value = xp_material_props.decals[0].dither_ratio
            material.node_tree.links.new(node_decal_1_subtract_alpha.outputs[0], node_decal_1_dither.inputs[0])

            #Then we need to add a math node and multiply the dither by -1 to match XP
            node_decal_1_dither_neg = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_decal_1_dither_neg.location = (-3250, -250)
            node_decal_1_dither_neg.label = "Decal 1 Dither Neg"
            node_decal_1_dither_neg.operation = 'MULTIPLY'
            node_decal_1_dither_neg.inputs[1].default_value = -1
            material.node_tree.links.new(node_decal_1_dither.outputs[0], node_decal_1_dither_neg.inputs[0])

            output_src_1_alb_rgb = node_decal_1_subtract_rgb.outputs[0]
            output_src_1_alb_alpha = node_decal_1_subtract_alpha.outputs[0]
            output_src_1_dither = node_decal_1_dither_neg.outputs[0]

        if image_decal_1_nml != None:
            node_decal_1_nml = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_decal_1_nml.location = (-4000, -500)
            node_decal_1_nml.label = "Decal 1 Nml"
            node_decal_1_nml.image = image_decal_1_nml
            image_decal_1_nml.colorspace_settings.name = 'Non-Color'
            material.node_tree.links.new(output_uv_decal_nml_1, node_decal_1_nml.inputs[0])

            node_decal_1_split_rgb = material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
            node_decal_1_split_rgb.location = (-3750, -500)
            node_decal_1_split_rgb.label = "Decal 1 Split RGB"
            material.node_tree.links.new(node_decal_1_nml.outputs[0], node_decal_1_split_rgb.inputs[0])

            node_decal_1_combine_rgb = material.node_tree.nodes.new(type="ShaderNodeCombineRGB")
            node_decal_1_combine_rgb.location = (-3500, -500)
            node_decal_1_combine_rgb.label = "Decal 1 Combine RGB"
            material.node_tree.links.new(node_decal_1_split_rgb.outputs[0], node_decal_1_combine_rgb.inputs[0])
            material.node_tree.links.new(node_decal_1_split_rgb.outputs[1], node_decal_1_combine_rgb.inputs[1])
            node_decal_1_combine_rgb.inputs[2].default_value = 1

            node_decal_1_normal_map = material.node_tree.nodes.new(type="ShaderNodeNormalMap")
            node_decal_1_normal_map.location = (-3250, -500)
            node_decal_1_normal_map.label = "Decal 1 Normal Map"
            material.node_tree.links.new(node_decal_1_combine_rgb.outputs[0], node_decal_1_normal_map.inputs[1])

            output_src_1_nml = node_decal_1_normal_map.outputs[0]

        if image_decal_2_alb != None:
            node_decal_2_alb = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_decal_2_alb.location = (-4000, -1000)
            node_decal_2_alb.label = "Decal 2 Alb"
            node_decal_2_alb.image = image_decal_2_alb
            node_decal_2_alb.image.colorspace_settings.name = 'Non-Color'
            material.node_tree.links.new(output_uv_decal_alb_2, node_decal_2_alb.inputs[0])

            #Now we need to subtract 0.5 from the rgb and the alpha
            node_decal_2_subtract_rgb = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_decal_2_subtract_rgb.location = (-3750, -1000)
            node_decal_2_subtract_rgb.label = "Decal 2 Subtract RGB"
            node_decal_2_subtract_rgb.operation = 'SUBTRACT'
            node_decal_2_subtract_rgb.inputs[1].default_value = 0.5
            material.node_tree.links.new(node_decal_2_alb.outputs[0], node_decal_2_subtract_rgb.inputs[0])

            node_decal_2_subtract_alpha = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_decal_2_subtract_alpha.location = (-3750, -1250)
            node_decal_2_subtract_alpha.label = "Decal 2 Subtract Alpha"
            node_decal_2_subtract_alpha.operation = 'SUBTRACT'
            node_decal_2_subtract_alpha.inputs[1].default_value = 0.5
            material.node_tree.links.new(node_decal_2_alb.outputs[1], node_decal_2_subtract_alpha.inputs[0])

            #Now for the dither, we need to add a math node to multiply the alpha by the dither ratio
            node_decal_2_dither = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_decal_2_dither.location = (-3500, -1250)
            node_decal_2_dither.label = "Decal 2 Dither"
            node_decal_2_dither.operation = 'MULTIPLY'
            node_decal_2_dither.inputs[1].default_value = xp_material_props.decals[1].dither_ratio
            material.node_tree.links.new(node_decal_2_subtract_alpha.outputs[0], node_decal_2_dither.inputs[0])

            #Then we need to add a math node and multiply the dither by -1 to match XP
            node_decal_2_dither_neg = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_decal_2_dither_neg.location = (-3250, -1250)
            node_decal_2_dither_neg.label = "Decal 2 Dither Neg"
            node_decal_2_dither_neg.operation = 'MULTIPLY'
            node_decal_2_dither_neg.inputs[1].default_value = -1
            material.node_tree.links.new(node_decal_2_dither.outputs[0], node_decal_2_dither_neg.inputs[0])

            output_src_2_alb_rgb = node_decal_2_subtract_rgb.outputs[0]
            output_src_2_alb_alpha = node_decal_2_subtract_alpha.outputs[0]
            output_src_2_dither = node_decal_2_dither_neg.outputs[0]

        if image_decal_2_nml != None:
            node_decal_2_nml = material.node_tree.nodes.new(type="ShaderNodeTexImage")
            node_decal_2_nml.location = (-4000, -1500)
            node_decal_2_nml.label = "Decal 2 Nml"
            node_decal_2_nml.image = image_decal_2_nml
            image_decal_2_nml.colorspace_settings.name = 'Non-Color'
            material.node_tree.links.new(output_uv_decal_nml_2, node_decal_2_nml.inputs[0])

            node_decal_2_split_rgb = material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
            node_decal_2_split_rgb.location = (-3750, -1500)
            node_decal_2_split_rgb.label = "Decal 2 Split RGB"
            material.node_tree.links.new(node_decal_2_nml.outputs[0], node_decal_2_split_rgb.inputs[0])

            node_decal_2_combine_rgb = material.node_tree.nodes.new(type="ShaderNodeCombineRGB")
            node_decal_2_combine_rgb.location = (-3500, -1500)
            node_decal_2_combine_rgb.label = "Decal 2 Combine RGB"
            material.node_tree.links.new(node_decal_2_split_rgb.outputs[0], node_decal_2_combine_rgb.inputs[0])
            material.node_tree.links.new(node_decal_2_split_rgb.outputs[1], node_decal_2_combine_rgb.inputs[1])
            node_decal_2_combine_rgb.inputs[2].default_value = 1

            node_decal_2_normal_map = material.node_tree.nodes.new(type="ShaderNodeNormalMap")
            node_decal_2_normal_map.location = (-3250, -1500)
            node_decal_2_normal_map.label = "Decal 2 Normal Map"
            material.node_tree.links.new(node_decal_2_combine_rgb.outputs[0], node_decal_2_normal_map.inputs[1])

            output_src_2_nml = node_decal_2_normal_map.outputs[0]

        # Now that we have the source nodes, we need to start mixing them!
        # Since we can have up to 4 Alb sources, we will have 4 cascading mix nodes from the base alb to the principled node. Add blend mode (since we subtracted 0.5 earlier this is basically sadd), factor is the key
        # For the normal, we will have 2 cascading mix nodes from the base normal to the principled node. Blend mode is add, factor is the key

        node_alb_post_mix_1 = node_alb #This defaults to alb because if we have a decal 2 and not decal 1, we still need an input for the decal 2 input
        node_nml_post_mix_1 = node_nml_out #This defaults to nml because if we have a decal 2 and not decal 1, we still need an input for the decal 2 input
        node_alpha_post_mix = node_alpha_clamp #This defaults to add because if we have a decal 2 and not decal 1, we still need an input for the decal 2 input

        if image_decal_1_alb != None and node_alb_post_mix_1 != None:
            node_mix_1 = material.node_tree.nodes.new(type="ShaderNodeMixRGB")
            node_mix_1.location = (-1500, 0)
            node_mix_1.label = "Mix Decal 1 Alb RGB"
            node_mix_1.blend_type = 'ADD'
            
            material.node_tree.links.new(output_key_1_alb_rgb, node_mix_1.inputs[0])
            material.node_tree.links.new(node_alb.outputs[0], node_mix_1.inputs[1])
            material.node_tree.links.new(output_src_1_alb_rgb, node_mix_1.inputs[2])

            node_mix_2 = material.node_tree.nodes.new(type="ShaderNodeMixRGB")
            node_mix_2.location = (-1250, 0)
            node_mix_2.label = "Mix Decal 1 Alb Alpha"
            node_mix_2.blend_type = 'ADD'

            material.node_tree.links.new(output_key_1_alb_alpha, node_mix_2.inputs[0])
            material.node_tree.links.new(node_mix_1.outputs[0], node_mix_2.inputs[1])
            material.node_tree.links.new(output_src_1_alb_alpha, node_mix_2.inputs[2])

            node_alb_post_mix_1 = node_mix_2

            #Now we need to mix in the dither. This is just adding to the alpha (node_alpha_post_mix)
            node_dither_mix_1 = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_dither_mix_1.location = (-1250, -250)
            node_dither_mix_1.label = "Mix Decal 1 Dither"
            node_dither_mix_1.operation = 'ADD'
            material.node_tree.links.new(node_alpha_post_mix.outputs[0], node_dither_mix_1.inputs[0])
            material.node_tree.links.new(output_src_1_dither, node_dither_mix_1.inputs[1])

            node_alpha_post_mix = node_dither_mix_1

        if image_decal_1_nml != None and node_nml_post_mix_1 != None:
            node_nml_mix_1 = material.node_tree.nodes.new(type="ShaderNodeMixRGB")
            node_nml_mix_1.location = (-1500, -500)
            node_nml_mix_1.label = "Mix Decal 1 Nml"
            node_nml_mix_1.blend_type = 'ADD'

            material.node_tree.links.new(output_key_1_nml, node_nml_mix_1.inputs[0])
            material.node_tree.links.new(node_nml_out.outputs[0], node_nml_mix_1.inputs[1])
            material.node_tree.links.new(output_src_1_nml, node_nml_mix_1.inputs[2])

            node_nml_post_mix_1 = node_nml_mix_1

        if image_decal_2_alb != None and node_alb_post_mix_1 != None:
            node_mix_3 = material.node_tree.nodes.new(type="ShaderNodeMixRGB")
            node_mix_3.location = (-1000, 0)
            node_mix_3.label = "Mix Decal 2 Alb RGB"
            node_mix_3.blend_type = 'ADD'

            material.node_tree.links.new(output_key_2_alb_rgb, node_mix_3.inputs[0])
            material.node_tree.links.new(node_alb_post_mix_1.outputs[0], node_mix_3.inputs[1])
            material.node_tree.links.new(output_src_2_alb_rgb, node_mix_3.inputs[2])

            node_mix_4 = material.node_tree.nodes.new(type="ShaderNodeMixRGB")
            node_mix_4.location = (-750, -0)
            node_mix_4.label = "Mix Decal 2 Alb Alpha"
            node_mix_4.blend_type = 'ADD'

            material.node_tree.links.new(output_key_2_alb_alpha, node_mix_4.inputs[0])
            material.node_tree.links.new(node_mix_3.outputs[0], node_mix_4.inputs[1])
            material.node_tree.links.new(output_src_2_alb_alpha, node_mix_4.inputs[2])

            node_alb_post_mix_1 = node_mix_4

            # Now we need to mix in the dither. This is just adding to the alpha (node_alpha_post_mix)
            node_dither_mix_2 = material.node_tree.nodes.new(type="ShaderNodeMath")
            node_dither_mix_2.location = (-1000, -250)
            node_dither_mix_2.label = "Mix Decal 2 Dither"
            node_dither_mix_2.operation = 'ADD'
            material.node_tree.links.new(node_alpha_post_mix.outputs[0], node_dither_mix_2.inputs[0])
            material.node_tree.links.new(output_src_2_dither, node_dither_mix_2.inputs[1])

            node_alpha_post_mix = node_dither_mix_2

        if image_decal_2_nml != None and node_nml_post_mix_1 != None:
            node_nml_mix_2 = material.node_tree.nodes.new(type="ShaderNodeMixRGB")
            node_nml_mix_2.location = (-1000, -500)
            node_nml_mix_2.label = "Mix Decal 2 Nml"
            node_nml_mix_2.blend_type = 'ADD'

            material.node_tree.links.new(output_key_2_nml, node_nml_mix_2.inputs[0])
            material.node_tree.links.new(node_nml_post_mix_1.outputs[0], node_nml_mix_2.inputs[1])
            material.node_tree.links.new(output_src_2_nml, node_nml_mix_2.inputs[2])

            node_nml_post_mix_1 = node_nml_mix_2

        #Now finally we will link the post-mix nodes to the principled node!
        if node_alpha_post_mix != None:
            material.node_tree.links.new(node_alb_post_mix_1.outputs[0], node_principled.inputs[0])

        if bpy.app.version < (3, 0, 0) and node_nml_post_mix_1 != None:
                material.node_tree.links.new(node_nml_post_mix_1.outputs[0], node_principled.inputs[20])    #Reconstructed normal to normal
        elif bpy.app.version < (4, 0, 0) and node_nml_post_mix_1 != None:
            material.node_tree.links.new(node_nml_post_mix_1.outputs[0], node_principled.inputs[22])    #Reconstructed normal to normal
        elif node_nml_post_mix_1 != None:
            material.node_tree.links.new(node_nml_post_mix_1.outputs[0], node_principled.inputs[5])    #Reconstructed normal to normal

        #Add a final clamp node to clamp the alpha to 0-1
        if node_alpha_post_mix != node_alpha_clamp and node_alpha_post_mix != None:
            
            node_alpha_clamp = material.node_tree.nodes.new(type="ShaderNodeClamp")
            node_alpha_clamp.location = (-750, -250)
            node_alpha_clamp.label = "Clamp Alpha"
            material.node_tree.links.new(node_alpha_post_mix.outputs[0], node_alpha_clamp.inputs[0])

            if bpy.app.version < (3, 0, 0):
                material.node_tree.links.new(node_alpha_clamp.outputs[0], node_principled.inputs[19]) #Clamped alpha to alpha
            elif bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(node_alpha_clamp.outputs[0], node_principled.inputs[21]) #Clamped alpha to alpha
            else:
                material.node_tree.links.new(node_alpha_clamp.outputs[0], node_principled.inputs[4]) #Clamped alpha to alpha

            

