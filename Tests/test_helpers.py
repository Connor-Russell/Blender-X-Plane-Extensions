#Project: Blender-X-Plane-Extensions
#Date: 6/20/2025
#Author: Connor Russell
#Module: Test Helpers
#Purpose: Provide functions helpful for testing the addon

import csv
import bpy
from ..io_scene_xplane_ext.Helpers import geometery_utils

#Function that compares each byte of two files to check how similar the files are. Returns a value 0-1 for 0% to 100% similarity.
def compare_files(file1, file2):
    """
    Compare two files byte by byte and return the line count difference and similarity ratio (0-1).
    Args:
        file1 (str): Path to the first file.
        file2 (str): Path to the second file.
    Returns:
        tuple: (line_count_diff, similarity) where similarity is a float between 0 and 1.
    """
    b_pass = True
    chr_same = 0
    chr_total = 0
    similarity = 0.0
    line_count_diff = 0
    
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
        line_count_diff = abs(len(new_lines) - len(good_lines))
    except:
        pass

    return line_count_diff, similarity

def compare_property_groups(pg1, pg2):
    """
    Recursively compare all properties in two Blender property groups, including collections and nested groups.
    Args:
        pg1, pg2: Blender PropertyGroup instances.
    Returns:
        list: List of property names that differ.
    """
    differences = []
    for prop in pg1.bl_rna.properties:
        if prop.identifier == "rna_type":
            continue
        v1 = getattr(pg1, prop.identifier)
        v2 = getattr(pg2, prop.identifier)
        if prop.is_collection:
            if len(v1) != len(v2):
                differences.append((prop.identifier))
            else:
                for i, (item1, item2) in enumerate(zip(v1, v2)):
                    sub_diffs = compare_property_groups(item1, item2)
                    for sub in sub_diffs:
                        differences.extend(sub_diffs)
        elif hasattr(prop, "fixed_type") and issubclass(prop.fixed_type, bpy.types.PropertyGroup):
            sub_diffs = compare_property_groups(v1, v2)
            for sub in sub_diffs:
                differences.append(prop.identifier)
        else:
            if v1 != v2:
                differences.append((prop.identifier))
    return differences

def compare_objects(obj1, obj2):
    """
    Compare two Blender objects for transform, property groups, geometry, materials, and children.
    Args:
        obj1, obj2: Blender objects to compare.
    Returns:
        list: List of differences found.
    """
    differences = []

    #Compare the location, rotation, and scale
    if obj1.location != obj2.location:
        differences.append((f"{obj1.name}, {obj2.name}, location"))
    if obj1.rotation_euler != obj2.rotation_euler:
        differences.append((f"{obj1.name}, {obj2.name}, rotation"))
    if obj1.scale != obj2.scale:
        differences.append((f"{obj1.name}, {obj2.name}, scale"))
    
    #Now we need to compare the matrix_world
    if obj1.matrix_world != obj2.matrix_world:
        differences.append((f"{obj1.name}, {obj2.name}, matrix_world"))

    #Now we need to compare the various property groups we care about
    differences.extend(compare_property_groups(obj1.xplane, obj2.xplane))
    differences.extend(compare_property_groups(obj1.xp_lin, obj2.xp_lin))
    differences.extend(compare_property_groups(obj1.xp_pol, obj2.xp_pol))
    differences.extend(compare_property_groups(obj1.xp_fac, obj2.xp_fac))
    differences.extend(compare_property_groups(obj1.xp_agp, obj2.xp_agp))

    #Now we need to compare the geometry/normals/UVs via 
    dc1 = geometery_utils.get_draw_call_from_obj(obj1)
    dc2 = geometery_utils.get_draw_call_from_obj(obj2)
    if dc1 != dc2:
        differences.append((f"{obj1.name}, {obj2.name}, geometry difference: {dc1} vs {dc2}"))
    
    #Now we compare the materials
    mats1 = obj1.data.materials
    mats2 = obj2.data.materials
    if len(mats1) != len(mats2):
        return False, "Different number of material slots"
    for i, (mat1, mat2) in enumerate(zip(mats1, mats2)):
        if not mat1 or not mat2:
            differences.append((f"{obj1.name}, {obj2.name}, material slot {i} is empty"))
            continue
        differences.extend(compare_property_groups(mat1.xp_materials, mat2.xp_materials))

    #Finally, we will compare the children
    children1 = obj1.children
    children2 = obj2.children
    if len(children1) != len(children2):
        differences.append((f"{obj1.name}, {obj2.name}, children count difference: {len(children1)} vs {len(children2)}"))
    else:
        for i, (child1, child2) in enumerate(zip(children1, children2)):
            if not child1 or not child2:
                differences.append((f"{obj1.name}, {obj2.name}, child slot {i} is empty"))
                continue
            differences.extend(compare_objects(child1, child2))

    return differences

def compare_collections(col1, col2):
    """
    Compare two Blender collections for properties and contained objects.
    Args:
        col1, col2: Blender collections to compare.
    Returns:
        list: List of differences found.
    """
    differences = []

    #Compare properties of the collections
    try:
        differences.extend(compare_property_groups(col1.xplane, col2.xplane))
        differences.extend(compare_property_groups(col1.xp_lin, col2.xp_lin))
        differences.extend(compare_property_groups(col1.xp_pol, col2.xp_pol))
        differences.extend(compare_property_groups(col1.xp_fac, col2.xp_fac))
        differences.extend(compare_property_groups(col1.xp_agp, col2.xp_agp))
    except Exception as e:
        differences.append((f"Error comparing properties: {str(e)}"))
        return differences
    
    if len(differences) > 0:
        return differences
    
    #Compare the objects
    try:
        objs1 = col1.objects
        objs2 = col2.objects

        if len(objs1) != len(objs2):
            differences.append((f"{col1.name}, {col2.name}, object count difference: {len(objs1)} vs {len(objs2)}"))
            return differences

        for i in range(min(len(objs1), len(objs2))):
            obj1 = objs1[i]
            obj2 = objs2[i]
            if obj1.name != obj2.name:
                differences.append((f"{obj1.name}, {obj2.name}, name difference"))
                continue
            obj_diffs = compare_objects(obj1, obj2)
            if obj_diffs:
                differences.extend(obj_diffs)
    except Exception as e:
        differences.append((f"Error comparing objects: {str(e)}"))

    #Return the results     
    return differences

def append_test_results(test_name, b_did_pass, percentage, message):
    """
    Append a test result to the 'Test Results.csv' file in the current Blender project directory.
    Args:
        test_name (str): Name of the test.
        b_did_pass (bool): Whether the test passed.
        percentage (float): Percentage score or similarity.
        message (str): Additional message or notes.
    """
    #Get path of this script
    script_path = bpy.path.abspath("//")

    #Create the CSV file if it doesn't exist
    csv_file_path = script_path + 'Test Results.csv'
    try:
        with open(csv_file_path, 'x', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Test Name', 'Did Pass?', 'Percentage', 'Message'])  # Write header
    except FileExistsError:
        pass  # File already exists, we can append to it

    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([test_name, b_did_pass, percentage, message])
