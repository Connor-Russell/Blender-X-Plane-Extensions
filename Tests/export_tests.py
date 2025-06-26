#Project: BlenderImportTests
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide a test to import various assets and compare them to previously imported known good assets

import bpy
import os
import sys

# Add the directory containing this script to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import test_helpers

def test(test_dir):
    relative_test_dir = "Export Tests"

    failed_count = 0
    total_count = 0

    import_files = []

    test_helpers.add_test_category("Export Tests")

    #Get all the .blend files in the test directory
    try:
        import_files = []
        for root, dirs, files in os.walk(os.path.join(test_dir, relative_test_dir)):
            for file in files:
                if file.endswith(".blend"):
                    import_files.append(os.path.join(os.path.join(test_dir, relative_test_dir), file))
    except Exception as e:
        test_helpers.add_test_name("Export Test Error")
        test_helpers.append_test_fail("Error finding .blend files: " + str(e))
        return
    
    for import_file in import_files:
        #Define the file name, and the parent folder
        base_name = os.path.splitext(os.path.basename(import_file))[0]
        parent_folder = os.path.dirname(import_file)

        test_helpers.add_test_name(base_name)
        total_count += 1

        try:
            #Open the .blend file
            bpy.ops.wm.open_mainfile(filepath=import_file)

            #Get the first collection. Then we'll get the path of the asset to import from the collection name
            if len(bpy.data.collections) < 1:
                raise ValueError("No collections found in the scene. Ensure the .blend file has a collection with the asset name.")

            col1 = None
            for col in bpy.data.collections:
                if col.xp_fac.exportable or col.xp_pol.exportable or col.xp_lin.exportable or col.xp_agp.exportable:
                    col1 = col

            if col1 is None:
                raise ValueError("No valid collections found in the scene. Ensure the .blend file has a collection with the asset name and extension.")

            #Define the output path, should be parent_folder + collection name (minus extension) + blender version + .good + (extension)
            col_name = col1.name
            col_name_split = col_name.split(".")
            if len(col_name_split) < 2:
                raise ValueError(f"Collection name '{col_name}' does not contain a valid extension. Expected format: 'name.extension'.")
            col_name_base = col_name_split[0]  # Get the name from the collection name
            col_name_ext = col_name_split[1]  # Get the extension from the collection name


            output_path = os.path.join(parent_folder, f"{col_name_base}.{bpy.app.version_string}.{col_name_ext}")
            output_path_name = os.path.basename(output_path)

            #Set the export path
            col.xp_fac.name = output_path_name
            col.xp_pol.name = output_path_name
            col.xp_lin.name = output_path_name
            col.xp_agp.name = output_path_name

            #Define the "good" file to compare to
            good_file = os.path.join(test_dir, relative_test_dir, f"{col_name_base}.good.{col_name_ext}")
            if not os.path.exists(good_file):
                raise FileNotFoundError(f"Good file not found: {good_file}. Ensure the test directory contains the expected good files.")
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Output file was not created: {output_path}")

            #Call the export operators. We'll just call them all, those that aren't applicable will simply do nothing
            bpy.ops.xp_ext.export_lines()
            bpy.ops.xp_ext.export_polygons()
            bpy.ops.xp_ext.export_facades()
            bpy.ops.xp_ext.export_agps()

            #Compare the two files
            line_diff, similarity = test_helpers.compare_files(output_path, good_file)

            if similarity < 0.98:
                failed_count += 1

            test_helpers.append_test_results(similarity >= 0.98, similarity * 100, 
                f"Different line count {line_diff}")

        except Exception as e:
            print(f"Error importing {base_name}: {str(e)}")
            test_helpers.append_test_fail(f"Error importing {base_name}: {str(e)}")
            failed_count += 1
            continue

    test_helpers.add_test_name("Export Test Summary")
    test_helpers.append_test_results(
        failed_count == 0,
        100.0 if failed_count == 0 else (1 - (failed_count / total_count)) * 100,
        f"Total tests: {total_count}, Failed: {failed_count}"
    )
        

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    test_dir = os.path.dirname(bpy.data.filepath)

    test(test_dir)
