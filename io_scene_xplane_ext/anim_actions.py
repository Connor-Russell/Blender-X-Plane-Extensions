#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      7/10/2025
#Module:    Anim Actions
#Purpose:   This file contains functions for performing actions in regards to animations for X-Plane in Blender

import bpy

from .Helpers import anim_utils

def create_flipbook_animation(in_obj, dataref, start_value, end_value, loop_value, start_frame, end_frame, keyframe_interval, apply_parent_transform=False):
    """
    Create a flipbook animation for the given object.

    :param in_obj: The object to animate.
    :param dataref: The dataref to use for the animation.
    :param start_value: The starting dataref value of the animation.
    :param end_value: The ending dataref value of the animation.
    :param loop_value: The dataref value to loop the animation at.
    :param start_frame: The frame to start the animation on.
    :param end_frame: The frame to end the animation on.
    :param keyframe_interval: The interval between keyframes.
    """
    #Get the number of frames that we'll freeze at
    num_frames = (end_frame - start_frame) // keyframe_interval + 1
    
    #Get the value interval
    value_interval = (end_value - start_value) / num_frames

    depsgraph = bpy.context.evaluated_depsgraph_get()

    for frame in range(0, num_frames):
        #Get the frame
        frame_num = start_frame + (frame * keyframe_interval)

        bpy.context.scene.frame_set(frame_num)
        bpy.context.view_layer.update()

        # Get the evaluated object with cloth deformation
        eval_obj = in_obj.evaluated_get(depsgraph)

        # Copy the mesh data from the evaluated object
        mesh_copy = eval_obj.to_mesh().copy()  # Make a real datablock copy

        #Duplicat the object via operators, then we will clear modifiers, and replace it's mesh data with mesh_copy
        bpy.ops.object.select_all(action='DESELECT')
        in_obj.select_set(True)
        bpy.context.view_layer.objects.active = in_obj
        bpy.ops.object.duplicate()
        anim_obj = bpy.context.active_object
        anim_obj.name = f"{in_obj.name}_anim_{frame_num}"

        # Clear all modifiers
        anim_obj.modifiers.clear()

        anim_obj.data = mesh_copy

        if apply_parent_transform:
            if anim_obj.parent:
                # Store the world matrix
                world_matrix = anim_obj.matrix_world.copy()
                # Clear parent
                anim_obj.parent = None
                # Restore world matrix
                anim_obj.matrix_world = world_matrix

        # Free the mesh when done (to avoid memory leaks)
        eval_obj.to_mesh_clear()

        #Now we need to setup the animation. So we need to get the start value, and the end value, then add the animations
        start_dref_value = start_value + value_interval * frame
        end_dref_value = (start_value + value_interval * (frame + 1)) + (value_interval * 0.1)

        #Add 3 to the dataref collection
        if start_dref_value != start_value:
            anim_obj.xplane.datarefs.add()
            anim_obj.xplane.datarefs[-1].path = dataref
            anim_obj.xplane.datarefs[-1].anim_type = 'hide'
            anim_obj.xplane.datarefs[-1].show_hide_v1 = start_value
            anim_obj.xplane.datarefs[-1].show_hide_v2 = start_dref_value
            anim_obj.xplane.datarefs[-1].loop = loop_value
        anim_obj.xplane.datarefs.add()
        anim_obj.xplane.datarefs[-1].path = dataref
        anim_obj.xplane.datarefs[-1].anim_type = 'show'
        anim_obj.xplane.datarefs[-1].show_hide_v1 = start_dref_value
        anim_obj.xplane.datarefs[-1].show_hide_v2 = end_dref_value
        anim_obj.xplane.datarefs[-1].loop = loop_value
        if end_dref_value != end_value + (value_interval * 0.1):
            anim_obj.xplane.datarefs.add()
            anim_obj.xplane.datarefs[-1].path = dataref
            anim_obj.xplane.datarefs[-1].anim_type = 'hide'
            anim_obj.xplane.datarefs[-1].show_hide_v1 = end_dref_value
            anim_obj.xplane.datarefs[-1].show_hide_v2 = end_value + (value_interval * 0.1)
            anim_obj.xplane.datarefs[-1].loop = loop_value

def auto_keyframe(in_obj, dataref, start_value, end_value, loop_value, start_frame, end_frame, keyframe_interval):
    """
    Automatically keyframe the given object for the specified dataref.

    :param in_obj: The object to keyframe.
    :param dataref: The dataref to use for the keyframe.
    :param start_value: The starting value of the dataref.
    :param end_value: The ending value of the dataref.
    :param loop_value: The value to loop the animation at.
    :param start_frame: The frame to start the keyframe on.
    :param end_frame: The frame to end the keyframe on.
    """

    #Get the value increment
    value_increment = (end_value - start_value) / (end_frame - start_frame)
    
    #Add the dataref track
    in_obj.xplane.datarefs.add()
    in_obj.xplane.datarefs[-1].path = dataref
    in_obj.xplane.datarefs[-1].anim_type = 'transform'
    in_obj.xplane.datarefs[-1].loop = loop_value

    #Iterate through the frames and set the xp keyframes
    for frame in range(start_frame, end_frame + 1, keyframe_interval):
        value = start_value + (frame - start_frame) * value_increment
        anim_utils.goto_frame(frame)
        anim_utils.keyframe_xp_dataref(in_obj, dataref, value)

def autodetect_frame_range(in_obj, fps=30.0):
    """
    Automatically detect the frame range for the given object or its armature.

    :param in_obj: The object to detect the frame range for.
    :param fps: The frames per second to use to calculate the end value.
    :return: A tuple containing the start and end frames and start and end values
    """
    # Try to get the action from the object itself
    action = in_obj.animation_data.action if in_obj.animation_data else None

    # If no action, check for armature modifier and get action from armature
    if not action:
        for mod in in_obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object and mod.object.animation_data:
                action = mod.object.animation_data.action
                break

    if not action:
        return (0, 0, 0.0, 0.0)

    start_frame = int(action.frame_range[0])
    end_frame = int(action.frame_range[1])
    frame_len = end_frame - start_frame + 1
    start_value = 0.0
    end_value = frame_len / fps

    return (start_frame, end_frame, start_value, end_value)