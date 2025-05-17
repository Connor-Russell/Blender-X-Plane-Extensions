#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/24/2025
#Module:    Anim Utils
#Purpose:   Provide functions to help with animations

import bpy
import math
import mathutils

def align_to_axis(obj, axis):
    #return
    """
    Rotates the object so its local Z axis aligns with the given normalized axis vector,
    without changing its position.
    """
    print("Start position: ", obj.location)
    z = axis.normalized()
    # Choose an arbitrary vector not parallel to z
    if abs(z.dot(mathutils.Vector((0, 0, 1)))) < 0.999:
        x = mathutils.Vector((0, 0, 1)).cross(z).normalized()
    else:
        x = mathutils.Vector((1, 0, 0)).cross(z).normalized()
    y = z.cross(x).normalized()
    # Build rotation matrix (columns are x, y, z)
    rot_mat = mathutils.Matrix((x, y, z))
    # Set only the rotation, keep the location
    obj.matrix_basis = rot_mat.to_4x4()
    
    print("End position: ", obj.location)

def rotate_on_z(object, angle):
    #return
    """
    Rotate an object object around its local Z-axis.

    :param object: The Blender object object to rotate. This object should already be aligned to the desired axis.
    :param angle: The angle in degrees to rotate the object.
    """
    rot_mat = mathutils.Matrix.Rotation(math.radians(angle), 4, 'Z')
    object.matrix_world = rot_mat @ object.matrix_world

import mathutils

def set_obj_position(obj, position):
    world_pos = mathutils.Vector(position)
    if obj.parent:
        obj.location = obj.parent.matrix_world.inverted() @ world_pos
    else:
        obj.location = world_pos

def get_obj_position(obj):
    loc = obj.matrix_world.to_translation()
    return (loc.x, loc.y, loc.z)

def set_obj_rotation(obj, rotation):
    """
    Set the rotation of an object in Blender.

    :param obj: The Blender object to set the rotation for.
    :param rotation: A tuple (x, y, z) representing the new rotation in radians.
    """
    #Convert the rotation from degrees to radians
    obj.rotation_euler.x = math.radians(rotation[0])
    obj.rotation_euler.y = math.radians(rotation[1])
    obj.rotation_euler.z = math.radians(rotation[2])

def get_obj_rotation(obj):
    """
    Get the rotation of an object in Blender.

    :param obj: The Blender object to get the rotation from.
    :return: A tuple (x, y, z) representing the object's rotation in radians.
    """
    #Convert the rotation from radians to degrees
    out_x = math.degrees(obj.rotation_euler.x)
    out_y = math.degrees(obj.rotation_euler.y)
    out_z = math.degrees(obj.rotation_euler.z)

    return (out_x, out_y, out_z)

def goto_frame(frame_number):
    """
    Set the current frame in Blender.

    :param frame_number: The frame number to set.
    """
    bpy.context.scene.frame_set(frame_number)

def get_current_frame():
    """
    Get the current frame in Blender.

    :return: The current frame number.
    """
    return bpy.context.scene.frame_current

def keyframe_obj_location(obj):
    """
    Keyframe the object at the current location at the current frame/

    :param obj: The Blender object to keyframe.
    """
    obj.keyframe_insert(data_path="location")

def keyframe_obj_rotation(obj):
    """
    Keyframe the object at the current rotation at the current frame.

    :param obj: The Blender object to keyframe.
    """
    obj.keyframe_insert(data_path="rotation_euler")

def add_xp_dataref_track(obj, name):
    obj.xplane.datarefs.add()
    obj.xplane.datarefs[len(obj.xplane.datarefs)-1].path = name

def keyframe_xp_dataref(obj, name, value):
    """
    Keyframe the XP dataref at the current value at the current frame.

    :param obj: The Blender object to keyframe.
    :param value: The value to set for the XP dataref.
    """
    for dref in obj.xplane.datarefs:
        if obj.xplane.datarefs[0].path == name:
            obj.xplane.datarefs[0].value = value
            obj.xplane.datarefs[0].keyframe_insert(data_path="value")
            break

def get_xp_dataref(obj, name):
    """
    Get the XP dataref value.

    :param obj: The Blender object to get the dataref from.
    :param name: The name of the dataref to get.
    :return: The value of the dataref.
    """
    for dref in obj.xplane.datarefs:
        if obj.xplane.datarefs[0].path == name:
            return obj.xplane.datarefs[0].value
    return 0