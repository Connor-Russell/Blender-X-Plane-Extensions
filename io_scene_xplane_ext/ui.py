#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    UI
#Purpose:   Provide a single file containing functions for drawing the UIs

import bpy # type: ignore

def draw_decal_prop(layout, property_item, index):
    layout.prop(property_item, "enabled", text=f"Decal {index + 1}")

    if property_item.enabled:

        box = layout.box()

        #Normal follows albedo
        box.prop(property_item, "normal_follows_albedo")

        #Decal Library (broken in xp currently)
        #box.prop(property_item, "decal_lib")

        if property_item.decal_lib != "":
            box.label(text="Decal asset is set, other properties are ignored.")
            return

        #Textures
        box.prop(property_item, "alb")
        box.prop(property_item, "nml")

        box.separator()

        #UVs
        if property_item.alb != "" or (property_item.normal_follows_albedo and property_item.nml != ""):
            row = box.row()
            row.prop(property_item, "projected")

            if property_item.projected:
                row.prop(property_item, "scale_x")
                row.prop(property_item, "scale_y")
            else:
                row.prop(property_item, "tile_ratio")

        if (not property_item.normal_follows_albedo) and property_item.nml != "":
            box.separator()
            box.label(text="Normal Map Scale")

            #Normal Map
            box.prop(property_item, "nml_projected")

            if property_item.nml_projected:
                row = box.row()
                row.prop(property_item, "nml_scale_x")
                row.prop(property_item, "nml_scale_y")
            else:
                row = box.row()
                row.prop(property_item, "nml_tile_ratio")

        box.separator()

        #Dither (not supported on objs)
        #if property_item.type != "NML":
            #box.prop(property_item, "dither_ratio")

        box.separator()

        #RGB strength and keying
        if (property_item.alb != "") or (property_item.normal_follows_albedo and property_item.nml != ""):
            box.label(text="RGB Decal Application Control")
            row = box.row()
            row.prop(property_item, "rgb_strength_constant")
            row.prop(property_item, "rgb_strength_modulator")
            row = box.row()
            row.prop(property_item, "rgb_decal_key_red")
            row.prop(property_item, "rgb_decal_key_green")
            row.prop(property_item, "rgb_decal_key_blue")
            row.prop(property_item, "rgb_decal_key_alpha")

            box.separator()

            box.label(text="Alpha Decal Application Control")
            row = box.row()
            row.prop(property_item, "alpha_strength_constant")
            row.prop(property_item, "alpha_strength_modulator")
            row = box.row()
            row.prop(property_item, "alpha_decal_key_red")
            row.prop(property_item, "alpha_decal_key_green")
            row.prop(property_item, "alpha_decal_key_blue")
            row.prop(property_item, "alpha_decal_key_alpha")

        if (not property_item.normal_follows_albedo) and property_item.nml != "":
            box.separator()

            box.label(text="Normal Decal Application Control")
            row = box.row()
            row.prop(property_item, "nml_strength_constant")
            row.prop(property_item, "nml_strength_modulator")
            row = box.row()
            row.prop(property_item, "nml_decal_key_red")
            row.prop(property_item, "nml_decal_key_green")
            row.prop(property_item, "nml_decal_key_blue")
            row.prop(property_item, "nml_decal_key_alpha")

