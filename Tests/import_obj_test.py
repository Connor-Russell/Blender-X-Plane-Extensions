#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide a test to import various objects and compare them to a previously imported known good obj

import bpy
import os
import sys

def test(test_dir):
    # Add the directory containing this script to sys.path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    import test_helpers

    relative_test_dir = "Object Import Tests"

    failed_count = 0
    total_count = 0
    differences = []

    #Get all the .blend files in the test directory
    import_objs = []
    for root, dirs, files in os.walk(os.path.join(test_dir, relative_test_dir)):
        for file in files:
            if file.endswith(".blend"):
                import_objs.append(os.path.join(root, file))

    #For each blender file open it, import the associated .fac (same base file name), then compare the two collections in the scene
    for obj_file in import_objs:
        #Get the base name of the file without extension
        base_name = os.path.splitext(os.path.basename(obj_file))[0]
        obj_import_path = os.path.join(test_dir, relative_test_dir, base_name + ".obj")

        #Open the .blend file
        bpy.ops.wm.open_mainfile(filepath=obj_file)
        total_count += 1

        #Import the .obj file
        try:
            bpy.ops.xp_ext.test_import_obj(import_path=obj_import_path)

            col1 = None
            col2 = None
            for i, col in enumerate(bpy.data.collections):
                if i == 0:
                    col1 = col
                elif i == 1:
                    col2 = col
                    break

            if col1 is None or col2 is None:
                raise ValueError(f"Failed to find two collections in {base_name} after import.")
                continue

            differences.extend(test_helpers.compare_collections(col1, col2))
            differences.extend(test_helpers.compare_property_groups(col1.xplane, col2.xplane))

        except Exception as e:
            differences += f"Error importing {base_name}: {str(e)}\n"
            failed_count += 1

        if len(differences) > 0:
            failed_count += 1
        
        test_helpers.append_test_results(
            f"Object Importer {base_name}",
            len(differences) == 0,
            100.0 if len(differences) == 0 else 0.0,
            f"Imported {base_name} with {len(differences)} differences: {differences}"
        )

        differences = []
    
    test_helpers.append_test_results(
        "Object Importer Summary",
        failed_count == 0,
        100.0 if failed_count == 0 else (1 - (failed_count / total_count)) * 100,
        f"Total tests: {total_count}, Failed: {failed_count}"
    )


#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    test_dir = os.path.dirname(bpy.data.filepath)

    test(test_dir)

