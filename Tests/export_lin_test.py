#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple single function call to open a blender file, call the export function, and compare it with a known good file

import bpy
import sys
import os

#Function that compares each byte of two files to check how similar the files are. Returns a value 0-1 for 0% to 100% similarity.
def compare_files(file1, file2):
    b_pass = True
    chr_same = 0
    chr_total = 0
    similarity = 0.0
    
    try:
        with open(file1, 'r') as new, open(file2, 'r') as good:
            f_new = new.read()
            f_good = good.read()

            #Iterate over each line in both file. Then compare the characters in each line one by one
            new_lines = f_new.splitlines()
            good_lines = f_good.splitlines()

            for i in range(min(len(new_lines), len(good_lines))):
                new_line_len = len(new_lines[i])
                good_line_len = len(good_lines[i])

                for j in range(min(new_line_len, good_line_len)):
                    chr_total += 1
                    if new_lines[i][j] == good_lines[i][j]:
                        chr_same += 1
                
                chr_total += abs(new_line_len - good_line_len)
                
        
        similarity = chr_same / chr_total
        similarity *= (abs(len(new_lines) - len(good_lines)) / max(len(new_lines) - len(good_lines)))
    except:
        pass

    return similarity

def test(test_dir):
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
        similarity = compare_files(new_file, known_good_file)
    except Exception as e:
        error_message = str(e)
        pass

    if similarity < 1.0:
        b_pass = False

    #Append the test results to the exporter_output file
    with open(exporter_output, 'a') as output:
        if b_pass:
            output.write("Line Exporter,PASS," + "{:.{precision}f}".format(similarity * 100, precision=4) + "% " + error_message + "\n")
        else:
            output.write("Line Exporter,FAIL," + "{:.{precision}f}".format(similarity * 100, precision=4) + "% " + error_message + "\n")

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    #The test dir is the parent of the blender file path. THis is just so we don't have to deal with passing in an extra argument, or hard coding the path in every test tilf
    test_dir = os.path.dirname(bpy.data.filepath)

    test(test_dir)


