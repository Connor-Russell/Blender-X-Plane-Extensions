#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide a test to import various objects and compare them to a previously imported known good obj

import bpy
import os
import sys

# Add the directory containing this script to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import test_helpers

def test(test_dir):
    relative_test_dir = "Polygon Import Tests"

    failed_count = 0
    total_count = 0
    differences = []

    test_helpers.add_test_category("Import Polygon Tests")

    #Get all the .blend files in the test directory
    try:
        import_pols = []
        for root, dirs, files in os.walk(os.path.join(test_dir, relative_test_dir)):
            for file in files:
                if file.endswith(".blend"):
                    import_pols.append(os.path.join(root, file))
    except Exception as e:
        test_helpers.add_test_name("Import Polygon Test Error")
        test_helpers.append_test_fail("Error finding .blend files: " + str(e))
        return

    #For each blender file open it, import the associated .pol (same base file name), then compare the two collections in the scene
    for pol_file in import_pols:
        #Get the base name of the file without extension
        base_name = os.path.splitext(os.path.basename(pol_file))[0]
        pol_import_path = os.path.join(test_dir, relative_test_dir, base_name + ".pol")

        test_helpers.add_test_name(base_name)

        try:
            #Open the .blend file
            bpy.ops.wm.open_mainfile(filepath=pol_file)
            total_count += 1

            #Import the .pol file
            try:
                bpy.ops.xp_ext.test_import_pol(import_path=pol_import_path)

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

                differences.extend(test_helpers.compare_collections(col1, col2))
                differences.extend(test_helpers.compare_property_groups(col1.xp_pol, col2.xp_pol))

            except Exception as e:
                differences += f"Error importing {base_name}: {str(e)}\n"
                failed_count += 1

            if len(differences) > 0:
                failed_count += 1

            test_helpers.append_test_results(
                len(differences) == 0,
                100.0 if len(differences) == 0 else 0.0,
                f"Imported {base_name} with {len(differences)} differences: {differences}"
            )

            differences = []
        except Exception as e:
            print(f"Error processing {pol_file}: {str(e)}")
            failed_count += 1
            test_helpers.append_test_fail(os.path.splitext(os.path.basename(pol_file))[0])

    test_helpers.add_test_name("Polygon Importer Summary")
    test_helpers.append_test_results(
        failed_count == 0,
        100.0 if failed_count == 0 else (1 - (failed_count / total_count)) * 100,
        f"Total tests: {total_count}, Failed: {failed_count}"
    )


#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    test_dir = os.path.dirname(bpy.data.filepath)

    test(test_dir)

