#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      9/9/2026
#Module:    depsgraph_updates.py
#Purpose:   Provide a single register/unregister point for all callbacks for depsgraph/file load

import bpy # type: ignore
from . import props
from bpy.app.handlers import persistent # type: ignore
from .Helpers import log_utils
from .Types import xp_attached_obj_preview
import os

def update_optional_registrations(self=None, context=None):
    if bpy.context.preferences.addons[__package__].preferences.do_automanage_preview_objects:
        if xp_attached_obj_preview.update_attached_obj_previews not in bpy.app.handlers.depsgraph_update_pre:
            bpy.app.handlers.depsgraph_update_pre.append(xp_attached_obj_preview.update_attached_obj_previews)
        if xp_attached_obj_preview.clear_existing_objects not in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.append(xp_attached_obj_preview.clear_existing_objects)
    else:
        if xp_attached_obj_preview.update_attached_obj_previews in bpy.app.handlers.depsgraph_update_pre:
            bpy.app.handlers.depsgraph_update_pre.remove(xp_attached_obj_preview.update_attached_obj_previews)
        if xp_attached_obj_preview.clear_existing_objects in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(xp_attached_obj_preview.clear_existing_objects)


def register():
    
    bpy.app.handlers.depsgraph_update_pre.append(props.update_fac_spelling_choices_depgraph_handler)
    bpy.app.handlers.load_post.append(props.update_fac_spelling_choices_load_handler)

    #Register optional registrations
    if bpy.context.preferences.addons[__package__].preferences.do_automanage_preview_objects:
        if xp_attached_obj_preview.update_attached_obj_previews not in bpy.app.handlers.depsgraph_update_pre:
            bpy.app.handlers.depsgraph_update_pre.append(xp_attached_obj_preview.update_attached_obj_previews)
        if xp_attached_obj_preview.clear_existing_objects not in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.append(xp_attached_obj_preview.clear_existing_objects)

def unregister():
    bpy.app.handlers.load_post.remove(props.update_fac_spelling_choices_load_handler)
    bpy.app.handlers.depsgraph_update_pre.remove(props.update_fac_spelling_choices_depgraph_handler)

    # Unregister optional registrations
    if xp_attached_obj_preview.update_attached_obj_previews in bpy.app.handlers.depsgraph_update_pre:
        bpy.app.handlers.depsgraph_update_pre.remove(xp_attached_obj_preview.update_attached_obj_previews)
    if xp_attached_obj_preview.clear_existing_objects in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(xp_attached_obj_preview.clear_existing_objects)


    
