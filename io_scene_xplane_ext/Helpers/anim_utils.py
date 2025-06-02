#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/24/2025
#Module:    Anim Utils
#Purpose:   Provide functions to help with animations

import bpy
import math
import mathutils

import mathutils

def move_along_axis(position, axis, distance):
    """
    Moves a position along an arbitrary axis by a given distance.
    
    :param position: The starting position (Vector).
    :param axis: The direction to move (Vector, should be normalized).
    :param distance: The distance to move.
    :return: New position after movement.
    """
    # Ensure axis is normalized
    axis = axis.normalized()
    
    # Compute displacement
    displacement = axis * distance

    # Apply movement
    new_position = position + displacement

    return new_position

def euler_to_axis_angle(euler):
    """
    Converts an XYZ Euler rotation to its equivalent axis-angle representation.
    
    :param euler: Euler rotation (in radians). For example, Euler((0.5, 0.3, 1.2), 'XYZ')
    :return: A tuple (axis, angle) where:
             - axis is a normalized Vector indicating the rotation axis,
             - angle is the rotation in degrees.
    """
    # Convert the Euler rotation to a quaternion.
    q = euler.to_quaternion()
    
    # Get the axis-angle representation from the quaternion.
    # mathutils.Quaternion.to_axis_angle returns (axis, angle)
    axis, angle = q.to_axis_angle()
    
    return axis, math.degrees(angle)


def rotate_point_and_euler(point, euler_angles, axis, angle_deg):
        """
        Rotates a location and euler around an arbitrary axis by a given angle in degrees.
        Args:
            point (mathutils.Vector): The position vector to rotate.
            euler_angles (mathutils.Euler): The Euler angles to rotate.
            axis (mathutils.Vector): The axis of rotation (should be normalized).
            angle_deg (float): The angle in degrees to rotate around the axis.
        Returns:
            tuple: A tuple containing the rotated position (mathutils.Vector) and the rotated Euler angles (mathutils.Euler).
        """
        # Ensure the axis is normalized just in case:
        axis = axis.normalized()

        # Convert degrees to radians since mathutils.Quaterion accepts radians
        angle_rad = math.radians(angle_deg)

        # Create the quaternion representing the rotation about the given axis
        q = mathutils.Quaternion(axis, angle_rad)

        # Rotate the position vector.
        # The '@' operator applies the rotation.
        rotated_point = q @ point

        # For the Euler rotation:
        # 1. Convert the Euler angles to a quaternion
        euler_quat = euler_angles.to_quaternion()

        # 2. Apply the arbitrary axis rotation by quaternion multiplication.
        # Note: Quaternion multiplication is not commutative, so if your intention is to pre-rotate,
        # use q @ euler_quat. If your intention is to post-rotate, you might use euler_quat @ q.
        rotated_euler_quat = q @ euler_quat

        # 3. Convert the result back to Euler angles using the original order
        rotated_euler = rotated_euler_quat.to_euler(euler_angles.order)

        return rotated_point, rotated_euler

def euler_to_align_z_with_vector(direction):
    """
    Compute the Euler XYZ rotation (in radians) to align the object's local Z axis with the given direction vector.

    Args:
        direction (tuple or mathutils.Vector): Normalized (x, y, z) direction vector.

    Returns:
        mathutils.Euler: Euler rotation in 'XYZ' order.
    """
    z_axis = mathutils.Vector((0, 0, 1))
    target = mathutils.Vector(direction).normalized()
    quat = z_axis.rotation_difference(target)
    return quat.to_euler('XYZ')

def get_base_rot_for_local_z_rotation(obj):
    """
    Get the object's current local rotation as a quaternion, for use as a base when rotating around local Z.

    Args:
        obj (bpy.types.Object): Blender object.

    Returns:
        mathutils.Quaternion: The object's current local rotation.
    """
    return obj.rotation_euler.to_quaternion()

def rotate_obj_around_local_z(obj, angle_degrees, base_rot):
    """
    Rotate the object around its current local Z axis by the given angle (degrees), using a base quaternion.

    Args:
        obj (bpy.types.Object): Blender object to rotate.
        angle_degrees (float): Angle in degrees to rotate around local Z.
        base_rot (mathutils.Quaternion): Base rotation quaternion (from get_base_rot_for_local_z_rotation).
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
    Set the object's local position.

    Args:
        obj (bpy.types.Object): Blender object.
        position (tuple): (x, y, z) local position.
    """
    world_pos = mathutils.Vector(position)
    obj.location = world_pos

def get_obj_position(obj):
    """
    Get the object's local position.

    Args:
        obj (bpy.types.Object): Blender object.

    Returns:
        tuple: (x, y, z) local position.
    """
    return (obj.location.x, obj.location.y, obj.location.z)

