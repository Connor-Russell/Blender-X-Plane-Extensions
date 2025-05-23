#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/28/2024
#Module:    Auto Baker
#Purpose:   Provide a single function to bake high poly models to low poly models in the X-Plane format

from .Helpers import bake_utils
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
    print("Baking base")
    bake_utils.config_source_materials(bake_utils.BakeType.BASE, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.BASE, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.BASE)
    bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
    print("Base baked")

    bpy.context.window_manager.progress_update(20)

    #Normal. We need to config source materials, config target material, config bake settings, bake
    print("Baking normal")
    bake_utils.config_source_materials(bake_utils.BakeType.NORMAL, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.NORMAL, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.NORMAL)
    bpy.ops.object.bake(type='NORMAL')
    print("Normal baked")

    bpy.context.window_manager.progress_update(40)

    #Roughness. We need to config source materials, config target material, config bake settings, bake
    print("Baking roughness")
    bake_utils.config_source_materials(bake_utils.BakeType.ROUGHNESS, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.ROUGHNESS, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.ROUGHNESS)
    bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
    print("Roughness baked")

    bpy.context.window_manager.progress_update(60)

    #Metalness. We need to config source materials, config target material, config bake settings, bake
    print("Baking metalness")
    bake_utils.config_source_materials(bake_utils.BakeType.METALNESS, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.METALNESS, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.METALNESS)
    bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
    print("Metalness baked")

    bpy.context.window_manager.progress_update(80)

    #Lit. We need to config source materials, config target material, config bake settings, bake
    print("Baking lit")
    bake_utils.config_source_materials(bake_utils.BakeType.LIT, mats)
    bake_utils.config_target_bake_texture(bpy.context.view_layer.objects.active, bake_utils.BakeType.LIT, bpy.context.scene.xp_ext.low_poly_bake_resolution * bpy.context.scene.xp_ext.low_poly_bake_ss_factor)
    bake_utils.config_bake_settings(bake_utils.BakeType.LIT)
    bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
    print("Lit baked")

    bpy.context.window_manager.progress_update(95)

    #Now save and merge out of process
    bake_utils.save_baked_textures(bpy.context.view_layer.objects.active)

    bpy.context.window_manager.progress_update(99)

    #Now revert all the materials
    print("Reverting materials")
    bake_utils.reset_source_materials(mats)

    #Now set the material for the low poly to the baked material
    print("Setting low poly material")
    bake_utils.config_target_object_with_new_textures(bpy.context.view_layer.objects.active)

    bpy.context.window_manager.progress_end()

    #Done
    print("Done!")

    