class MENU_lin_exporter(bpy.types.Panel):
    bl_label = "X-Plane Line Exporter"
    bl_idname = "SCENE_PT_lin_exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #Draw the export button
        layout.operator("xp.lin_exporter", text="Export Lines")
        layout.separator()
        layout.prop(scene.xp_lin, "collection_search")

        if scene.xp_lin.collection_search != "":
            layout.label(text="Filtered Collections")

        #For every collection, if it exportable, draw it's params
        for col in bpy.data.collections:
            if col.xp_lin.is_exportable:
                #Check if the collection starts with the search name, or, the search is empty
                if scene.xp_lin.collection_search == "" or (col.name.startswith(scene.xp_lin.collection_search) or col.name.endswith(scene.xp_lin.collection_search)):
                    box = layout.box()
                    top_row = box.row()
                    top_row.prop(col.xp_lin, "is_ui_expanded", text=col.name, icon='TRIA_DOWN' if col.xp_lin.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
                    top_row.prop(col.xp_lin, "is_exportable", text="Export Enabled")
                    if col.xp_lin.is_ui_expanded:
                        box.prop(col.xp_lin, "export_path")
                        box.prop(col.xp_lin, "mirror")
                        box.prop(col.xp_lin, "segment_count")


        #Draw a collapsable box where we can list all the collections, and whether they are exportable
        disabled_box = layout.box()
        disabled_box.prop(scene.xp_lin, "exportable_collections_expanded", text="Disabled Collections", icon='TRIA_DOWN' if scene.xp_lin.exportable_collections_expanded else 'TRIA_RIGHT', emboss=False)
        if scene.xp_ext.exportable_collections_expanded:
            for col in bpy.data.collections:
                if not col.xp_lin.is_exportable:
                    #Check if the collection starts with the search name, or, the search is empty
                    if scene.xp_lin.collection_search == "" or (col.name.startswith(scene.xp_lin.collection_search) or col.name.endswith(scene.xp_lin.collection_search)):
                        box = disabled_box.box()
                        top_row = box.row()
                        top_row.prop(col.xp_lin, "is_ui_expanded", text=col.name, icon='TRIA_DOWN' if col.xp_lin.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
                        top_row.prop(col.xp_lin, "is_exportable", text="Export Disabled")
                        if col.xp_lin.is_ui_expanded:
                            box.prop(col.xp_lin, "export_path")
                            box.prop(col.xp_lin, "mirror")
                            box.prop(col.xp_lin, "segment_count")

class MENU_lin_layer(bpy.types.Panel):
    bl_label = "X-Plane Line Layer"
    bl_idname = "OBJECT_PT_lin_layer"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        #Draw the exportable checkbox
        layout.prop(obj.xp_lin, "is_exportable")

        #If it's exportable, draw the type selector
        if obj.xp_lin.is_exportable:
            layout.prop(obj.xp_lin, "type")

class MENU_mats(bpy.types.Panel):
    bl_label = "X-Plane Material Properties"
    bl_idname = "MaterialMenuBlenderUtils"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        material = context.material

        if not material:
            return

        xp_materials = material.xp_materials

        if xp_materials:
            layout.operator("xp_mats.autodetect_texture", text="Autodetect Texture")
            layout.prop(xp_materials, "alb_texture", text="Albedo Texture")
            layout.prop(xp_materials, "normal_texture", text="Normal Texture")
            layout.prop(xp_materials, "lit_texture", text="Lit Texture")
            if (xp_materials.lit_texture != ""):
                layout.prop(xp_materials, "brightness", text="Brightness")
            layout.prop(xp_materials, "draped", text="Draped")
            layout.prop(xp_materials, "hard", text="Hard")
            layout.prop(xp_materials, "blend_alpha", text="Blend Alpha")
            if (not xp_materials.blend_alpha):
                layout.prop(xp_materials, "blend_cutoff", text="Blend Cutoff")
            layout.prop(xp_materials, "polygon_offset", text="Polygon Offset")
            layout.prop(xp_materials, "cast_shadow", text="Casts Shadows")
            layout.prop(xp_materials, "layer_group", text="Layer Group")
            layout.prop(xp_materials, "layer_group_offset", text="Layer Group Offset")
            layout.operator("xp_mats.update_material_nodes", text="Update Material")

            layout.separator()

            box = layout.box()

            box.label(text="Decals:")
            box.prop(xp_materials, "decal_modulator", text="Decal Modulator Texture")

            draw_decal_prop(box, xp_materials.decal_one, 0)
            draw_decal_prop(box, xp_materials.decal_two, 1)

class MENU_operations(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "X-Plane Materials"
    bl_idname = "MenuXPMats"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "X-Plane Materials"

    def draw(self, context):

        layout = self.layout

        xp_ext = bpy.context.scene.xp_ext

        layout.separator()
        layout.label(text="Auto Low-Poly Baker")
        layout.prop(xp_ext, "low_poly_bake_resolution")
        layout.operator("xp_ext.bake_low_poly", text="Bake to Selected to Low Poly")

        layout.separator()
        layout.operator("xp_ext.update_collection_textures", text="Update X-Plane Export Texture Settings")

        #if TestMode:
        #    layout.separator()
        #    layout.label(text="Tests")
        #    layout.separator()
        #    layout.label(text="Bake Utils")
        #    layout.operator("xp_mats.test_config_source_material_base", text="Test Config Source Material Base")
        #    layout.operator("xp_mats.test_config_source_material_normal", text="Test Config Source Material Normal")
        #    layout.operator("xp_mats.test_config_source_material_roughness", text="Test Config Source Material Roughness")
        #    layout.operator("xp_mats.test_config_source_material_metalness", text="Test Config Source Material Metalness")
        #    layout.operator("xp_mats.test_config_source_material_lit", text="Test Config Source Material Lit")
        #    layout.operator("xp_mats.test_config_target_bake_texture", text="Test Config Target Bake Texture")
        #    layout.operator("xp_mats.test_config_bake_settings_base", text="Test Config Bake Settings Base")
        #    layout.operator("xp_mats.test_config_bake_settings_normal", text="Test Config Bake Settings Normal")
        #    layout.operator("xp_mats.test_config_bake_settings_roughness", text="Test Config Bake Settings Roughness")
        #    layout.operator("xp_mats.test_config_bake_settings_metalness", text="Test Config Bake Settings Metalness")
        #    layout.operator("xp_mats.test_config_bake_settings_lit", text="Test Config Bake Settings Lit")
        #    layout.operator("xp_mats.test_bake_texture", text="Test Bake Texture")
        #    layout.operator("xp_mats.test_reset_source_materials", text="Test Reset Source Materials")
        #    layout.operator("xp_mats.test_full_base_bake", text="Test_full_base_bake")

def register():
    bpy.utils.register_class(MENU_lin_exporter)
    bpy.utils.register_class(MENU_lin_layer)
    bpy.utils.register_class(MENU_mats)
    bpy.utils.register_class(MENU_operations)

def unregister():
    bpy.utils.unregister_class(MENU_lin_exporter)
    bpy.utils.unregister_class(MENU_lin_layer)
    bpy.utils.unregister_class(MENU_mats)
    bpy.utils.unregister_class(MENU_operations)