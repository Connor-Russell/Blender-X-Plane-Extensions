#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/28/2024
#Module:    auto_baker.py
#Purpose:   Automates the baking of high poly to low poly models for X-Plane

from .Helpers import bake_utils
from .Helpers import log_utils
import bpy

# Iterates through all the channels to bake, configuring all source materials, calling blender bake, then saving the textures. Once all channels have been baked, normals are merged, then the target textures are saved the source materials reverted
def auto_bake_current_to_active():
    #Make the active object no longer be selected (so changes don't affect it)
    bpy.context.view_layer.objects.active.select_set(False)

    #Store the original bake settings
    original_state_bake_selected_to_active = bpy.context.scene.render.bake.use_selected_to_active
    original_state_bake_use_clear = bpy.context.scene.render.bake.use_clear
    original_state_cycles_samples = bpy.context.scene.cycles.samples
    original_state_render_engine = bpy.context.scene.render.engine
    original_state_cycles_bake_type = bpy.context.scene.cycles.bake_type
    original_state_bake_use_pass_direct = bpy.context.scene.render.bake.use_pass_direct
    original_state_bake_use_pass_indirect = bpy.context.scene.render.bake.use_pass_indirect
    original_state_bake_use_pass_color = bpy.context.scene.render.bake.use_pass_color
    original_state_image_settings_color_mode = bpy.context.scene.render.image_settings.color_mode
    original_state_bake_normal_space = bpy.context.scene.render.bake.normal_space
    original_state_bake_normal_r = bpy.context.scene.render.bake.normal_r
    original_state_bake_normal_g = bpy.context.scene.render.bake.normal_g
    original_state_bake_normal_b = bpy.context.scene.render.bake.normal_b
    original_state_bake_cage_extrusion = bpy.context.scene.render.bake.cage_extrusion
    original_state_bake_max_ray_distance = bpy.context.scene.render.bake.max_ray_distance
    original_state_margin = bpy.context.scene.render.bake.margin

    #Do initial bake settings
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.use_clear = False
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.bake.cage_extrusion = bpy.context.scene.xp_ext.low_poly_bake_extrusion_distance
    bpy.context.scene.render.bake.max_ray_distance = bpy.context.scene.xp_ext.low_poly_bake_max_ray_distance
    bpy.context.scene.render.bake.margin = bpy.context.scene.xp_ext.low_poly_bake_margin

    #Get all the materials for the selected models
    mats = bake_utils.get_source_materials()

    #Check if we need to bake lits, normals, and albedos
    do_bake_alb = False
    do_bake_nrm = False
    do_bake_mat = False
    do_bake_lit = False
    do_bake_opacity = False
    for mat in mats:
        print("Checking ", mat)
        if mat.xp_materials.alb_texture != "":
            do_bake_alb = bpy.context.scene.xp_ext.low_poly_bake_do_alb
            do_bake_opacity = bpy.context.scene.xp_ext.low_poly_bake_do_opacity
        if mat.xp_materials.normal_texture != "":
            do_bake_nrm = bpy.context.scene.xp_ext.low_poly_bake_do_nrm
        if mat.xp_materials.material_texture != "" or (not mat.xp_materials.do_separate_material_texture and mat.xp_materials.normal_texture != ""):
            do_bake_mat = bpy.context.scene.xp_ext.low_poly_bake_do_mat
        if mat.xp_materials.lit_texture != "":
            do_bake_lit = bpy.context.scene.xp_ext.low_poly_bake_do_lit

    #If we are doing *combined* normals, we must do mat if we are doing nrm
    if not bpy.context.scene.xp_ext.low_poly_bake_do_separate_normals:
        do_bake_mat = do_bake_nrm

    bpy.context.window_manager.progress_begin(0, 100)
    bpy.context.window_manager.progress_update(0)

    #Alb. We need to config source materials, config target material, config bake settings, bake
    if do_bake_alb:
        log_utils.new_section("Baking low poly model to high poly model")
        log_utils.info("Baking base")
        bake_utils.config_source_materials(bake_utils.BakeType.BASE, mats)
        bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.BASE, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
        bake_utils.config_bake_settings(bake_utils.BakeType.BASE)
        bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
        log_utils.info("Base baked")
    else:
        log_utils.info("Skipping base bake as no albedo textures were found")

    bpy.context.window_manager.progress_update(15)

    if do_bake_opacity:
        log_utils.info("Baking opacity")
        bake_utils.config_source_materials(bake_utils.BakeType.OPACITY, mats)
        bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.OPACITY, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
        bake_utils.config_bake_settings(bake_utils.BakeType.OPACITY)
        bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
        log_utils.info("Opacity baked")

    bpy.context.window_manager.progress_update(30)

    #Normal. We need to config source materials, config target material, config bake settings, bake
    if do_bake_nrm:
        log_utils.info("Baking normal")
        bake_utils.config_source_materials(bake_utils.BakeType.NORMAL, mats)
        bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.NORMAL, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
        bake_utils.config_bake_settings(bake_utils.BakeType.NORMAL)
        bpy.ops.object.bake(type='NORMAL')
        log_utils.info("Normal baked")

    if do_bake_mat:
        bpy.context.window_manager.progress_update(45)

        #Roughness. We need to config source materials, config target material, config bake settings, bake
        log_utils.info("Baking roughness")
        bake_utils.config_source_materials(bake_utils.BakeType.ROUGHNESS, mats)
        bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.ROUGHNESS, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
        bake_utils.config_bake_settings(bake_utils.BakeType.ROUGHNESS)
        bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
        log_utils.info("Roughness baked")

        bpy.context.window_manager.progress_update(60)

        #Metalness. We need to config source materials, config target material, config bake settings, bake
        log_utils.info("Baking metalness")
        bake_utils.config_source_materials(bake_utils.BakeType.METALNESS, mats)
        bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.METALNESS, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
        bake_utils.config_bake_settings(bake_utils.BakeType.METALNESS)
        bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
        log_utils.info("Metalness baked")

    bpy.context.window_manager.progress_update(75)

    #Lit. We need to config source materials, config target material, config bake settings, bake
    if do_bake_lit:
        log_utils.info("Baking lit")
        bake_utils.config_source_materials(bake_utils.BakeType.LIT, mats)
        bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.LIT, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
        bake_utils.config_bake_settings(bake_utils.BakeType.LIT)
        bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
        log_utils.info("Lit baked")

    bpy.context.window_manager.progress_update(90)

    #Now save and merge out of process
    log_utils.info("Merging and saving textures")
    bake_utils.save_baked_textures(bpy.context.view_layer.objects.active, bpy.context.scene.xp_ext.low_poly_bake_do_separate_normals, do_bake_alb, do_bake_opacity, do_bake_nrm, do_bake_mat, do_bake_lit)

    bpy.context.window_manager.progress_update(99)

    #Now revert all the materials
    log_utils.info("Reverting materials")
    bake_utils.reset_source_materials(mats)

    #Now set the material for the low poly to the baked material
    log_utils.info("Setting low poly material")
    bake_utils.config_target_object_with_new_textures(bpy.context.view_layer.objects.active, bpy.context.scene.xp_ext.low_poly_bake_do_separate_normals)

    #Reset the bake settings
    bpy.context.scene.render.bake.use_selected_to_active = original_state_bake_selected_to_active
    bpy.context.scene.render.bake.use_clear = original_state_bake_use_clear
    bpy.context.scene.cycles.samples = original_state_cycles_samples
    bpy.context.scene.render.engine = original_state_render_engine
    bpy.context.scene.cycles.bake_type = original_state_cycles_bake_type
    bpy.context.scene.render.bake.use_pass_direct = original_state_bake_use_pass_direct
    bpy.context.scene.render.bake.use_pass_indirect = original_state_bake_use_pass_indirect
    bpy.context.scene.render.bake.use_pass_color = original_state_bake_use_pass_color
    bpy.context.scene.render.image_settings.color_mode = original_state_image_settings_color_mode
    bpy.context.scene.render.bake.normal_space = original_state_bake_normal_space
    bpy.context.scene.render.bake.normal_r = original_state_bake_normal_r
    bpy.context.scene.render.bake.normal_g = original_state_bake_normal_g
    bpy.context.scene.render.bake.normal_b = original_state_bake_normal_b
    bpy.context.scene.render.bake.cage_extrusion = original_state_bake_cage_extrusion
    bpy.context.scene.render.bake.max_ray_distance = original_state_bake_max_ray_distance
    bpy.context.scene.render.bake.margin = original_state_margin

    bpy.context.window_manager.progress_end()

    #Done
    print("Done!")
  