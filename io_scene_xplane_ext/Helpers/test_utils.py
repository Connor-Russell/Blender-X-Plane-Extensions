#Project: Blender X-Plane Extensions
#Author: Connor Russell
#Date: 4/23/2025
#Module: test_utils
#Purpose: Tests utility functions for the X-Plane Blender exporter

import bpy
from ..Helpers import collection_utils
from ..Helpers import file_utils
from ..Helpers import anim_utils
import mathutils

#---------------------------------------------------------------------------------
#collection_utils.py tests
#---------------------------------------------------------------------------------

def TEST_get_all_collections_from_view_layer():

    result = "FAIL"
    try:

        #First remove all collections from the scene
        for collection in bpy.data.collections:
            bpy.data.collections.remove(collection)

        collection_names = []
        for i in range(3):
            collection_name = f"TestCollection_{i}"
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)
            collection_names.append(collection_name)

        try:
            view_layer = bpy.context.view_layer
            collections = collection_utils.get_all_collections_from_view_layer(view_layer)

            returned_names = [col.collection.name for col in collections]

            if set(returned_names) == set(collection_names):
                result = "PASS"
            else:
                result = f"FAIL,Expected {collection_names}, but got {returned_names}"
        finally:
            # Step 5: Cleanup - Remove the created collections
            for collection_name in collection_names:
                collection = bpy.data.collections.get(collection_name)
                if collection:
                    bpy.data.collections.remove(collection)

    except Exception as e:
        result = "FAIL,Exception: " + str(e)
    except:
        result = "FAIL,Unknown error occurred."

    return result  # Return the result of the test

#----------------------------------------------------------------------------------
#facade_utils.py tests
#----------------------------------------------------------------------------------

def TEST_get_roof_data():
    """
    Test the get_roof_data function from facade_utils.
    This test creates a collection with plane and empty objects, invokes get_roof_data, and validates the results.
    """

    try:

        # Step 1: Create a new collection
        collection_name = "TestRoofCollection"
        test_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(test_collection)

        try:
            # Step 2: Add two plane objects at different heights
            mesh1 = bpy.data.meshes.new("Plane1")
            mesh1.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [], [(0, 1, 2, 3)])
            obj1 = bpy.data.objects.new("PlaneObject1", mesh1)
            obj1.location = (0, 0, 5)  # Height 5 meters
            test_collection.objects.link(obj1)

            mesh2 = bpy.data.meshes.new("Plane2")
            mesh2.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [], [(0, 1, 2, 3)])
            obj2 = bpy.data.objects.new("PlaneObject2", mesh2)
            obj2.location = (0, 0, 10)  # Height 10 meters
            test_collection.objects.link(obj2)

            # Step 3: Add several empty objects within the range 0 to 10 meters
            empty_positions = [(1, 2, 3), (2, 3, 4), (4, 5, 6), (5, 6, 7)]
            for i, pos in enumerate(empty_positions):
                empty = bpy.data.objects.new(f"Empty_{i}", None)
                empty.xp_attached_obj.resource = str(i)  # Dummy resource name
                empty.location = pos
                empty.empty_display_size = 1
                empty.empty_display_type = 'PLAIN_AXES'
                test_collection.objects.link(empty)

            # Step 4: Invoke get_roof_data
            from ..Helpers import facade_utils
            roof_scale_x, roof_scale_y, roof_objs, roof_heights = facade_utils.get_roof_data(test_collection)

            # Step 5: Validate the results
            expected_heights = [5, 10]  # Heights of the plane objects
            expected_roof_objs = len(empty_positions)  # Number of empty objects

            if roof_scale_x != obj1.dimensions.x or \
            roof_scale_y != obj1.dimensions.y or \
            roof_heights != expected_heights:
                return f"FAIL,Expected heights {expected_heights}, got {roof_heights}. " \
                    f"Expected {expected_roof_objs} roof objects, got {len(roof_objs)}."
            
            roof_objs.sort(key=lambda x: x.resource)  # Sort roof objects by index for comparison

            for i, cur_obj in enumerate(roof_objs):

                if int(cur_obj.loc_x) != empty_positions[i][0] or \
                int(cur_obj.loc_y) != empty_positions[i][1] or \
                int(cur_obj.loc_z) != empty_positions[i][2]:
                    return f"FAIL,Expected roof object at {empty_positions[i]}, got {cur_obj.loc_x, cur_obj.loc_y, cur_obj.loc_z}."
                
                if cur_obj.resource != str(i):
                    return f"FAIL,Expected roof object resource {str(i)}, got {cur_obj.resource}."
            
        finally:
            # Cleanup: Remove the created collection and its objects
            bpy.data.collections.remove(test_collection)
    
    except Exception as e:
        result = "FAIL,Exception: " + str(e)
    except:
        result = "FAIL,Unknown error occurred."

    return "PASS"  # If all checks pass, return "PASS"

