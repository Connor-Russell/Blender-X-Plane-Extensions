#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple single function call to open a blender file, call the export function, and compare it with a known good file

import bpy
import sys
import os

def test(test_dir):
    # Add the directory containing this script to sys.path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    import test_helpers

    b_pass = False
    similarity = 0.0
    error_message = ""
    exporter_output = test_dir + "/../Test Results.csv"
    try:

        new_file_name = "Exporter_" + str(bpy.app.version[0]) + str(bpy.app.version[1]) + ".test_result.lin"
        new_file = test_dir + "/" + new_file_name

        if os.path.exists(new_file):
            os.remove(new_file)

        for col in bpy.data.collections:
            if col.xp_lin.exportable:
                if col.xp_lin.name == "Exporter.lin":
                    col.xp_lin.name = new_file_name

        print("Exporting Line")
        bpy.ops.xp_ext.export_lines()

        known_good_file = test_dir + "/Exporter.good.lin"

        #Resolve the file paths to use \\ instead of / for windows compatibility
        new_file = new_file.replace("/", "\\")
        known_good_file = known_good_file.replace("/", "\\")

        print("Comparing files" + new_file + " and " + known_good_file)

        #Compare the exported file with the known good file
        b_pass = True
        line_diff_count, similarity = test_helpers.compare_files(new_file, known_good_file)
    except Exception as e:
        error_message = str(e)
        pass

    if similarity < 1.0:
        b_pass = False

    test_helpers.append_test_results(
        "Line Exporter",
        b_pass,
        similarity * 100,
        error_message
    )

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    #The test dir is the parent of the blender file path. THis is just so we don't have to deal with passing in an extra argument, or hard coding the path in every test tilf
    test_dir = os.path.dirname(bpy.data.filepath)

    try:
        test(test_dir)
    except Exception as e:
        test_output = test_dir + "/../Test Results.csv"

        with open(test_output, 'a') as output:
            output.write("Line Exporter,FAIL,Critical error: " + str(e) + "\n")


