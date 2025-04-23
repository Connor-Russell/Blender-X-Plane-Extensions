#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple single function call to open a blender file, call the export function, and compare it with a known good file

import bpy
import sys
import argparse

def test(test_dir):
    b_pass = False

    exporter_output = test_dir + "/Test Results.csv"

    #Append the test results to the exporter_output file
    with open(exporter_output, 'a') as output:
        if b_pass:
            output.write("<test name>,PASS\n")
        else:
            output.write("<test name>,FAIL\n")

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    #Parse the command line arguments
    try:
        for i in range(len(sys.argv)):
            if sys.argv[i] == "--test-dir":
                test_dir = sys.argv[i+1]
    except:
        print("Error parsing command line arguments")
        sys.exit(1)

    test(test_dir)


