#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      7/10/2025
#Module:    Anim Actions
#Purpose:   This file contains functions for performing actions in regards to animations for X-Plane in Blender

import bpy

from .Helpers import anim_utils

def create_flipbook_animation(in_obj, dataref, start_value, end_value, loop_value, start_frame, end_frame, keyframe_interval):
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

    for frame in range(0, num_frames):
        #Get the frame
        frame_num = start_frame + (frame * keyframe_interval)

        #Goto the correct frame
        anim_utils.goto_frame(frame_num)
        print(frame_num)

        #Duplicate the object via operators
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        in_obj.select_set(True)
        bpy.context.view_layer.objects.active = in_obj
        bpy.ops.object.duplicate()
        anim_obj = bpy.context.active_object
        anim_obj.name = f"{in_obj.name}_anim_{frame_num}"
        in_obj.select_set(False)

        #Apply the modifiers
        for modifier in anim_obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=modifier.name)

        #Now we need to setup the animation. So we need to get the start value, and the end value, then add the animations
        start_dref_value = start_value + value_interval * frame
        end_dref_value = (start_value + value_interval * (frame + 1)) + (value_interval * 0.1)

        #Add 3 to the dataref collection
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
        anim_obj.xplane.datarefs.add()
        anim_obj.xplane.datarefs[-1].path = dataref
        anim_obj.xplane.datarefs[-1].anim_type = 'hide'
        anim_obj.xplane.datarefs[-1].show_hide_v1 = end_dref_value
        anim_obj.xplane.datarefs[-1].show_hide_v2 = end_value
        anim_obj.xplane.datarefs[-1].loop = loop_value

