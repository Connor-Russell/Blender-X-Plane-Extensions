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

def register():
    
    bpy.app.handlers.depsgraph_update_pre.append(props.update_fac_spelling_choices_depgraph_handler)
    bpy.app.handlers.load_post.append(props.update_fac_spelling_choices_load_handler)

def unregister():
    bpy.app.handlers.load_post.remove(props.update_fac_spelling_choices_load_handler)
    bpy.app.handlers.depsgraph_update_pre.remove(props.update_fac_spelling_choices_depgraph_handler)



    
