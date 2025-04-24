#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple single function call to open a blender file, call the export function, and compare it with a known good file

import bpy
import sys
import os

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    #Call the internal test function
    bpy.ops.xp_ext.run_tests()
