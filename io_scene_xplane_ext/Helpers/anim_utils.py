#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/24/2025
#Module:    Anim Utils
#Purpose:   Provide functions to help with animations

import bpy
import math
import mathutils

import mathutils

def euler_to_align_z_with_vector(direction):
    """
    Returns Euler XYZ angles (in radians) to rotate the object's local Z axis to align with the given direction vector.
    :param direction: A normalized (x, y, z) tuple or mathutils.Vector.
    :return: mathutils.Euler in 'XYZ' order.
    """
    z_axis = mathutils.Vector((0, 0, 1))
    target = mathutils.Vector(direction).normalized()
    quat = z_axis.rotation_difference(target)
    return quat.to_euler('XYZ')

def get_base_rot_for_local_z_rotation(obj):
    """
    Returns the current local rotation of the object as a quaternion. To be used in rotate_obj_around_local_z
    :param obj: The Blender object to get the base rotation from.
    :return: The current local rotation of the object as a quaternion.
    """
    return obj.rotation_euler.to_quaternion()

def rotate_obj_around_local_z(obj, angle_degrees, base_rot):
    """
    Rotates the object around its *current* local Z axis by the given angle (in degrees),
    regardless of its existing rotation.
    :param obj: The Blender object to rotate.
    :param angle_degrees: The angle in degrees to rotate around the local Z axis.
    :param base_rot: The base rotation quaternion to use as a reference for the local Z axis. Get from get_base_rot_for_local_z_rotation.
    :return: None
    """
    angle_rad = math.radians(angle_degrees)
    
    # Create a quaternion for the Z rotation in local space
    z_rot = mathutils.Quaternion((0, 0, 1), angle_rad)
    # Apply the Z rotation in local space
    new_rot = base_rot @ z_rot
    # Set the new rotation
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler = new_rot.to_euler('XYZ')

def set_obj_position(obj, position):
    """
    Set the position of an object in Blender.
    :param obj: The Blender object to set the position for.
    :param position: A tuple (x, y, z) representing the new position.
    :return: None
    """
    world_pos = mathutils.Vector(position)
    obj.location = world_pos

def get_obj_position(obj):
    """
    Get the position of an object in Blender.
    :param obj: The Blender object to get the position from.
    :return: A tuple (x, y, z) representing the object's position.
    """
    return (obj.location.x, obj.location.y, obj.location.z)

def set_obj_position_world(obj, position):
    """
    Sets the object's position so it has the given world space position. Position will be invalid if a parent's transform changes afterwards
    :param obj: The Blender object to set the position for.
    :param position: A tuple (x, y, z) representing the new world position.
    """
    bpy.context.view_layer.update()
    world_pos = mathutils.Vector(position)
    if obj.parent:
        obj.location = obj.parent.matrix_world.inverted() @ world_pos
    else:
        obj.location = world_pos

def get_obj_position_world(obj):
    """
    Returns the object's position in world space as a tuple (x, y, z).
    :param obj: The Blender object to get the position from.
    :return: A tuple (x, y, z) representing the object's world position.
    """
    bpy.context.view_layer.update()
    loc = obj.matrix_world.to_translation()
    return (loc.x, loc.y, loc.z)

def set_obj_rotation_from_euler(obj, rotation):
    """
    Set the rotation of an object in Blender from an xyz euler rotation.

    :param obj: The Blender object to set the rotation for.
    :param rotation: A tuple (x, y, z) representing the new rotation in radians.
    """
    obj.rotation_euler = mathutils.Euler(rotation, 'XYZ')

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

def get_obj_rotation_world(obj):
    """
    Returns the object's rotation in world space as a mathutils.Euler (in radians, 'XYZ').
    """
    bpy.context.view_layer.update()
    rot = obj.matrix_world.to_euler('XYZ')
    return rot

def set_obj_rotation_world(obj, world_euler):
    """
    Sets the object's rotation so it has the given world space rotation (Euler, in radians).
    """
    bpy.context.view_layer.update()
    world_rot = mathutils.Euler(world_euler, 'XYZ').to_matrix().to_4x4()
    if obj.parent:
        parent_rot = obj.parent.matrix_world.to_3x3().to_4x4()
        local_rot = parent_rot.inverted() @ world_rot
        obj.rotation_euler = local_rot.to_euler('XYZ')
    else:
        obj.rotation_euler = mathutils.Euler(world_euler, 'XYZ')

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