#----------------------------------------------------------------------------------
# geometery_utils.py tests
#----------------------------------------------------------------------------------

def TEST_draw_call_round_trip():
        """
        Test creating a mesh from a draw call, then getting the draw call from that mesh,
        and comparing the outputted xp_vertex with the source ones.
        """
        import mathutils
        from ..Helpers import geometery_utils

        result = "PASS"

        try:
            # Step 1: Define draw call data. We can only do a triangle because if when we get a draw call, we get triangles back, so the data would not match
            vertices = [
                geometery_utils.xp_vertex(-1.0, -1.0, -1.0, 0.1, 0.2, 0.3, 0.0, 0.0),
                geometery_utils.xp_vertex(1.0, -1.0, -1.0, 0.4, 0.5, 0.6, 1.0, 0.0),
                geometery_utils.xp_vertex(1.0, 1.0, -1.0, 0.7, 0.8, 0.9, 1.0, 1.0),
            ]
            indices = [0, 1, 2]

            # Step 2: Create the mesh from the draw call
            obj = geometery_utils.create_obj_from_draw_call(vertices, indices, "RoundTripMesh")

            #Link to scene
            bpy.context.scene.collection.objects.link(obj)

            # Step 3: Get the draw call from the created mesh
            round_tripped_vertices, round_tripped_indices = geometery_utils.get_draw_call_from_obj(obj)

            # Step 4: Sort vertices for 1:1 comparison
            original_sorted = sorted(vertices, key=lambda v: (v.loc_x, v.loc_y, v.loc_z, v.uv_x, v.uv_y))
            round_tripped_sorted = sorted(round_tripped_vertices, key=lambda v: (v.loc_x, v.loc_y, v.loc_z, v.uv_x, v.uv_y))

            # Ensure the number of vertices matches
            if len(original_sorted) != len(round_tripped_sorted):
                result = f"FAIL,Vertex count mismatch. Expected {len(original_sorted)}, got {len(round_tripped_sorted)}."

            # Compare each vertex within a tolerance
            tolerance = 0.000001
            normal_tolerance = 0.001
            for orig_vert, rt_vert in zip(original_sorted, round_tripped_sorted):
                if abs(orig_vert.loc_x - rt_vert.loc_x) > tolerance or \
                   abs(orig_vert.loc_y - rt_vert.loc_y) > tolerance or \
                   abs(orig_vert.loc_z - rt_vert.loc_z) > tolerance:
                    result = f"FAIL,Vertex position mismatch. Expected {orig_vert.loc_x, orig_vert.loc_y, orig_vert.loc_z}, got {rt_vert.loc_x, rt_vert.loc_y, rt_vert.loc_z}."
                    break
                if abs(orig_vert.uv_x - rt_vert.uv_x) > tolerance or \
                     abs(orig_vert.uv_y - rt_vert.uv_y) > tolerance:
                      result = f"FAIL,Vertex UV mismatch. Expected {orig_vert.uv_x, orig_vert.uv_y}, got {rt_vert.uv_x, rt_vert.uv_y}."
                      break
                normalized_vert_normal = mathutils.Vector((orig_vert.normal_x, orig_vert.normal_y, orig_vert.normal_z)).normalized()
                if abs(normalized_vert_normal[0] - rt_vert.normal_x) > normal_tolerance or \
                     abs(normalized_vert_normal[1] - rt_vert.normal_y) > normal_tolerance or \
                     abs(normalized_vert_normal[2] - rt_vert.normal_z) > normal_tolerance:
                      result = f"FAIL,Vertex normal mismatch. Expected {normalized_vert_normal[0]} {normalized_vert_normal[1]} {normalized_vert_normal[2]} got {rt_vert.normal_x} {rt_vert.normal_y} {rt_vert.normal_z}."
                      break
        except Exception as e:
            result = "FAIL,Exception: " + str(e)
        except:
            result = "FAIL,Unknown error occurred."

        return result

