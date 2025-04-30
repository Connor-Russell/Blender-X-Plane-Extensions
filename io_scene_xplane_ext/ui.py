#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    UI
#Purpose:   Provide a single file containing functions for drawing the UIs

import bpy # type: ignore
from . import props


#Facade parts UI functions

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

            if property_item.alb != "":

                box.label(text="Alpha Dither Ratio")
                row = box.row()

                row.prop(property_item, "dither_ratio")

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

def draw_fac_spelling_entry(layout, entry, collection_name, floor_index, wall_index, spelling_index, entry_index):
    row = layout.row()
    #row.prop(entry, "collection", text="Segment")

    #Find this collection in the collection list
    col = None
    for collection in bpy.data.collections:
        if collection.name == collection_name:
            col = collection
            break
    if col is None:
        raise ValueError(f"Collection '{collection_name}' not found in bpy.data.collections.")
        return

    row.prop_search(entry, "collection", col.xp_fac, "spelling_choices")
    btn_rem = row.operator("xp.add_rem_fac", text="", icon='X')
    btn_rem.collection_name = collection_name
    btn_rem.floor_index = floor_index
    btn_rem.wall_index = wall_index
    btn_rem.spelling_index = spelling_index
    btn_rem.spelling_entry_index = entry_index
    btn_rem.level = "spelling_entry"
    btn_rem.add = False

