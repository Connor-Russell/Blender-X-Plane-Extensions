#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    init.py
#Purpose:   Provides plugin setup, registration, and preferences for the X-Plane Extensions Blender addon.

#Import modules
from . import props
from . import ui
from . import operators
from . import material_config
from . import handler_callbacks

import bpy # type: ignore

#Blender plugin info
bl_info = {
    "name": "X-Plane Extensions",
    "author": "Connor Russell",
    "version": (1, 0, 1),
    "blender": (3, 0, 0),
    "location": "Properties > Scene > X-Plane Extensions",
    "description": "Unofficial Blender addon to add support for additional X-Plane formats and QOL improvements.",
    "git_url": "https://github.com/Connor-Russell/Blender-X-Plane-Extensions",
    "category": "Import-Export"
}

@bpy.app.handlers.persistent
def pre_save(dummy):
    plugin_version = bl_info["version"]
    bpy.context.scene.xp_ext.last_save_plugin_version.major = plugin_version[0]
    bpy.context.scene.xp_ext.last_save_plugin_version.minor = plugin_version[1]
    bpy.context.scene.xp_ext.last_save_plugin_version.patch = plugin_version[2]
    

def register():
    props.register()
    operators.register()
    ui.register()
    handler_callbacks.register()
    bpy.app.handlers.save_pre.append(pre_save)

def unregister():
    operators.unregister()
    props.unregister()
    ui.unregister()
    handler_callbacks.unregister()
    if pre_save in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(pre_save)

if __name__ == "__main__":
    register()