#----------------------------------------------------------------------------------
# anim_utils.py tests
#----------------------------------------------------------------------------------

def TEST_keyframing():
    """
    Test the keyframing functionality in Blender.
    This test creates a cube, sets its location, and keyframes it.
    """
    result = "PASS"

    try:

        #Add an empty object to the scene
        empty = bpy.data.objects.new("TestEmpty", None)
        empty.empty_display_size = 1
        empty.empty_display_type = 'PLAIN_AXES'
        bpy.context.scene.collection.objects.link(empty)

        #Define start and end positions, rotations, and keyframes
        dref_name = "TestEmpty"
        start_pos = (0, 0, 0)
        end_pos = (1, 1, 1)
        start_rot = (0, 0, 0)
        end_rot = (45, 45, 45)
        start_dref_value = 0.0
        end_dref_value = 1.0
        start_frame = 1
        end_frame = 10

        #Add the X-Plane
        anim_utils.add_xp_dataref_track(empty, dref_name)

        #Set the frame, loc, and rot to 
        anim_utils.goto_frame(start_frame)
        anim_utils.set_obj_position(empty, start_pos)
        anim_utils.set_obj_rotation(empty, start_rot)
        anim_utils.keyframe_obj_location(empty)
        anim_utils.keyframe_obj_rotation(empty)
        anim_utils.keyframe_xp_dataref(empty, dref_name, start_dref_value)

        #Goto the end frame and set the position and rotation
        anim_utils.goto_frame(end_frame)
        anim_utils.set_obj_position(empty, end_pos)
        anim_utils.set_obj_rotation(empty, end_rot)
        anim_utils.keyframe_obj_location(empty)
        anim_utils.keyframe_obj_rotation(empty)
        anim_utils.keyframe_xp_dataref(empty, dref_name, end_dref_value)

        #Now check if the first keyframe is set properly
        anim_utils.goto_frame(start_frame)
        cur_frame = anim_utils.get_current_frame()
        check_start_pos = anim_utils.get_obj_position(empty)
        check_start_rot = anim_utils.get_obj_rotation(empty)
        check_start_dref_value = anim_utils.get_xp_dataref(empty, dref_name)
        if cur_frame != start_frame:
            result = f"FAIL,Expected frame {start_frame}, got {cur_frame}."
        if abs(check_start_dref_value - start_dref_value) > 0.0001:
            result = f"FAIL,Expected dataref value {start_dref_value}, got {check_start_dref_value}."
        if abs(check_start_pos[0] - start_pos[0]) > 0.0001 or \
        abs(check_start_pos[1] - start_pos[1]) > 0.0001 or \
        abs(check_start_pos[2] - start_pos[2]) > 0.0001:
            result = f"FAIL,Expected start position {start_pos}, got {check_start_pos}."
        if abs(check_start_rot[0] - start_rot[0]) > 0.0001 or \
        abs(check_start_rot[1] - start_rot[1]) > 0.0001 or \
        abs(check_start_rot[2] - start_rot[2]) > 0.0001:
            result = f"FAIL,Expected start rotation {start_rot}, got {check_start_rot}."    

        #Now check the last keyframe
        anim_utils.goto_frame(end_frame)
        cur_frame = anim_utils.get_current_frame()
        check_end_pos = anim_utils.get_obj_position(empty)
        check_end_rot = anim_utils.get_obj_rotation(empty)
        check_end_dref_value = anim_utils.get_xp_dataref(empty, dref_name)
        if cur_frame != end_frame:
            result = f"FAIL,Expected frame {end_frame}, got {cur_frame}."
        if abs(check_end_dref_value - end_dref_value) > 0.0001:
            result = f"FAIL,Expected dataref value {end_dref_value}, got {check_end_dref_value}."
        if abs(check_end_pos[0] - end_pos[0]) > 0.0001 or \
        abs(check_end_pos[1] - end_pos[1]) > 0.0001 or \
        abs(check_end_pos[2] - end_pos[2]) > 0.0001:
            result = f"FAIL,Expected end position {end_pos}, got {check_end_pos}."
        if abs(check_end_rot[0] - end_rot[0]) > 0.0001 or \
        abs(check_end_rot[1] - end_rot[1]) > 0.0001 or \
        abs(check_end_rot[2] - end_rot[2]) > 0.0001:
            result = f"FAIL,Expected end rotation {end_rot}, got {check_end_rot}."

    except Exception as e:
        result = "FAIL,Exception: " + str(e)
    except:
        result = "FAIL,Unknown error occurred."

    return result