def draw_fac_spelling(layout, spelling, collection_name, floor_index, wall_index, spelling_index):
    box = layout.box()
    row = box.row()

    row.prop(spelling, "is_ui_expanded", text=f"Spelling {spelling_index + 1}", icon='TRIA_DOWN' if spelling.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
    
    if spelling.is_ui_expanded:
        btn_rem = row.operator("xp.add_rem_fac", text="", icon='X')
        btn_rem.collection_name = collection_name
        btn_rem.floor_index = floor_index
        btn_rem.wall_index = wall_index
        btn_rem.spelling_index = spelling_index
        btn_rem.level = "spelling"
        btn_rem.add = False

        for i, entry in enumerate(spelling.entries):
            draw_fac_spelling_entry(box, entry, collection_name, floor_index, wall_index, spelling_index, i)

        row = box.row()

        btn_add = row.operator("xp.add_rem_fac", text="Add Segment", icon='ADD')
        btn_add.collection_name = collection_name
        btn_add.floor_index = floor_index
        btn_add.wall_index = wall_index
        btn_add.spelling_index = spelling_index
        btn_add.spelling_entry_index = len(spelling.entries)
        btn_add.level = "spelling_entry"
        btn_add.add = True

        btn_duplicate = row.operator("xp.add_rem_fac", text="Duplicate Spelling", icon='DUPLICATE')
        btn_duplicate.collection_name = collection_name
        btn_duplicate.floor_index = floor_index
        btn_duplicate.wall_index = wall_index
        btn_duplicate.spelling_index = spelling_index
        btn_duplicate.spelling_entry_index = len(spelling.entries)
        btn_duplicate.level = "spelling"
        btn_duplicate.add = True
        btn_duplicate.duplicate = True

def draw_fac_wall(layout, wall, collection_name, floor_index, wall_index):
    box = layout.box()
    row = box.row()
    row.prop(wall, "is_ui_expanded", text=wall.name, icon='TRIA_DOWN' if wall.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
    if wall.is_ui_expanded:
        box.prop(wall, "name", text="Name")
        box.prop(wall, "min_length", text="Min Length")
        box.prop(wall, "max_length", text="Max Length")
        box.prop(wall, "min_heading", text="Min Heading")
        box.prop(wall, "max_heading", text="Max Heading")

        box.label(text="Wall Spellings")

        for i, spelling in enumerate(wall.spellings):
            draw_fac_spelling(box, spelling, collection_name, floor_index, wall_index, i)

        box.separator()

        btn_add = box.operator("xp.add_rem_fac", text="Add Spelling", icon='ADD')
        btn_add.collection_name = collection_name
        btn_add.floor_index = floor_index
        btn_add.wall_index = wall_index
        btn_add.spelling_index = len(wall.spellings)
        btn_add.level = "spelling"
        btn_add.add = True


    btn_rem = row.operator("xp.add_rem_fac", text="", icon='X')
    btn_rem.collection_name = collection_name
    btn_rem.floor_index = floor_index
    btn_rem.wall_index = wall_index
    btn_rem.level = "wall"
    btn_rem.add = False

def draw_fac_floor(layout, floor, collection_name, floor_index):
    box = layout.box()
    row = box.row()
    row.prop(floor, "is_ui_expanded", text=floor.name, icon='TRIA_DOWN' if floor.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
    if floor.is_ui_expanded:
        box.label(text=f"Floor")
        box.prop(floor, "name", text="Name")
        box.prop(floor, "roof_collection", text="Roof Collection")
        box.separator()
        box.label(text="Wall Rules:")

        for i, wall in enumerate(floor.walls):
            draw_fac_wall(box, wall, collection_name, floor_index, i)

        box.separator()
        btn_add = box.operator("xp.add_rem_fac", text="Add Wall", icon='ADD')
        btn_add.collection_name = collection_name
        btn_add.floor_index = floor_index
        btn_add.wall_index = len(floor.walls)
        btn_add.level = "wall"
        btn_add.add = True

    btn_rem = row.operator("xp.add_rem_fac", text="", icon='X')
    btn_rem.collection_name = collection_name
    btn_rem.floor_index = floor_index
    btn_rem.level = "floor"
    btn_rem.add = False

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
        layout.operator("xp_ext.export_lines", text="Export Lines")
        layout.separator()
        layout.prop(scene.xp_ext, "lin_collection_search")

        if scene.xp_ext.lin_collection_search != "":
            layout.label(text="Filtered Collections")

        #For every collection, if it exportable, draw it's params
        for col in bpy.data.collections:
            if col.xp_lin.exportable:
                #Check if the collection starts with the search name, or, the search is empty
                if scene.xp_ext.lin_collection_search == "" or (col.name.startswith(scene.xp_ext.lin_collection_search) or col.name.endswith(scene.xp_ext.lin_collection_search)):
                    box = layout.box()
                    top_row = box.row()
                    top_row.prop(col.xp_lin, "is_ui_expanded", text=col.name, icon='TRIA_DOWN' if col.xp_lin.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
                    top_row.prop(col.xp_lin, "exportable", text="Export Enabled")
                    if col.xp_lin.is_ui_expanded:
                        box.prop(col.xp_lin, "name")
                        box.prop(col.xp_lin, "mirror")
                        box.prop(col.xp_lin, "segment_count")

        #Draw a collapsable box where we can list all the collections, and whether they are exportable
        disabled_box = layout.box()
        disabled_box.prop(scene.xp_ext, "lin_disabled_collections_expanded", text="Disabled Collections", icon='TRIA_DOWN' if scene.xp_ext.lin_disabled_collections_expanded else 'TRIA_RIGHT', emboss=False)
        if scene.xp_ext.lin_disabled_collections_expanded:
            for col in bpy.data.collections:
                if not col.xp_lin.exportable:
                    #Check if the collection starts with the search name, or, the search is empty
                    if scene.xp_ext.lin_collection_search == "" or (col.name.startswith(scene.xp_ext.lin_collection_search) or col.name.endswith(scene.xp_ext.lin_collection_search)):
                        box = layout.box()
                        top_row = box.row()
                        top_row.prop(col.xp_lin, "is_ui_expanded", text=col.name, icon='TRIA_DOWN' if col.xp_lin.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
                        top_row.prop(col.xp_lin, "exportable", text="Export Disabled")
                        if col.xp_lin.is_ui_expanded:
                            box.prop(col.xp_lin, "name")
                            box.prop(col.xp_lin, "mirror")
                            box.prop(col.xp_lin, "segment_count")

class MENU_lin_layer(bpy.types.Panel):
    bl_label = "X-Plane Line Layer"
    bl_idname = "OBJECT_PT_lin_layer"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # Only show the panel if the active object is a MESH
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        #Draw the exportable checkbox
        layout.prop(obj.xp_lin, "exportable")

        #If it's exportable, draw the type selector
        if obj.xp_lin.exportable:
            layout.prop(obj.xp_lin, "type")

class MENU_mats(bpy.types.Panel):
    bl_label = "X-Plane Material Properties"
    bl_idname = "MATERIAL_PT_mats"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        # Only show the panel if there is a material
        return context.material

    def draw(self, context):
        if not context.material:
            return
        
        layout = self.layout
        material = context.material

        xp_materials = material.xp_materials

        if xp_materials:
            layout.operator("xp_ext.autodetect_texture", text="Autodetect Texture")
            layout.prop(xp_materials, "alb_texture", text="Albedo Texture")
            if xp_materials.draped:
                row = layout.row()            
                row.prop(xp_materials, "normal_tile_ratio")
                row.prop(xp_materials, "normal_texture", text="Normal Texture")
            else:
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
            layout.operator("xp_ext.update_material_nodes", text="Update Material")

            layout.separator()

            box = layout.box()

            box.label(text="Decals:")
            box.prop(xp_materials, "decal_modulator", text="Decal Modulator Texture")

            draw_decal_prop(box, xp_materials.decal_one, 0)
            draw_decal_prop(box, xp_materials.decal_two, 1)

class MENU_operations(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "X-Plane Extensions"
    bl_idname = "SCENE_PT_operations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "X-Plane Extensions"

    def draw(self, context):

        layout = self.layout

        xp_ext = bpy.context.scene.xp_ext

        layout.separator()
        layout.label(text="Auto Low-Poly Baker")
        layout.prop(xp_ext, "low_poly_bake_resolution")
        layout.prop(xp_ext, "low_poly_bake_ss_factor")
        layout.operator("xp_ext.bake_low_poly", text="Bake to Selected to Low Poly")

        layout.separator()
        layout.label(text="X-Plane Exporter Sync")
        layout.operator("xp_ext.update_collection_textures", text="Update X-Plane Export Texture Settings")

        do_test_operators = True
        if do_test_operators:
            layout.separator()
            layout.label(text="Test Operators")
            layout.operator("xp_ext.run_tests", text="Run Tests")

            layout.separator()
            btn_bake_test_base = layout.operator("xp_ext.test_config_bake_settings", text="Config Base Bake Settings")
            btn_bake_test_base.bake_type = "BASE"
            btn_bake_test_normal = layout.operator("xp_ext.test_config_bake_settings", text="Config Normal Bake Settings")
            btn_bake_test_normal.bake_type = "NORMAL"
            btn_bake_test_roughness = layout.operator("xp_ext.test_config_bake_settings", text="Config Roughness Bake Settings")
            btn_bake_test_roughness.bake_type = "ROUGHNESS"
            btn_bake_test_metalness = layout.operator("xp_ext.test_config_bake_settings", text="Config Metalness Bake Settings")
            btn_bake_test_metalness.bake_type = "METALNESS"
            btn_bake_test_lit = layout.operator("xp_ext.test_config_bake_settings", text="Config Lit Bake Settings")
            btn_bake_test_lit.bake_type = "LIT"
            btn_bake_test_reset = layout.operator("xp_ext.test_config_bake_settings", text="Reset Bake Settings")
            btn_bake_test_reset.bake_type = "RESET"

class MENU_facade(bpy.types.Panel):
    """Creates a Panel in the scene properties window"""
    bl_label = "X-Plane Facade Exporter"
    bl_idname = "SCENE_PT_facade_exporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):

        layout = self.layout

        #Draw the export button
        layout.operator("xp_ext.export_facades", text="Export All")

        layout.separator()

        layout.prop(context.scene.xp_ext, "fac_collection_search")
        if context.scene.xp_ext.fac_collection_search != "":
            layout.label(text="Filtered Collections")

        #Function to draw all the properties for the collection. Just so we can reuse it for the disabled collections
        def draw_collection(col, in_layout):
            fac = col.xp_fac

            box = in_layout.box()
            top_row = box.row()
            top_row.prop(col.xp_fac, "is_ui_expanded", text=col.name, icon='TRIA_DOWN' if col.xp_fac.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
            top_row.prop(col.xp_fac, "exportable", text="Export Enabled")
            if col.xp_fac.is_ui_expanded:
                box.prop(fac, "name")

                box.separator()

                box.label(text="Global Properties:")
                box.prop(fac, "graded")
                box.prop(fac, "ring")

                box.separator()

                #Wall properties-----------------------------------------------------------------------------------------

                wall_box = box.box()

                wall_box.label(text="Wall Properties:")
                wall_box.prop(fac, "render_wall")
                if fac.render_wall:
                    wall_box.prop(fac, "wall_material")

                box.separator()

                #Roof properties-----------------------------------------------------------------------------------------

                roof_box = box.box()

                roof_box.label(text="Roof Properties:")
                roof_box.prop(fac, "render_roof")
                if fac.render_roof:
                    roof_box.prop(fac, "roof_material")

                box.separator()

                #Wall spellings-----------------------------------------------------------------------------------------

                spelling_box = box
                spelling_box.label(text="Floor Definitions:")
                for i, floor in enumerate(fac.floors):
                    if floor.name == "":
                        floor.name = f"Floor {i}"
                    draw_fac_floor(spelling_box, floor, col.name, i)
                
                btn_add = spelling_box.operator("xp.add_rem_fac", text="Add Floor", icon='ADD')
                btn_add.collection_name = col.name
                btn_add.floor_index = len(fac.floors)
                btn_add.level = "floor"
                btn_add.add = True

        for col in bpy.data.collections:
            if col.xp_fac.exportable:
                if context.scene.xp_ext.fac_collection_search != "" and not (col.name.startswith(context.scene.xp_ext.fac_collection_search) or col.name.endswith(context.scene.xp_ext.fac_collection_search)):
                    continue
                draw_collection(col, layout)
                
        disabled_collections = layout.box()
        disabled_collections.prop(context.scene.xp_ext, "fac_disabled_collections_expanded", text="Disabled Collections", icon='TRIA_DOWN' if context.scene.xp_ext.fac_disabled_collections_expanded else 'TRIA_RIGHT', emboss=False)
        if context.scene.xp_ext.fac_disabled_collections_expanded:
            for col in bpy.data.collections:
                if not col.xp_fac.exportable:
                    if context.scene.xp_ext.fac_collection_search != "" and not (col.name.startswith(context.scene.xp_ext.fac_collection_search) or col.name.endswith(context.scene.xp_ext.fac_collection_search)):
                        continue
                    draw_collection(col, disabled_collections)

class MENU_attached_object(bpy.types.Panel):
    """Creates a Panel in the object properties window"""
    bl_label = "X-Plane Attached Object"
    bl_idname = "OBJECT_PT_attached_object"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # Only show the panel if the active object is an EMPTY
        return context.object and context.object.type == 'EMPTY'

    def draw(self, context):

        layout = self.layout

        attached_obj = context.object.xp_attached_obj

        if context.object.type == 'EMPTY':
            layout.prop(attached_obj, "exportable")
            layout.prop(attached_obj, "draped")
            layout.prop(attached_obj, "resource")

class MENU_fac_mesh(bpy.types.Panel):
    """Creates a Panel in the object properties window"""
    bl_label = "X-Plane Facade Mesh"
    bl_idname = "OBJECT_PT_facade_object"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # Only show the panel if the active object is a MESH
        return context.object and context.object.type == 'MESH'

    def draw(self, context):

        layout = self.layout

        fac_mesh = context.object.xp_fac_mesh

        #If this is a mesh, we show the mesh options of cut, and exportable
        if context.object.type == 'MESH':
            layout.prop(fac_mesh, "far_lod")
            layout.prop(fac_mesh, "group")
            layout.prop(fac_mesh, "cuts")
            layout.prop(fac_mesh, "exportable")

def register():
    bpy.utils.register_class(MENU_lin_exporter)
    bpy.utils.register_class(MENU_lin_layer)
    bpy.utils.register_class(MENU_mats)
    bpy.utils.register_class(MENU_operations)
    bpy.utils.register_class(MENU_facade)
    bpy.utils.register_class(MENU_attached_object)
    bpy.utils.register_class(MENU_fac_mesh)

def unregister():
    bpy.utils.unregister_class(MENU_lin_exporter)
    bpy.utils.unregister_class(MENU_lin_layer)
    bpy.utils.unregister_class(MENU_mats)
    bpy.utils.unregister_class(MENU_operations)
    bpy.utils.unregister_class(MENU_facade)
    bpy.utils.unregister_class(MENU_attached_object)
    bpy.utils.unregister_class(MENU_fac_mesh)