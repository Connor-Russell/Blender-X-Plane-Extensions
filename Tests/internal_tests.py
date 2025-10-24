#Project: Blender X-Plane Extensions
#Author: Connor Russell
#Date: 11/9/2024
#Module: internal_tests.py
#Purpose: Provide a call to the internal test operators. This will likely be phased out for in_app_test.py

import bpy
import sys
import os

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    #Call the internal test function
    bpy.ops.xp_ext.run_tests()
