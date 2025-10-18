#Project: in-app_anim_tool_tests.py
#Author: Connor Russell
#Date: 9/22/2025
#Module: in_app_anim_tool_test.py
#Purpose: Define in app tests here, used in in_ap_anim_tests.py

import bpy
import os
import sys

def inapp_flipbook_test(in_collection):
    #Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    #Iterate over all objects in this collection and select them.
    for obj in in_collection.all_objects:
        obj.select_set(True)

    #Set the anim operation properties
    bpy.data.scenes["Scene"].xp_ext.autoanim_frame_start = 1
    bpy.data.scenes["Scene"].xp_ext.autoanim_frame_end = 255
    bpy.data.scenes["Scene"].xp_ext.autoanim_dataref = "my_dataref123[4]"
    bpy.data.scenes["Scene"].xp_ext.autoanim_start_value = 0
    bpy.data.scenes["Scene"].xp_ext.autoanim_end_value = 100
    bpy.data.scenes["Scene"].xp_ext.autoanim_loop_value = 50

    bpy.ops.xp_ext.generate_flipbook_animation()

def inapp_autokeyframe_test(in_collection):
    #Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    #Iterate over all objects in this collection and select them.
    for obj in in_collection.all_objects:
        obj.select_set(True)

    #Set the anim operation properties
    bpy.data.scenes["Scene"].xp_ext.autoanim_frame_start = 1
    bpy.data.scenes["Scene"].xp_ext.autoanim_frame_end = 255
    bpy.data.scenes["Scene"].xp_ext.autoanim_dataref = "my_dataref123[4]"
    bpy.data.scenes["Scene"].xp_ext.autoanim_start_value = 0
    bpy.data.scenes["Scene"].xp_ext.autoanim_end_value = 100
    bpy.data.scenes["Scene"].xp_ext.autoanim_loop_value = 50

    bpy.ops.xp_ext.auto_keyframe_animation()
