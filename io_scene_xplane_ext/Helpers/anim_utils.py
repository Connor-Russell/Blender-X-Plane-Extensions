#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/24/2025
#Module:    Anim Utils
#Purpose:   Provide functions to help with animations

import bpy
import math
import mathutils

def set_obj_position(obj, position):
    """
    Set the position of an object in Blender.

    :param obj: The Blender object to set the position for.
    :param position: A tuple (x, y, z) representing the new position.
    """
    obj.location.x = position[0]
    obj.location.y = position[1]
    obj.location.z = position[2]

def get_obj_position(obj):
    """
    Get the position of an object in Blender.

    :param obj: The Blender object to get the position from.
    :return: A tuple (x, y, z) representing the object's position.
    """
    return (obj.location.x, obj.location.y, obj.location.z)

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