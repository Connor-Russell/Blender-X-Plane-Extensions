#Project: Blender-X-Plane-Extensions
#Date: 6/20/2025
#Author: Connor Russell
#Module: Test Helpers
#Purpose: Provide functions helpful for testing the addon

import csv
import bpy
import collections

import mathutils
import math
import os

#Simple container to hold an X-Plane Vertex
class xp_vertex:
    """
    Simple class that contains all the data for a vertex in X-Plane.
    """
    loc_x = 0
    loc_y = 0
    loc_z = 0

    normal_x = 0
    normal_y = 0
    normal_z = 0

    uv_x = 0
    uv_y = 0

    def __init__(self, loc_x, loc_y, loc_z, normal_x, normal_y, normal_z, uv_x, uv_y):
        self.loc_x = loc_x
        self.loc_y = loc_y
        self.loc_z = loc_z

        self.normal_x = normal_x
        self.normal_y = normal_y
        self.normal_z = normal_z

        self.uv_x = uv_x
        self.uv_y = uv_y

    def __eq__(self, other):
        return self.loc_x == other.loc_x and self.loc_y == other.loc_y and self.loc_z == other.loc_z and self.normal_x == other.normal_x and self.normal_y == other.normal_y and self.normal_z == other.normal_z and self.uv_x == other.uv_x and self.uv_y == other.uv_y
    
    def almost_equal(self, other, epsilon=0.0001):
        """
        Check if this vertex is almost equal to another vertex within a small epsilon tolerance.
        """
        return (math.isclose(self.loc_x, other.loc_x, abs_tol=epsilon) and
                math.isclose(self.loc_y, other.loc_y, abs_tol=epsilon) and
                math.isclose(self.loc_z, other.loc_z, abs_tol=epsilon) and
                math.isclose(self.normal_x, other.normal_x, abs_tol=epsilon) and
                math.isclose(self.normal_y, other.normal_y, abs_tol=epsilon) and
                math.isclose(self.normal_z, other.normal_z, abs_tol=epsilon) and
                math.isclose(self.uv_x, other.uv_x, abs_tol=epsilon) and
                math.isclose(self.uv_y, other.uv_y, abs_tol=epsilon))

def vectors_close(v1, v2, epsilon=0.0001):
    """
    Check if two mathutils.Vector objects are close to each other within a small epsilon tolerance.
    Args:
        v1 (mathutils.Vector): First vector.
        v2 (mathutils.Vector): Second vector.
        epsilon (float): Tolerance for comparison.
    Returns:
        bool: True if vectors are close, False otherwise.
    """
    return (math.isclose(v1.x, v2.x, abs_tol=epsilon) and
            math.isclose(v1.y, v2.y, abs_tol=epsilon) and
            math.isclose(v1.z, v2.z, abs_tol=epsilon))

def euler_close(e1, e2, epsilon=0.0001):
    """
    Check if two mathutils.Euler objects are close to each other within a small epsilon tolerance.
    Args:
        e1 (mathutils.Euler): First Euler rotation.
        e2 (mathutils.Euler): Second Euler rotation.
        epsilon (float): Tolerance for comparison.
    Returns:
        bool: True if Euler rotations are close, False otherwise.
    """
    return (math.isclose(e1.x, e2.x, abs_tol=epsilon) and
            math.isclose(e1.y, e2.y, abs_tol=epsilon) and
            math.isclose(e1.z, e2.z, abs_tol=epsilon))

def matrix_close(m1, m2, epsilon=0.0001):
    """
    Check if two mathutils.Matrix objects are close to each other within a small epsilon tolerance.
    Args:
        m1 (mathutils.Matrix): First matrix.
        m2 (mathutils.Matrix): Second matrix.
        epsilon (float): Tolerance for comparison.
    Returns:
        bool: True if matrices are close, False otherwise.
    """
    for i in range(4):
        for j in range(4):
            if not math.isclose(m1[i][j], m2[i][j], abs_tol=epsilon):
                return False
    return True

