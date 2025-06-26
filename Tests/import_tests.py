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
    relative_test_dir = "Import Tests"

    failed_count = 0
    total_count = 0

    import_files = []

    test_helpers.add_test_category("Import Tests")

    #Get all the .blend files in the test directory
    try:
        import_files = []
        for root, dirs, files in os.walk(os.path.join(test_dir, relative_test_dir)):
            for file in files:
                if file.endswith(".blend"):
                    import_files.append(os.path.join(root, file))
    except Exception as e:
        test_helpers.add_test_name("Import Test Error")
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
                if col.xp_fac.exportable or col.xp_pol.exportable or col.xp_lin.exportable or col.xp_agp.exportable or col.xplane.is_exportable_collection:
                    col1 = col

            asset_import_path = os.path.join(parent_folder, col1.name)
            asset_extension = os.path.splitext(asset_import_path)[1].lower()

            if os.path.exists(asset_import_path) is False:
                raise FileNotFoundError(f"Asset file not found: {asset_import_path}")

            if asset_extension == '.fac':
                bpy.ops.xp_ext.test_import_fac(import_path=asset_import_path)
            elif asset_extension == '.obj':
                bpy.ops.xp_ext.test_import_obj(import_path=asset_import_path)
            elif asset_extension == '.pol':
                bpy.ops.xp_ext.test_import_pol(import_path=asset_import_path)
            elif asset_extension == '.lin':
                bpy.ops.xp_ext.test_import_lin(import_path=asset_import_path)
            elif asset_extension == '.agp':
                bpy.ops.xp_ext.test_import_agp(import_path=asset_import_path)
            
            #Now we will get the two collections
            col1 = None
            col2 = None
        
            for i, col in enumerate(bpy.data.collections):
                if col.xp_fac.exportable or col.xp_pol.exportable or col.xp_lin.exportable or col.xp_agp.exportable or col.xplane.is_exportable_collection:
                    if col1 is None:
                        col1 = col
                    elif col2 is None:
                        col2 = col
                        break

            #Make sure we have two collections
            if col1 is None or col2 is None:
                raise ValueError(f"Failed to find two collections in {base_name} after import.")
            
            #Compare the two collections
            differences = test_helpers.compare_collections(col1, col2)

            if len(differences) > 0:
                failed_count += 1

            #Define a map to hold the differences, that way we can summarize them
            differences_map = {}
            for diff in differences:
                if diff.category not in differences_map:
                    differences_map[diff.category] = []
                differences_map[diff.category].append(diff.message)
                print(f"Difference found in {base_name}: {diff.category} - {diff.message}")

            #Define a summary string
            differences_summary = "Differences: "
            for diff_category in differences_map.keys():
                differences_summary += f"{diff_category}: {len(differences_map[diff_category])} "

            for diff_category in differences_map.keys():
                differences_summary += f"\n{diff_category}: "
                for message in differences_map[diff_category]:
                    differences_summary += f"{message} "

            test_helpers.append_test_results(len(differences) == 0,
                100.0 if len(differences) == 0 else 0.0,
                differences_summary
            )

        except Exception as e:
            test_helpers.append_test_fail(f"Error importing {base_name}: {str(e)}")
            failed_count += 1
            continue

    test_helpers.add_test_name("Import Test Summary")
    test_helpers.append_test_results(
        failed_count == 0,
        100.0 if failed_count == 0 else (1 - (failed_count / total_count)) * 100,
        f"Total tests: {total_count}, Failed: {failed_count}"
    )
        

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    test_dir = os.path.dirname(bpy.data.filepath)

    test(test_dir)
