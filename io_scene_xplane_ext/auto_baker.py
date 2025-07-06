#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/28/2024
#Module:    Auto Baker
#Purpose:   Provide a single function to bake high poly models to low poly models in the X-Plane format

from .Helpers import bake_utils
from .Helpers import log_utils
import bpy

# Iterates through all the channels to bake, configuring all source materials, calling blender bake, then saving the textures. Once all channels have been baked, normals are merged, then the target textures are saved the source materials reverted
def auto_bake_current_to_active():
    #Make the active object no longer be selected (so changes don't affect it)
    bpy.context.view_layer.objects.active.select_set(False)

    #Get all the materials for the selected models
    mats = bake_utils.get_source_materials()

    bpy.context.window_manager.progress_begin(0, 100)
    bpy.context.window_manager.progress_update(0)

    #Alb. We need to config source materials, config target material, config bake settings, bake
    log_utils.new_section("Baking low poly model to high poly model")
    log_utils.info("Baking base")
    bake_utils.config_source_materials(bake_utils.BakeType.BASE, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.BASE, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.BASE)
    bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
    log_utils.info("Base baked")

    bpy.context.window_manager.progress_update(15)

    log_utils.info("Baking opacity")
    bake_utils.config_source_materials(bake_utils.BakeType.OPACITY, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.OPACITY, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.OPACITY)
    bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
    log_utils.info("Opacity baked")

    bpy.context.window_manager.progress_update(30)

    #Normal. We need to config source materials, config target material, config bake settings, bake
    log_utils.info("Baking normal")
    bake_utils.config_source_materials(bake_utils.BakeType.NORMAL, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.NORMAL, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.NORMAL)
    bpy.ops.object.bake(type='NORMAL')
    log_utils.info("Normal baked")

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
    log_utils.info("Baking lit")
    bake_utils.config_source_materials(bake_utils.BakeType.LIT, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.LIT, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.LIT)
    bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
    log_utils.info("Lit baked")

    bpy.context.window_manager.progress_update(90)

    #Now save and merge out of process
    log_utils.info("Merging and saving textures")
    bake_utils.save_baked_textures(bpy.context.view_layer.objects.active)

    bpy.context.window_manager.progress_update(99)

    #Now revert all the materials
    log_utils.info("Reverting materials")
    bake_utils.reset_source_materials(mats)

    #Now set the material for the low poly to the baked material
    log_utils.info("Setting low poly material")
    bake_utils.config_target_object_with_new_textures(bpy.context.view_layer.objects.active)

    bpy.context.window_manager.progress_end()

    #Done
    print("Done!")

    