def get_draw_call_from_obj(obj):
    """
    Get the geometry from a Blender object and return it as a tuple of xp_vertexs and integer indices.
    Args:
        obj (bpy.types.Object): Blender object to extract geometry from.
    """

    # Ensure the object is a mesh
    if obj.type != 'MESH':
        raise TypeError("Object must be a mesh")
    
    #Define our output arrays
    out_verts = []  #Array of xp_vertex
    out_inds = []   #Ints

    #Check if this object has modifiers. If it does, we'll duplicate it, and apply the modifiers to the duplicate.
    did_duplicate = False
    if len(obj.modifiers) > 0:
        #Make sure we are in object mode before we duplicate and apply the modifiers
        bpy.context.view_layer.objects.active = obj
        if bpy.context.active_object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        obj = obj.copy()
        obj.data = obj.data.copy()
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        did_duplicate = True

        for mod in obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=mod.name)

    try:
        #Get our mesh data
        mesh = obj.data

        #Calculate split normals if this mesh has them. Note used in 4.1+ but this property wouldn't exist there soo it should be fine
        if hasattr(mesh, "calc_normals_split"):
            mesh.calc_normals_split()

        #Triangulate the mesh and get the loop triangles
        mesh.calc_loop_triangles()
        loop_triangles = mesh.loop_triangles

        #Attempt to get the uv layer. We look for the first layer. 
        try:
            uv_layer = mesh.uv_layers[0]
        except (KeyError, TypeError) as e:
            uv_layer = None

        #Define a temporary data structure to hold our triangle faces.
        XPTriangle = collections.namedtuple(
                        "XPTriangle",
                        field_names=[
                            "vertex_pos",  # Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]] Tuple containing the positions for each vertex. Only used when smooth is true
                            "vertex_nrm",  # Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]] Tuple containing the normals for each vertex. Only used when smooth is true
                            "uvs",  # type: Tuple[[float, float], [float, float], [float, float]]
                        ],
                    )
        
        #Define an array to hold our faces
        xp_triangles = []

        #TODO: We need to warn the user if this is Blender 4.1+ and they have an autosmooth modifier on the object, as this does not get applied to the normals

        for tri in loop_triangles:

            #Define our UV and normal data beforehand. The struct is immutable so we can't change it after the fact
            xp_triangle_uvs = ((0, 0), (0, 0), (0, 0))
            if uv_layer != None:
                xp_triangle_uvs = (uv_layer.data[tri.loops[0]].uv, uv_layer.data[tri.loops[1]].uv, uv_layer.data[tri.loops[2]].uv)

            xp_triangles_normals = (tri.split_normals[0], tri.split_normals[1], tri.split_normals[2])


            #Define a temporary face with the data from the loop triangle. UVs default to none so we can add them IF we do have a uv layer
            tmp_face = XPTriangle(
                vertex_pos = (mesh.vertices[tri.vertices[0]].co, mesh.vertices[tri.vertices[1]].co, mesh.vertices[tri.vertices[2]].co),
                vertex_nrm = xp_triangles_normals,
                uvs = xp_triangle_uvs
            )

            #Append the face to the array
            xp_triangles.append(tmp_face)

        #Now that we have the faces stored, we need to actually turn them into vertices and indicies.
        #This is a bit more complicated. We have to iterate through every face. Then we need to check if *any* of it's 3 vertices already exist - if they do, we will use the existing one instead
        #Once we know the indicies of each vertex because it's either been added, or already exists, we can do the index output array, which would be in the order of last vertex, middle, first. 

        for t in xp_triangles:
            #Define vertices for each triangle. Then see if they exist, if they don't, add them.
            v1 = xp_vertex(t.vertex_pos[0][0], t.vertex_pos[0][1], t.vertex_pos[0][2], t.vertex_nrm[0][0], t.vertex_nrm[0][1], t.vertex_nrm[0][2], t.uvs[0][0], t.uvs[0][1])
            v2 = xp_vertex(t.vertex_pos[1][0], t.vertex_pos[1][1], t.vertex_pos[1][2], t.vertex_nrm[1][0], t.vertex_nrm[1][1], t.vertex_nrm[1][2], t.uvs[1][0], t.uvs[1][1])
            v3 = xp_vertex(t.vertex_pos[2][0], t.vertex_pos[2][1], t.vertex_pos[2][2], t.vertex_nrm[2][0], t.vertex_nrm[2][1], t.vertex_nrm[2][2], t.uvs[2][0], t.uvs[2][1])

            out_verts.append(v3)
            v1_index = len(out_verts) - 1
            out_verts.append(v2)
            v2_index = len(out_verts) - 1
            out_verts.append(v1)
            v3_index = len(out_verts) - 1

            #Now finally we add the indicies! These are in the order v3, v2, v1
            out_inds.append(v3_index)
            out_inds.append(v2_index)
            out_inds.append(v1_index)

        #Now we need to get the transform matrix for the object
        transform = obj.matrix_world

        #Now we loop through the vertices and apply the transform to each one
        for v in out_verts:
            #Get the local position as a vector
            local_position = mathutils.Vector((v.loc_x, v.loc_y, v.loc_z))
            normal = mathutils.Vector((v.normal_x, v.normal_y, v.normal_z))

            #Apply the full transformation
            transformed_position = transform @ local_position

            #Work to apply the transform to the normals
            normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
            transformed_normal = normal_matrix @ normal
            transformed_normal.normalize()

            #Set the new position and rotation
            v.loc_x = transformed_position.x
            v.loc_y = transformed_position.y
            v.loc_z = transformed_position.z

            #Set the new normal
            v.normal_x = transformed_normal.x
            v.normal_y = transformed_normal.y
            v.normal_z = transformed_normal.z

    finally:
        #If we made a duplicate object, delete it
        if did_duplicate and obj != None:
            bpy.data.objects.remove(obj, do_unlink=True)
            obj = None

        return (out_verts, out_inds)

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

