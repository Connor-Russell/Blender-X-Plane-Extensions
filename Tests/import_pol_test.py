#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide a test to import various objects and check if they import without error.
# Actual contents of the object are not checked currently as we do not yet have the code to compare *blender* contents, and that would require a baseline
# The primary purpose of this test is to ensure the importer code doesn't throw errors when importing any objects
# TODO: Implement a cheap check of vertex counts

import bpy
import os

def test(test_dir):
    relative_test_dir = "ImportTests"
    exporter_output = test_dir + "/../Test Results.csv"

    failed_count = 0
    error_messages = ""

    #Get all the .obj files in the test directory
    import_pols = []
    for root, dirs, files in os.walk(os.path.join(test_dir, relative_test_dir)):
        for file in files:
            if file.endswith(".pol"):
                import_pols.append(os.path.join(root, file))

    for pol in import_pols:
        try:
            bpy.ops.xp_ext.test_import_pol(import_path=pol)
        except Exception as e:
            failed_count += 1
            error_messages += (f"Failed to import {pol}: {str(e)},")
            continue

    with open(exporter_output, 'a') as output:
        if failed_count == 0:
            output.write(f"Polygon Importer,PASS,Imported {len(import_pols)} polygons\n")
        else:
            output.write("Polygon Importer,FAIL," + f"Failed to import {failed_count} of {len(import_pols)} objects with errors: " + error_messages + "\n")


#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    test_dir = os.path.dirname(bpy.data.filepath)

    try:
        test(test_dir)
    except Exception as e:
        test_output = test_dir + "/../Test Results.csv"

        with open(test_output, 'a') as output:
            output.write("Polygon Importer,FAIL,Critical error: " + str(e) + "\n")