def TEST_world_space_transform():
    """
    Test world space transform utilities with parented objects and rotation.
    """
    import math
    result = "PASS"
    try:
        # Clean up any previous test objects
        for obj in bpy.data.objects:
            if obj.name.startswith("TestA") or obj.name.startswith("TestB"):
                bpy.data.objects.remove(obj, do_unlink=True)

        # Create parent object A
        obj_a = bpy.data.objects.new("TestA", None)
        bpy.context.scene.collection.objects.link(obj_a)

        # Create child object B
        obj_b = bpy.data.objects.new("TestB", None)
        bpy.context.scene.collection.objects.link(obj_b)
        obj_b.parent = obj_a
        obj_b.location = (0, 2, 0)
        obj_b.rotation_euler = (0, 0, 0)

        #Move A. Has to be after B so it applies to both
        obj_a.location = (2, 0, 0)
        obj_a.rotation_euler = (0, 0, math.radians(45))

        # Get world position of B
        world_pos = anim_utils.get_obj_position_world(obj_b)

        # Expected world position: rotate (0,2,0) by 45deg around Z, then add (2,0,0)
        expected_x = 0.58579
        expected_y = 1.4142
        tolerance = 0.001
        if abs(world_pos[0] - expected_x) > tolerance or abs(world_pos[1] - expected_y) > tolerance:
            result = f"FAIL,Expected world pos ({expected_x:.3f},{expected_y:.3f}), got ({world_pos[0]:.3f},{world_pos[1]:.3f})"

        # Now set B to a new world position and check if it is set correctly
        new_world_pos = (5, 5, 0)
        anim_utils.set_obj_position_world(obj_b, new_world_pos)
        check_pos = anim_utils.get_obj_position_world(obj_b)
        if abs(check_pos[0] - new_world_pos[0]) > tolerance or abs(check_pos[1] - new_world_pos[1]) > tolerance:
            result = f"FAIL,Set world pos to {new_world_pos}, got {check_pos}"

        # Cleanup
        bpy.data.objects.remove(obj_b, do_unlink=True)
        bpy.data.objects.remove(obj_a, do_unlink=True)
    except Exception as e:
        result = "FAIL,Exception: " + str(e)
    except:
        result = "FAIL,Unknown error occurred."
    return result

#----------------------------------------------------------------------------------
# Main function to run all tests
#----------------------------------------------------------------------------------

def run_all_tests():
    """
    Run all tests and print the results.
    """
    print("Running tests...")
    result1 = TEST_get_all_collections_from_view_layer()
    print(f"TEST_get_all_collections_from_view_layer: {result1}")

    result2 = TEST_get_roof_data()
    print(f"TEST_get_roof_data: {result2}")

    result3 = TEST_keyframing()
    print(f"TEST_keyframing: {result3}")

    result4 = TEST_draw_call_round_trip()
    print(f"TEST_get_draw_call_from_obj: {result4}")

    result5 = TEST_world_space_transform()
    print(f"TEST_world_space_transform: {result5}")

    test_results_file = file_utils.rel_to_abs("../Test Results.csv")
    with open(test_results_file, 'a') as output:
        output.write(f"TEST_get_all_collections_from_view_layer,{result1}\n")
        output.write(f"TEST_get_roof_data,{result2}\n")
        output.write(f"TEST_keyframing,{result3}\n")
        output.write(f"TEST_get_draw_call_from_obj,{result4}\n")
        output.write(f"TEST_world_space_transform,{result5}\n")