def compare_property_groups(pg1, pg2, path=""):
    """
    Recursively compare two Blender PropertyGroup instances.
    Returns a list of property paths that differ.
    """
    diffs = []
    for prop in pg1.bl_rna.properties:
        if prop.is_readonly or prop.identifier in {"rna_type"}:
            continue

        name = prop.identifier
        val1 = getattr(pg1, name, None)
        val2 = getattr(pg2, name, None)
        prop_path = f"{path}.{name}" if path else name

        #Check if name contains _ui_, something we don't care about
        if "_ui_" in name:
            continue

        if prop.type == 'COLLECTION':
            if len(val1) != len(val2):
                diffs.append(f"{prop_path} (collection length {len(val1)} != {len(val2)})")
                continue
            for i, (item1, item2) in enumerate(zip(val1, val2)):
                if hasattr(item1, "bl_rna") and hasattr(item2, "bl_rna"):
                    subdiffs = compare_property_groups(item1, item2, f"{prop_path}[{i}]")
                    diffs.extend(subdiffs)
                else:
                    if item1 != item2:
                        diffs.append(f"{prop_path}[{i}] (value {item1} != {item2})")

        elif prop.type == 'POINTER':
            if hasattr(val1, "bl_rna") and hasattr(val2, "bl_rna"):
                subdiffs = compare_property_groups(val1, val2, prop_path)
                diffs.extend(subdiffs)
            else:
                if val1 != val2:
                    diffs.append(f"{prop_path} (pointer value {val1} != {val2})")

        else:
            if isinstance(val1, bpy.types.bpy_prop_array) or isinstance(val2, bpy.types.bpy_prop_array):
                if not tuple(val1) == tuple(val2):
                    diffs.append(f"{prop_path} (array value {tuple(val1)} != {tuple(val2)})")
                
            elif val1 != val2:
                diffs.append(f"{prop_path} (value {val1} != {val2})")

    return diffs

def compare_objects(obj1, obj2):
    """
    Compare two Blender objects for transform, property groups, geometry, materials, and children.
    Args:
        obj1, obj2: Blender objects to compare.
    Returns:
        list: List of differences found.
    """
    differences = []

    #Compare the location, rotation, scale and matrix world are close
    if vectors_close(obj1.location, obj2.location) is False:
        differences.append((f"{obj1.name}, {obj2.name}, location difference: {obj1.location} vs {obj2.location}"))
    if euler_close(obj1.rotation_euler, obj2.rotation_euler) is False:
        differences.append((f"{obj1.name}, {obj2.name}, rotation difference: {obj1.rotation_euler} vs {obj2.rotation_euler}"))
    if vectors_close(obj1.scale, obj2.scale) is False:
        differences.append((f"{obj1.name}, {obj2.name}, scale difference: {obj1.scale} vs {obj2.scale}"))
    if matrix_close(obj1.matrix_world, obj2.matrix_world) is False:
        differences.append((f"{obj1.name}, {obj2.name}, matrix world difference: {obj1.matrix_world} vs {obj2.matrix_world}"))

    #Now we need to compare the various property groups we care about
    differences.extend(compare_property_groups(obj1.xplane, obj2.xplane))
    differences.extend(compare_property_groups(obj1.xp_lin, obj2.xp_lin))
    differences.extend(compare_property_groups(obj1.xp_fac_mesh, obj2.xp_fac_mesh))
    differences.extend(compare_property_groups(obj1.xp_attached_obj, obj2.xp_attached_obj))
    differences.extend(compare_property_groups(obj1.xp_agp, obj2.xp_agp))

    #If these are both a mesh we'll compare geometry and materials
    if obj1.type == 'MESH' and obj2.type == 'MESH':
        dc1 = get_draw_call_from_obj(obj1)
        dc2 = get_draw_call_from_obj(obj2)
        if dc1[1] != dc2[1]:
            differences.append((f"{obj1.name}, {obj2.name}, geometry indices count difference: {len(dc1[1])} vs {len(dc2[1])}"))
        if len(dc1[0]) != len(dc2[0]):
            differences.append((f"{obj1.name}, {obj2.name}, geometry vertices count difference: {len(dc1[0])} vs {len(dc2[0])}"))
        else:
            #Now we compare the vertices
            for i in range(len(dc1[0])):
                v1 = dc1[0][i]
                v2 = dc2[0][i]
                if not v1.almost_equal(v2):
                    differences.append((f"{obj1.name}, {obj2.name}, vertex {i} differs: {v1} vs {v2}"))

            #Now we compare the indices
            for i in range(len(dc1[1])):
                if dc1[1][i] != dc2[1][i]:
                    differences.append((f"{obj1.name}, {obj2.name}, index {i} differs: {dc1[1][i]} vs {dc2[1][i]}"))
    
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
    elif obj1.type != obj2.type:
        differences.append((f"{obj1.name}, {obj2.name}, object type difference: {obj1.type} vs {obj2.type}"))

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
    script_path = os.path.dirname(os.path.abspath(__file__))

    #Create the CSV file if it doesn't exist
    csv_file_path = script_path + os.sep + 'Test Results.csv'
    try:
        with open(csv_file_path, 'x', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Test Name', 'Did Pass?', 'Percentage', 'Message'])  # Write header
    except FileExistsError:
        pass  # File already exists, we can append to it

    print(csv_file_path)

    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([test_name, b_did_pass, percentage, message])
