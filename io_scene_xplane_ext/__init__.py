#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Purpose:   Provides additional functionality to Blender for X-Plane, including import/export for .lins, .pols, .facs, import of .objs, and WYSIWYG materials

#Import modules
from . import props
from . import ui
from . import operators
from . import material_config

import bpy # type: ignore

#Blender plugin info
bl_info = {
    "name": "X-Plane Extensions",
    "author": "Connor Russell",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Properties > Scene > X-Plane Extensions",
    "description": "Unofficial Blender addon to add support for additional X-Plane formats and QOL improvements.",
    "git_url": "https://github.com/Connor-Russell/Blender-X-Plane-Extensions",
    "category": "Import-Export"
}

@bpy.app.handlers.persistent
def post_load(dummy):
    for mat in bpy.data.materials:
        material_config.update_settings(mat)
    
    #If any version updating needs to be done, do it here

@bpy.app.handlers.persistent
def pre_save(dummy):
    plugin_version = bl_info["version"]
    bpy.types.Scene.xp_ext.last_save_plugin_version = plugin_version[0] + plugin_version[1] + plugin_version[2]

def register():
    props.register()
    operators.register()
    ui.register()
    bpy.app.handlers.load_post.append(post_load)
    bpy.app.handlers.save_pre.append(pre_save)

def unregister():
    operators.unregister()
    props.unregister()
    ui.unregister()
    if post_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(post_load)
    if pre_save in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(pre_save)

if __name__ == "__main__":
    register()

