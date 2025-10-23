#Project: Blender-X-Plane-Extensions
#Author: Connor Russell
#Date: 10/6/2025
#Module: normal_conversion.py
#Purpose: Tests the conversion of combined normal maps to separate normal maps and back.

import bpy
import os
import sys

# Add the directory containing this script to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import test_helpers

def test(test_dir):
    test_helpers.add_test_name("Normal Map Conversion Test")

    #Iterate throuh all the materials. Get the first name
    target_mat_name = ""

    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for mat_slot in obj.material_slots:
            if mat_slot.material is not None:
                target_mat_name = mat_slot.material.name
                break
        if target_mat_name != "":
            break

    #Invoke the operator, with the name of the material for it's "material_name" property
    bpy.ops.xp_ext.convert_combined_xp_nml_to_separate(material_name=target_mat_name)

    #Now we will do the combine operation
    bpy.ops.xp_ext.convert_separate_maps_to_combined_xp_nml(material_name=target_mat_name)

    #Now from that material, get the normal texture
    nml_texture = bpy.data.materials[target_mat_name].xp_materials.normal_texture
    nml_texture = bpy.path.abspath(nml_texture)

    #Now define the known good as .good.png
    good_nml_texture = nml_texture
    good_nml_texture = good_nml_texture.replace(".png", ".good.png")
    print("Comparing generated normal map: " + nml_texture + " with known good: " + good_nml_texture)

    #Now compare the two images
    similiarity = test_helpers.compare_images(nml_texture, good_nml_texture)

    test_helpers.append_test_results(similiarity > 0.98, similiarity * 100, "")

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    test_dir = os.getcwd() + os.sep + "Content"
    print("Normal Conversion Test directory: " + test_dir)

    #Open the bake file
    bake_file = test_dir + os.sep + "NormalConversionTest.blend"
    try:
        bpy.ops.wm.open_mainfile(filepath=bake_file)
    except Exception as e:
        #Check if this is the "newer Blender" error - if so, ignore it, it's expected
        if "newer Blender" in str(e):
            pass
        else:
            test_helpers.add_test_category("Normal Map Conversion Test")
            test_helpers.append_test_fail("Failed to open normal conversion test file: " + str(e))

    try:
        test(test_dir)
    except Exception as e:
        print("Fatal error in import tests: " + str(e))
