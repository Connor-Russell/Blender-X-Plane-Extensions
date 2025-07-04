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

class XP_EXT_prefs(bpy.types.AddonPreferences):
    bl_idname = __name__

    #Suffixes for various file types

    suffix_combined_normal: bpy.props.StringProperty(
        name="Suffic Combined Normal",
        description="Suffix for combined normal maps",
        default="_NML",
    ) #type: ignore

    suffix_albedo: bpy.props.StringProperty(
        name="Suffix Albedo",
        description="Suffix for albedo maps",
        default="",
    ) #type: ignore

    suffix_lit: bpy.props.StringProperty(
        name="Suffix Lit",
        description="Suffix for lit maps",
        default="_LIT",
    ) #type: ignore

    suffix_normal: bpy.props.StringProperty(
        name="Suffix Normal",
        description="Suffix for normal maps",
        default="_NRM",
    ) #type: ignore

    suffix_material: bpy.props.StringProperty(
        name="Suffix Material",
        description="Suffix for material files",
        default="_MAT",
    ) #type: ignore

    suffix_lod_bake: bpy.props.StringProperty(
        name="Suffix LOD Bake",
        description="Suffix for baked LOD textures",
        default="_LOD",
    ) #type: ignore

    #General Settings

    show_only_relevant_settings: bpy.props.BoolProperty(
        name="Show Only Relevant Settings",
        description="Only show settings that are relevant to the current collection. I.e. facade settigns will not be shown for an object in a collection that is not enabled to export as a facade.",
        default=True,
    ) #type: ignore

    always_fully_reload_images: bpy.props.BoolProperty(
        name="Always Fully Reload Images",
        description="Always fully reload images when updating materials",
        default=False,
    ) #type: ignore

    def draw(self, context):
        layout = self.layout
        layout.label(text="X-Plane Extensions Preferences")

        #General Settings
        layout.prop(self, "show_only_relevant_settings")
        layout.prop(self, "always_fully_reload_images")

        layout.separator()

        #Suffixes
        layout.label(text="Suffixes for texture autodetecting and baking:")
        layout.prop(self, "suffix_albedo")
        layout.prop(self, "suffix_lit")
        layout.prop(self, "suffix_combined_normal")
        layout.prop(self, "suffix_normal")
        layout.prop(self, "suffix_material")
        layout.prop(self, "suffix_lod_bake")

@bpy.app.handlers.persistent
def pre_save(dummy):
    plugin_version = bl_info["version"]
    bpy.types.Scene.xp_ext.last_save_plugin_version = plugin_version[0] + plugin_version[1] + plugin_version[2]

def register():
    bpy.utils.register_class(XP_EXT_prefs)
    props.register()
    operators.register()
    ui.register()
    bpy.app.handlers.save_pre.append(pre_save)

def unregister():
    bpy.utils.unregister_class(XP_EXT_prefs)
    operators.unregister()
    props.unregister()
    ui.unregister()
    if pre_save in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(pre_save)

if __name__ == "__main__":
    register()

