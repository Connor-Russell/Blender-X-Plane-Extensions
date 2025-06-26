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

#Function that compares each byte of two files to check how similar the files are. Returns a value 0-1 for 0% to 100% similarity.
def compare_images(file1, file2):
    """
    Compares two images and returns a similarity ratio (0-1).
    """
    try:
        print("Loading images...")
        img1 = bpy.data.images.load(file1)
        img2 = bpy.data.images.load(file2)

        # Check if the images are the same size
        if img1.size[0] != img2.size[0] or img1.size[1] != img2.size[1]:
            print("Images are not the same size.")
            return 0

        # Convert pixel data to NumPy arrays
        pixels1 = np.array(img1.pixels[:])
        pixels2 = np.array(img2.pixels[:])

        # Calculate the absolute difference between the two images
        #I... don't actually know why this works. But the results *appear* right and Github Copilot told me to soooo...
        #If python wasn't SOOOOOOOOOOOOOOOO SLOW I'd do this with a simple nested for *cries in c++*
        diff = np.abs(pixels1 - pixels2)

        # Calculate the similarity ratio
        total_pixels = len(pixels1)
        similarity = 1 - (np.sum(diff) / total_pixels)

        print("Images compared.")
        return max(0, similarity)  # Ensure similarity is not negative

    except Exception as e:
        print(f"Error comparing images: {e}")
        return 0

def test(test_dir):

    error_messages = ""

    albedo_similarity = 0
    normal_similarity = 0
    lit_similarity = 0

    test_helpers.add_test_category("Bake Tests")

    #Bake
    try:

        # Sometimes Blender tries to change the name to .000 (or similar). This *seems* to be a bug in their unique name code since there's no actual conflict
        # But that's not super important to the core plugin so we have this bandaid
        for col in bpy.data.collections:
            if col.name.startswith("BakeTest."):
                col.name = "BakeTest"

        #Set params
        bpy.context.scene.xp_ext.low_poly_bake_resolution = 256
        bpy.context.scene.xp_ext.low_poly_bake_ss_factor = 2

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
        albedo_similarity = compare_images(test_albedo, known_good_albedo)
        normal_similarity = compare_images(test_normal, known_good_normal)
        lit_similarity = compare_images(test_lit, known_good_lit)

        #Rename the test result images to _version.test_result.png so they are ignored by git
        blender_version = bpy.app.version_string.split(".")
        blender_version = blender_version[0] + blender_version[1]
        test_albedo = test_albedo.replace(".png", "_" + blender_version + ".test_result.png")
        test_normal = test_normal.replace(".png", "_" + blender_version + ".test_result.png")
        test_lit = test_lit.replace(".png", "_" + blender_version + ".test_result.png")
        if os.path.exists(test_albedo):
            os.remove(test_albedo)
        if os.path.exists(test_normal):
            os.remove(test_normal)
        if os.path.exists(test_lit):
            os.remove(test_lit)
    except Exception as e:
        error_messages += "Image comparison failed: " + str(e) + "\n"

    test_helpers.add_test_name("Bake Test Albedo")
    test_helpers.append_test_results(
        albedo_similarity > 0.98,
        albedo_similarity * 100,
        error_messages
    )

    test_helpers.add_test_name("Bake Test Normal")
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

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    #The test dir is the parent of the blender file path. THis is just so we don't have to deal with passing in an extra argument, or hard coding the path in every test tilf
    test_dir = bpy.data.filepath.rsplit("\\", 1)[0]

    test(test_dir)
    


