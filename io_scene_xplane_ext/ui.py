#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    UI
#Purpose:   Provide a single file containing functions for drawing the UIs

import bpy # type: ignore
from . import props

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
        if not context.material:
            return
        
        layout = self.layout
        material = context.material

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
        layout.prop(xp_ext, "low_poly_bake_ss_factor")
        layout.operator("xp_ext.bake_low_poly", text="Bake to Selected to Low Poly")

        layout.separator()
        layout.operator("xp_ext.update_collection_textures", text="Update X-Plane Export Texture Settings")

class MENU_facade(bpy.types.Panel):
    """Creates a Panel in the scene properties window"""
    bl_label = "X-Plane Facade Exporter"
    bl_idname = "SCENE_PT_facade_exporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):

        layout = self.layout

        facade_exporter = context.scene.facade_exporter

        #Export button
        layout.operator("blender_utils.export_facade")
        layout.prop(facade_exporter, "facade_name")

        layout.separator()

        layout.label(text="Global Properties:")
        layout.prop(facade_exporter, "graded")
        layout.prop(facade_exporter, "ring")
        layout.prop(facade_exporter, "solid")
        layout.prop(facade_exporter, "layergroup")
        layout.prop(facade_exporter, "layergroup_draped")

        layout.separator()

        #Wall properties-----------------------------------------------------------------------------------------

        box = layout.box()

        box.label(text="Wall Properties:")
        box.prop(facade_exporter, "render_wall")
        if facade_exporter.render_wall:
            box.prop(facade_exporter, "wall_texture_alb")
            box.prop(facade_exporter, "wall_texture_nml")
            box.prop(facade_exporter, "wall_texture_nml_scale")
            
            box.separator()

            #Decals
            box.prop(facade_exporter, "wall_seperate_normal_decals")
            box.prop(facade_exporter, "wall_modulator_texture")
            for index, item in enumerate(facade_exporter.wall_decals):
                if item.visible:
                    props.PROP_decal.draw(box, item, index)
        

        layout.separator()

        #Roof properties-----------------------------------------------------------------------------------------

        box = layout.box()

        box.label(text="Roof Properties:")
        box.prop(facade_exporter, "render_roof")
        if facade_exporter.render_roof:
            box.prop(facade_exporter, "roof_texture_alb")
            box.prop(facade_exporter, "roof_texture_nml")
            box.prop(facade_exporter, "roof_texture_nml_scale")
            box.prop(facade_exporter, "roof_height")

            box.separator()

            #Decals
            box.prop(facade_exporter, "roof_seperate_normal_decals")
            box.prop(facade_exporter, "roof_modulator_texture")
            for index, item in enumerate(facade_exporter.roof_decals):
                if item.visible:
                    DecalProperties.DecalProperties.draw(box, item, index)

        layout.separator()

        #Wall spettings-----------------------------------------------------------------------------------------

        box = layout.box()

        box.label(text="Facade Wall Spellings:")

        # Display the collection of text items
        wall_counter = 0
        for index, item in enumerate(facade_exporter.spellings):
            row = box.row()
            col1 = row.column()
            col2 = row.column()
            
            #We will switch which properties we show based on whether this is a wall or a spelling
            col1.prop(item, "type", text="", expand=False)

            if item.type == "WALL":
                col2.prop(item, "wall_name")
                row2 = box.row()
                row2.prop(item, "min_width")
                row2.prop(item, "max_width")
                row2.prop(item, "min_heading")
                row2.prop(item, "max_heading")
            elif item.type == "WALL_RULE":
                row2 = box.row()
                row2.prop(item, "min_width")
                row2.prop(item, "max_width")
                row2.prop(item, "min_heading")
                row2.prop(item, "max_heading")
            else:
                col2.prop(item, "spellings")
            
            row.operator("object.remove_spelling", text="", icon='X').index = index

        # Add button to add new text items
        box.operator("object.add_spelling", text="Add Spelling")

class MENU_attached_object(bpy.types.Panel):
    """Creates a Panel in the object properties window"""
    bl_label = "X-Plane Attached Object"
    bl_idname = "OBJECT_PT_facade_object"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):

        layout = self.layout

        facade_object = context.object.facade_object

        #If this is a mesh, we show the mesh options of cut, and exportable
        if context.object.type == 'MESH':
            layout.label(text="Facade Mesh Properties")
            layout.separator()
            layout.prop(facade_object, "far_lod")
            layout.prop(facade_object, "group")
            layout.prop(facade_object, "cuts")
            layout.prop(facade_object, "exportable")

        elif context.object.type == 'EMPTY':
            layout.label(text="Facade Attached Object Properties")
            layout.separator()
            layout.prop(facade_object, "exportable")
            layout.prop(facade_object, "draped")
            layout.prop(facade_object, "resource")

        else:
            layout.label(text="This object is not a mesh or empty")

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