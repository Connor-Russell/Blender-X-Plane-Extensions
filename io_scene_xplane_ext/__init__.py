#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Purpose:   Provides a simple WYSIWYG interface for exporting X-Plane lines from Blender

#Import modules
from . import props
from . import ui
from . import operators

import bpy # type: ignore

#Blender plugin info
bl_info = {
    "name": "X-Plane Extensions",
    "author": "Connor Russell",
    "version": (0, 9),
    "blender": (3, 1, 0),
    "location": "Properties > Scene > X-Plane Extensions",
    "description": "Unofficial Blender addon to add support for additional X-Plane formats and QOL improvements.",
    "git_url": "https://github.com/Connor-Russell/X-Plane-Blender-Facade-Exporter",
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

