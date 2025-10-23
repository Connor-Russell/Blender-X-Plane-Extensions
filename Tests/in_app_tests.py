#Project: in-app_tests.py
#Author: Connor Russell
#Date: 9/22/2025
#Module: in_app_tests.py
#Purpose: Provide a standardized way to perform in-app tests
#Usage: In app tests are added to tests list. Provide a test name a .blend file path (relative to the test dir), and a function to call. Your function will be called with these params and can do it's testing how it likes

import bpy
import os
import sys


# Add the directory containing this script to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import test_helpers
import in_app_anim_tool_test

test_dir = ""

def run_inapp_test(test_name, filepath, test_func):
    """
    Run the in-app import test for a given file.
    Args:
        filepath (str): The path to the blender file
    """
    try:
        #Open the test
        test_helpers.add_test_name("test_name:")

        #Open the .blend file
        try:
            bpy.ops.wm.open_mainfile(filepath=os.path.join(test_dir, filepath))
        except Exception as e:
            if "File written by newer" in str(e):
                pass
            else:
                raise

        #Get two collections, the one starting in "Start" and the one starting in "End". We operate on start, then compare to end
        start_col = None
        end_col = None

        for col in bpy.data.collections:
            if col.name.startswith("Start"):
                start_col = col
            elif col.name.startswith("End"):
                end_col = col

        #Make sure we got both collections
        if start_col is None or end_col is None:
            raise ValueError("Could not find both 'Start' and 'End' collections in the scene. Ensure the .blend file has these collections.")
        
        #Call the test function, passing in the start collection
        test_func(start_col)

        #Compare the start and end collections
        differences = test_helpers.compare_collections(start_col, end_col)

        if len(differences) == 0:
            test_helpers.append_test_results(True, 100, "")
        else:
            test_helpers.append_test_results(False, 0, test_helpers.differences_to_string(differences))

    except Exception as e:
        test_helpers.append_test_fail(str(e))
        return

    finally:
        #Close the file
        bpy.ops.wm.read_factory_settings(use_empty=True)

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    test_dir = os.getcwd()  + os.sep + "Content"
    print("In-app test dir: " + test_dir)

    tests = [
        ["Auto Keyframe Test", "Autokeyframe.blend", in_app_anim_tool_test.inapp_autokeyframe_test],
        ["Flipbook Test", "Flipbook.blend", in_app_anim_tool_test.inapp_flipbook_test]
    ]

    for test in tests:
        try:
            run_inapp_test(test[0], test[1], test[2])
        except Exception as e:
            print("Fatal error in inapp test: " + str(e))
