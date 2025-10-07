#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple single function call to open a blender file, call the export function, and compare it with a known good file

import bpy
import sys
import os
import numpy as np

# Add the directory containing this script to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import test_helpers

def test_combined(test_dir):

    error_messages = ""

    albedo_similarity = 0
    normal_similarity = 0
    lit_similarity = 0

    test_helpers.add_test_category("Bake Tests")

    bpy.context.scene.xp_ext.low_poly_bake_do_alb = False
    bpy.context.scene.xp_ext.low_poly_bake_do_opacity = False
    bpy.context.scene.xp_ext.low_poly_bake_do_nrm = True
    bpy.context.scene.xp_ext.low_poly_bake_do_mat = True
    bpy.context.scene.xp_ext.low_poly_bake_do_lit = False
    bpy.context.scene.xp_ext.low_poly_bake_margin = 2
    bpy.context.scene.xp_ext.low_poly_bake_extrusion_distance = 0.1
    bpy.context.scene.xp_ext.low_poly_bake_resolution = 256
    bpy.context.scene.xp_ext.low_poly_bake_ss_factor = 2
    bpy.context.scene.xp_ext.low_poly_bake_max_ray_distance = 0.0
    bpy.context.scene.xp_ext.low_poly_bake_do_separate_normals = True

    #Bake
    try:

        # Sometimes Blender tries to change the name to .000 (or similar). This *seems* to be a bug in their unique name code since there's no actual conflict
        # But that's not super important to the core plugin so we have this bandaid
        for col in bpy.data.collections:
            if col.name.startswith("BakeTest."):
                col.name = "BakeTest"

        #File Paths
        known_good_albedo = test_dir + "/BakeTest_LOD.good.png"
        known_good_normal = test_dir + "/BakeTest_LOD_NML.good.png"
        known_good_lit = test_dir + "/BakeTest_LOD_LIT.good.png"

        test_albedo = test_dir + "/BakeTest_LOD.png"
        test_normal = test_dir + "/BakeTest_LOD_NML.png"
        test_lit = test_dir + "/BakeTest_LOD_LIT.png"

        #Delete existing images
        if os.path.exists(test_albedo):
            os.remove(test_albedo)
        if os.path.exists(test_normal):
            os.remove(test_normal)
        if os.path.exists(test_lit):
            os.remove(test_lit)
    
        bpy.ops.xp_ext.bake_low_poly()
    except Exception as e:
        error_messages += "Bake failed: " + str(e) + "\n"

    #Compare the images
    try:
        albedo_similarity = test_helpers.compare_images(test_albedo, known_good_albedo)
        normal_similarity = test_helpers.compare_images(test_normal, known_good_normal)
        lit_similarity = test_helpers.compare_images(test_lit, known_good_lit)

        #Rename the test result images to _version.test_result.png so they are ignored by git
        blender_version = bpy.app.version_string.split(".")
        blender_version = blender_version[0] + blender_version[1]
        save_test_albedo = test_albedo.replace(".png", "_" + blender_version + ".test_result.png")
        save_test_normal = test_normal.replace(".png", "_" + blender_version + ".test_result.png")
        save_test_lit = test_lit.replace(".png", "_" + blender_version + ".test_result.png")
        if os.path.exists(save_test_albedo):
            os.remove(save_test_albedo)
        if os.path.exists(save_test_normal):
            os.remove(save_test_normal)
        if os.path.exists(save_test_lit):
            os.remove(save_test_lit)

        #Rename the test result images
        os.rename(test_albedo, save_test_albedo)
        os.rename(test_normal, save_test_normal)
        os.rename(test_lit, save_test_lit)
    except Exception as e:
        error_messages += "Image comparison failed: " + str(e) + "\n"

    test_helpers.add_test_name("Bake Test Albedo")
    test_helpers.append_test_results(
        albedo_similarity > 0.98,
        albedo_similarity * 100,
        error_messages
    )

    test_helpers.add_test_name("Bake Test Combined Normal")
    test_helpers.append_test_results(
        normal_similarity > 0.98,
        normal_similarity * 100,
        error_messages
    )

    test_helpers.add_test_name("Bake Test Lit")
    test_helpers.append_test_results(
        lit_similarity > 0.98,
        lit_similarity * 100,
        error_messages
    )

def test_separate(test_dir):

    error_messages = ""

    normal_similarity = 0
    material_similarity = 0

    bpy.context.scene.xp_ext.low_poly_bake_do_alb = False
    bpy.context.scene.xp_ext.low_poly_bake_do_opacity = False
    bpy.context.scene.xp_ext.low_poly_bake_do_nrm = False
    bpy.context.scene.xp_ext.low_poly_bake_do_mat = False
    bpy.context.scene.xp_ext.low_poly_bake_do_lit = False
    bpy.context.scene.xp_ext.low_poly_bake_margin = 2
    bpy.context.scene.xp_ext.low_poly_bake_extrusion_distance = 0.1
    bpy.context.scene.xp_ext.low_poly_bake_resolution = 256
    bpy.context.scene.xp_ext.low_poly_bake_ss_factor = 2
    bpy.context.scene.xp_ext.low_poly_bake_max_ray_distance = 0.0
    bpy.context.scene.xp_ext.low_poly_bake_do_separate_normals = True

    #Bake
    try:

        # Sometimes Blender tries to change the name to .000 (or similar). This *seems* to be a bug in their unique name code since there's no actual conflict
        # But that's not super important to the core plugin so we have this bandaid
        for col in bpy.data.collections:
            if col.name.startswith("BakeTest."):
                col.name = "BakeTest"

        #File Paths
        known_good_normal = test_dir + "/BakeTest_LOD_NML.good.png"
        known_good_material = test_dir + "/BakeTest_LOD_MAT.good.png"

        test_normal = test_dir + "/BakeTest_LOD_NRM.png"
        test_material = test_dir + "/BakeTest_LOD_MAT.png"

        #Delete existing images
        if os.path.exists(test_normal):
            os.remove(test_normal)
        if os.path.exists(test_material):
            os.remove(test_material)
    
        bpy.ops.xp_ext.bake_low_poly()
    except Exception as e:
        error_messages += "Bake failed: " + str(e) + "\n"

    #Compare the images
    try:
        normal_similarity = test_helpers.compare_images(test_normal, known_good_normal)
        material_similarity = test_helpers.compare_images(test_material, known_good_material)

        #Rename the test result images to _version.test_result.png so they are ignored by git
        blender_version = bpy.app.version_string.split(".")
        blender_version = blender_version[0] + blender_version[1]
        save_test_normal = test_normal.replace(".png", "_" + blender_version + ".test_result.png")
        save_test_material = test_material.replace(".png", "_" + blender_version + ".test_result.png")
        if os.path.exists(save_test_normal):
            os.remove(save_test_normal)
        if os.path.exists(save_test_material):
            os.remove(save_test_material)

        #Rename the test result images
        os.rename(test_normal, save_test_normal)
        os.rename(test_material, save_test_material)
    except Exception as e:
        error_messages += "Image comparison failed: " + str(e) + "\n"


    test_helpers.add_test_name("Bake Test Normal")
    test_helpers.append_test_results(
        normal_similarity > 0.98,
        normal_similarity * 100,
        error_messages
    )

    test_helpers.add_test_name("Bake Test Material")
    test_helpers.append_test_results(
        material_similarity > 0.98,
        material_similarity * 100,
        error_messages
    )

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    #The test dir is the parent of the blender file path. THis is just so we don't have to deal with passing in an extra argument, or hard coding the path in every test tilf
    test_dir = os.getcwd()

    test(test_dir)
    


