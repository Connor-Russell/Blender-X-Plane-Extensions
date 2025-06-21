#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide a test to import various lins and compare them to the existing imported .lin

import bpy
import os
import sys

def test(test_dir):
    # Add the directory containing this script to sys.path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    import test_helpers

    relative_test_dir = "LineImportTests"

    failed_count = 0
    error_messages = ""

    #Get all the .blend files in the test directory
    import_lins = []
    for root, dirs, files in os.walk(os.path.join(test_dir, relative_test_dir)):
        for file in files:
            if file.endswith(".blend"):
                import_lins.append(os.path.join(root, file))

    #For each blender file open it, import the associated .lin (same base file name), then compare the two collections in the scene
    for lin_file in import_lins:
        #Get the base name of the file without extension
        base_name = os.path.splitext(os.path.basename(lin_file))[0]
        lin_import_path = os.path.join(test_dir, relative_test_dir, base_name + ".lin")

        #Open the .blend file
        bpy.ops.wm.open_mainfile(filepath=lin_file)

        #Import the .lin file
        try:
            bpy.ops.TEST_import_lin(import_path=lin_import_path)
        except Exception as e:
            error_messages += f"Error importing {base_name}: {str(e)}\n"
            failed_count += 1
            continue

        col1 = None
        col2 = None
        for i, col in enumerate(bpy.data.collections):
            if i == 0:
                col1 = col
            elif i == 1:
                col2 = col
                break

        if col1 is None or col2 is None:
            test_helpers.append_test_results(
                "Line Importer",
                False,
                0.0,
                f"Failed to find two collections in {base_name} after import."
            )
            continue

        differences = test_helpers.compare_collections(col1, col2)
        
        test_helpers.append_test_results(
            "Line Importer",
            len(differences) == 0,
            100.0 if len(differences) == 0 else 0.0,
            f"Imported {base_name} with {len(differences)} differences: {differences}"
        )            
            


#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    test_dir = os.path.dirname(bpy.data.filepath)

    test(test_dir)