def set_obj_position_world(obj, position):
    """
    Set the object's world space position. If the parent transform changes later, the world position may become invalid.

    Args:
        obj (bpy.types.Object): Blender object.
        position (tuple): (x, y, z) world position.
    """
    # The view layer needs to be updated otherwise the world matrix may be invalid. I lost so many hours not realizing this...
    bpy.context.view_layer.update()
    world_pos = mathutils.Vector(position)
    if obj.parent:
        obj.location = obj.parent.matrix_world.inverted() @ world_pos
    else:
        obj.location = world_pos

def get_obj_position_world(obj):
    """
    Get the object's world space position.

    Args:
        obj (bpy.types.Object): Blender object.

    Returns:
        tuple: (x, y, z) world position.
    """
    # The view layer needs to be updated otherwise the world matrix may be invalid. I lost so many hours not realizing this...
    bpy.context.view_layer.update()
    loc = obj.matrix_world.to_translation()
    return (loc.x, loc.y, loc.z)

def set_obj_rotation(obj, rotation):
    """
    Set the object's rotation from an XYZ tuple (degrees).

    Args:
        obj (bpy.types.Object): Blender object.
        rotation (tuple): (x, y, z) Euler angles in degrees.
    """
    obj.rotation_euler.x = math.radians(rotation[0])
    obj.rotation_euler.y = math.radians(rotation[1])
    obj.rotation_euler.z = math.radians(rotation[2])

def get_obj_rotation(obj):
    """
    Get the object's rotation as an XYZ tuple (degrees).

    Args:
        obj (bpy.types.Object): Blender object.

    Returns:
        tuple: (x, y, z) Euler angles in degrees.
    """
    out_x = math.degrees(obj.rotation_euler.x)
    out_y = math.degrees(obj.rotation_euler.y)
    out_z = math.degrees(obj.rotation_euler.z)

    return (out_x, out_y, out_z)

def get_obj_rotation_world(obj):
    """
    Get the object's world space rotation as a mathutils.Euler (radians, 'XYZ').

    Args:
        obj (bpy.types.Object): Blender object.

    Returns:
        mathutils.Euler: World rotation in radians.

    Notes:
        We do this with a euler vs degrees in a tuple (like local space) because when working with world space
        we typically are working with a euler rotation we got from aligning to a vector. The function for local space rotation
        is just a tuple of degrees for ease of use. If we wanted to set it with a euler we would just set it's rotation_euler.

        Just a note on why this is different.
    """
    bpy.context.view_layer.update()
    rot = obj.matrix_world.to_euler('XYZ')
    return rot

def set_obj_rotation_world(obj, world_euler):
    """
    Set the object's rotation so it matches the given world space Euler rotation (radians).

    Args:
        obj (bpy.types.Object): Blender object.
        world_euler (tuple): (x, y, z) Euler angles in radians (world space).

    Notes:
        We do this with a euler vs degrees in a tuple (like local space) because when working with world space
        we typically are working with a euler rotation we got from aligning to a vector. The function for local space rotation
        is just a tuple of degrees for ease of use. If we wanted to set it with a euler we would just set it's rotation_euler.

        Just a note on why this is different.

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
    Set the current frame in Blender. Use this to set the frame for keyframing.

    Args:
        frame_number (int): Frame number to set.
    """
    bpy.context.scene.frame_set(frame_number)

def get_current_frame():
    """
    Get the current frame number in Blender.

    Returns:
        int: Current frame number.
    """
    return bpy.context.scene.frame_current

def keyframe_obj_location(obj):
    """
    Insert a keyframe for the object's current location at the current frame.

    Args:
        obj (bpy.types.Object): Blender object.
    """
    obj.keyframe_insert(data_path="location")

def keyframe_obj_rotation(obj):
    """
    Insert a keyframe for the object's current rotation at the current frame.

    Args:
        obj (bpy.types.Object): Blender object.
    """
    obj.keyframe_insert(data_path="rotation_euler")

def add_xp_dataref_track(obj, name):
    """
    Add a new X-Plane dataref track to the object.

    Args:
        obj (bpy.types.Object): Blender object.
        name (str): Dataref name/path.
    """
    obj.xplane.datarefs.add()
    obj.xplane.datarefs[len(obj.xplane.datarefs)-1].path = name

def keyframe_xp_dataref(obj, name, value):
    """
    Keyframe the X-Plane dataref at the current value at the current frame.

    Args:
        obj (bpy.types.Object): Blender object.
        name (str): Dataref name/path.
        value (float): Value to set and keyframe.
    """
    for dref in obj.xplane.datarefs:
        if obj.xplane.datarefs[0].path == name:
            obj.xplane.datarefs[0].value = value
            obj.xplane.datarefs[0].keyframe_insert(data_path="value")
            break

def get_xp_dataref(obj, name):
    """
    Get the value of the specified X-Plane dataref from the object.

    Args:
        obj (bpy.types.Object): Blender object.
        name (str): Dataref name/path.

    Returns:
        float: Value of the dataref, or 0 if not found.
    """
    for dref in obj.xplane.datarefs:
        if obj.xplane.datarefs[0].path == name:
            return obj.xplane.datarefs[0].value
    return 0