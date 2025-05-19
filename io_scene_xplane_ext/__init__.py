#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Purpose:   Provides additional functionality to Blender for X-Plane, including import/export for .lins, .pols, .facs, import of .objs, and WYSIWYG materials

#Import modules
from . import props
from . import ui
from . import operators

import bpy # type: ignore

#Blender plugin info
bl_info = {
    "name": "X-Plane Extensions",
    "author": "Connor Russell",
    "version": (0, 9, 7),
    "blender": (3, 0, 0),
    "location": "Properties > Scene > X-Plane Extensions",
    "description": "Unofficial Blender addon to add support for additional X-Plane formats and QOL improvements.",
    "git_url": "https://github.com/Connor-Russell/Blender-X-Plane-Extensions",
    "category": "Import-Export"
}

def register():
    props.register()
    operators.register()
    ui.register()

def unregister():
    operators.unregister()
    props.unregister()
    ui.unregister()

if __name__ == "__main__":
    register()

