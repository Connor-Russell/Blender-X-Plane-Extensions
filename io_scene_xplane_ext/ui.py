#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    ui.py
#Purpose:   Provide UI classes for the plugin

import bpy # type: ignore
from . import props

def draw_decal_prop(layout, property_item, index, material_name=""):
    box = layout.box()

    decal_name = "Decal " + str(index + 1) + (" - Normal" if property_item.is_normal else " - Albedo")

    row = box.row()
    split = row.split(factor=0.7)

    col_left = split.column()
    row_left = col_left.row(align=True)
    row_left.alignment = 'LEFT'
    row_left.prop(property_item, "is_ui_expanded", text=decal_name, icon='TRIA_DOWN' if property_item.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
    row_left.prop(property_item, "enabled", text="")

    #Copy and paste operators
    col_right = split.column()
    row_right = col_right.row(align=True)
    row_right.alignment = 'RIGHT'
    btn_copy = row_right.operator("xp_ext.copy_decal", text="", icon='COPYDOWN')
    btn_copy.decal_index = index
    btn_copy.material_name = material_name
    btn_paste = row_right.operator("xp_ext.paste_decal", text="", icon='PASTEDOWN')
    btn_paste.decal_index = index
    btn_paste.material_name = material_name

    if property_item.is_ui_expanded:
        box.prop(property_item, "texture")

        box.separator()

        box.prop(property_item, "projected")

        row = box.row()

        if property_item.projected:
            row.prop(property_item, "scale_x")
            row.prop(property_item, "scale_y")
        else:
            row.prop(property_item, "tile_ratio")

        if not property_item.is_normal:
            box.separator()
            box.prop(property_item, "dither_ratio")

        box.separator()

        row = box.row()

        row.prop(property_item, "strength_constant")
        row.prop(property_item, "strength_modulator")

        row = box.row()

        row.prop(property_item, "strength_key_red")
        row.prop(property_item, "strength_key_green")
        row.prop(property_item, "strength_key_blue")
        row.prop(property_item, "strength_key_alpha")

        if not property_item.is_normal:
            box.separator()

            row = box.row()

            row.prop(property_item, "strength2_constant")
            row.prop(property_item, "strength2_modulator")

            row = box.row()

            row.prop(property_item, "strength2_key_red")
            row.prop(property_item, "strength2_key_green")
            row.prop(property_item, "strength2_key_blue")
            row.prop(property_item, "strength2_key_alpha")

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
    btn_rem = row.operator("xp_ext.add_rem_fac", text="", icon='X')
    btn_rem.collection_name = collection_name
    btn_rem.floor_index = floor_index
    btn_rem.wall_index = wall_index
    btn_rem.spelling_index = spelling_index
    btn_rem.spelling_entry_index = entry_index
    btn_rem.level = "spelling_entry"
    btn_rem.add = False

def draw_fac_spelling(layout, spelling, collection_name, floor_index, wall_index, spelling_index, spelling_len=0):
    box = layout.box()
    row = box.row()

    row.prop(spelling, "is_ui_expanded", text=f"Spelling {spelling_index + 1}", icon='TRIA_DOWN' if spelling.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
    
    if spelling_index != 0:
        btn_swap_up = row.operator("xp_ext.fac_swap_spellings", text="", icon='TRIA_UP')
        btn_swap_up.collection_name = collection_name
        btn_swap_up.floor_index = floor_index
        btn_swap_up.wall_index = wall_index
        btn_swap_up.spelling_index_1 = spelling_index - 1
        btn_swap_up.spelling_index_2 = spelling_index

    if spelling_index != spelling_len - 1:
        btn_swap_down = row.operator("xp_ext.fac_swap_spellings", text="", icon='TRIA_DOWN')
        btn_swap_down.collection_name = collection_name
        btn_swap_down.floor_index = floor_index
        btn_swap_down.wall_index = wall_index
        btn_swap_down.spelling_index_1 = spelling_index
        btn_swap_down.spelling_index_2 = spelling_index + 1

    btn_rem = row.operator("xp_ext.add_rem_fac", text="", icon='X')
    btn_rem.collection_name = collection_name
    btn_rem.floor_index = floor_index
    btn_rem.wall_index = wall_index
    btn_rem.spelling_index = spelling_index
    btn_rem.level = "spelling"
    btn_rem.add = False
    
    if spelling.is_ui_expanded:
        for i, entry in enumerate(spelling.entries):
            draw_fac_spelling_entry(box, entry, collection_name, floor_index, wall_index, spelling_index, i)

        row = box.row()

        btn_add = row.operator("xp_ext.add_rem_fac", text="Add Segment", icon='ADD')
        btn_add.collection_name = collection_name
        btn_add.floor_index = floor_index
        btn_add.wall_index = wall_index
        btn_add.spelling_index = spelling_index
        btn_add.spelling_entry_index = len(spelling.entries)
        btn_add.level = "spelling_entry"
        btn_add.add = True

        btn_duplicate = row.operator("xp_ext.fac_duplicate_spelling", text="Duplicate Spelling", icon='DUPLICATE')
        btn_duplicate.collection_name = collection_name
        btn_duplicate.floor_index = floor_index
        btn_duplicate.wall_index = wall_index
        btn_duplicate.spelling_index = spelling_index

def draw_fac_wall(layout, wall, collection_name, floor_index, wall_index, wall_len=0):
    box = layout.box()
    row = box.row()
    row.prop(wall, "is_ui_expanded", text=wall.name, icon='TRIA_DOWN' if wall.is_ui_expanded else 'TRIA_RIGHT', emboss=False)

    if wall_index != 0:
        btn_swap_up = row.operator("xp_ext.fac_swap_walls", text="", icon='TRIA_UP')
        btn_swap_up.collection_name = collection_name
        btn_swap_up.floor_index = floor_index
        btn_swap_up.wall_index_1 = wall_index - 1
        btn_swap_up.wall_index_2 = wall_index

    if wall_index != wall_len - 1:
        btn_swap_down = row.operator("xp_ext.fac_swap_walls", text="", icon='TRIA_DOWN')
        btn_swap_down.collection_name = collection_name
        btn_swap_down.floor_index = floor_index
        btn_swap_down.wall_index_1 = wall_index
        btn_swap_down.wall_index_2 = wall_index + 1

    btn_rem = row.operator("xp_ext.add_rem_fac", text="", icon='X')
    btn_rem.collection_name = collection_name
    btn_rem.floor_index = floor_index
    btn_rem.wall_index = wall_index
    btn_rem.level = "wall"
    btn_rem.add = False

    if wall.is_ui_expanded:
        box.prop(wall, "name", text="Name")
        row = box.row()
        row.prop(wall, "min_length", text="Min Length")
        row.prop(wall, "max_length", text="Max Length")
        row = box.row()
        row.prop(wall, "min_heading", text="Min Heading")
        row.prop(wall, "max_heading", text="Max Heading")

        box.label(text="Wall Spellings")

        for i, spelling in enumerate(wall.spellings):
            draw_fac_spelling(box, spelling, collection_name, floor_index, wall_index, i, len(wall.spellings))

        box.separator()

        row=box.row()

        btn_add = row.operator("xp_ext.add_rem_fac", text="Add Spelling", icon='ADD')
        btn_add.collection_name = collection_name
        btn_add.floor_index = floor_index
        btn_add.wall_index = wall_index
        btn_add.spelling_index = len(wall.spellings)
        btn_add.level = "spelling"
        btn_add.add = True
        btn_add.duplicate = False

        btn_duplicate = row.operator("xp_ext.fac_duplicate_wall", text="Duplicate Wall", icon='DUPLICATE')
        btn_duplicate.collection_name = collection_name
        btn_duplicate.floor_index = floor_index
        btn_duplicate.wall_index = wall_index

def draw_fac_floor(layout, floor, collection_name, floor_index, floor_len=0):
    #Get the collection from the collection name
    col = None
    for collection in bpy.data.collections:
        if collection.name == collection_name:
            col = collection
            break

    box = layout.box()
    row = box.row()
    row.prop(floor, "is_ui_expanded", text=floor.name, icon='TRIA_DOWN' if floor.is_ui_expanded else 'TRIA_RIGHT', emboss=False)

    if floor_index != 0:
        btn_swap_up = row.operator("xp_ext.fac_swap_floors", text="", icon='TRIA_UP')
        btn_swap_up.collection_name = collection_name
        btn_swap_up.floor_index_1 = floor_index - 1
        btn_swap_up.floor_index_2 = floor_index

    if floor_index != floor_len - 1:
        btn_swap_down = row.operator("xp_ext.fac_swap_floors", text="", icon='TRIA_DOWN')
        btn_swap_down.collection_name = collection_name
        btn_swap_down.floor_index_1 = floor_index
        btn_swap_down.floor_index_2 = floor_index + 1

    btn_rem = row.operator("xp_ext.add_rem_fac", text="", icon='X')
    btn_rem.collection_name = collection_name
    btn_rem.floor_index = floor_index
    btn_rem.level = "floor"
    btn_rem.add = False

    if floor.is_ui_expanded:
        box.label(text=f"Floor")
        box.prop(floor, "name", text="Name")
        box.prop_search(floor, "roof_collection", col.xp_fac, "spelling_choices", text="Roof Collection")
        box.separator()
        box.label(text="Wall Rules:")

        for i, wall in enumerate(floor.walls):
            draw_fac_wall(box, wall, collection_name, floor_index, i, len(floor.walls))

        box.separator()

        row = box.row()

        btn_add = row.operator("xp_ext.add_rem_fac", text="Add Wall", icon='ADD')
        btn_add.collection_name = collection_name
        btn_add.floor_index = floor_index
        btn_add.wall_index = len(floor.walls)
        btn_add.level = "wall"
        btn_add.add = True

        btn_duplicate = row.operator("xp_ext.fac_duplicate_floor", text="Duplicate Floor", icon='DUPLICATE')
        btn_duplicate.collection_name = collection_name
        btn_duplicate.floor_index = floor_index

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
                            row = box.row()
                            row.prop(col.xp_lin, "layer_group")
                            row.prop(col.xp_lin, "layer_group_offset")

class MENU_lin_layer(bpy.types.Panel):
    bl_label = "X-Plane Line Layer"
    bl_idname = "OBJECT_PT_lin_layer"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # Only show the panel if the active object is a MESH
        result = context.object and context.object.type == 'MESH'

        #Get our prefs for whether we hide this in non-agp collections
        addon_prefs = bpy.context.preferences.addons["io_scene_xplane_ext"].preferences

        #Get the parent collection
        if result:
            #Check if the parent collection has the xp_fac property
            parent_collection = context.object.users_collection[0] if context.object.users_collection else None
            if parent_collection and addon_prefs.show_only_relevant_settings:
                result = result and parent_collection.xp_lin.exportable

        # Only show the panel if the active object is a MESH
        return result

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        #Draw the exportable checkbox
        layout.prop(obj.xp_lin, "exportable")

        #If it's exportable, draw the type selector
        if obj.xp_lin.exportable:
            layout.prop(obj.xp_lin, "type")

class MENU_agp_obj(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "X-Plane AGP Object"
    bl_idname = "OBJECT_PT_agp_object"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # Only show the panel if the active object is an EMPTY
        result = context.object

        #Get our prefs for whether we hide this in non-agp collections
        addon_prefs = bpy.context.preferences.addons["io_scene_xplane_ext"].preferences

        #Get the parent collection
        if result:
            #Check if the parent collection has the xp_fac property
            parent_collection = context.object.users_collection[0] if context.object.users_collection else None
            if parent_collection and addon_prefs.show_only_relevant_settings:
                result = result and parent_collection.xp_agp.exportable

        # Only show the panel if the active object is an EMPTY
        return result and (context.object.type == 'EMPTY' or context.object.type == 'MESH')

    def draw(self, context):

        layout = self.layout

        agp_obj = context.object.xp_agp

        layout.prop(agp_obj, "exportable")
        if agp_obj.exportable:
            layout.prop(agp_obj, "type")
            
            if agp_obj.type == "ATTACHED_OBJ":
                layout.separator()
                layout.prop(agp_obj, "attached_obj_resource")
                layout.prop(agp_obj, "attached_obj_draped")
            elif agp_obj.type == "AUTO_SPLIT_OBJ":
                layout.separator()
                layout.label(text="DISCLAIMER:")
                layout.label(text="More Materials = more .objs = more draw calls = worse performance.")
                layout.label(text="Use at your own risk!")
                layout.separator()
                layout.prop(agp_obj, "autosplit_obj_name")
                layout.separator()
                layout.prop(agp_obj, "autosplit_do_fake_lods")
                if agp_obj.autosplit_do_fake_lods:
                    layout.prop(agp_obj, "autosplit_fake_lods_size")
                layout.separator()
                layout.prop(agp_obj, "autosplit_lod_count")
                if  agp_obj.autosplit_lod_count > 0:
                    row = layout.row()
                    row.prop(agp_obj, "autosplit_lod_1_min")
                    row.prop(agp_obj, "autosplit_lod_1_max")
                if agp_obj.autosplit_lod_count > 1:
                    row = layout.row()
                    row.prop(agp_obj, "autosplit_lod_2_min")
                    row.prop(agp_obj, "autosplit_lod_2_max")
                if agp_obj.autosplit_lod_count > 2:
                    row = layout.row()
                    row.prop(agp_obj, "autosplit_lod_3_min")
                    row.prop(agp_obj, "autosplit_lod_3_max")
                if agp_obj.autosplit_lod_count > 3:
                    row = layout.row()
                    row.prop(agp_obj, "autosplit_lod_4_min")
                    row.prop(agp_obj, "autosplit_lod_4_max")
            elif agp_obj.type == "FACADE":
                layout.separator()
                layout.prop(agp_obj, "facade_resource")
                layout.prop(agp_obj, "facade_height")
            elif agp_obj.type == "TREE":
                layout.separator()
                layout.prop(agp_obj, "tree_layer")
            elif agp_obj.type == "TREE_LINE":
                layout.separator()
                layout.prop(agp_obj, "tree_layer")

class MENU_agp_exporter(bpy.types.Panel):
    bl_label = "X-Plane AGP Exporter"
    bl_idname = "SCENE_PT_agp_exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #Export button
        layout.operator("xp_ext.export_agps", text="Export AGPs")
        layout.separator()

        layout.prop(scene.xp_ext, "agp_collection_search")

        if scene.xp_ext.agp_collection_search != "":
            layout.label(text="Filtered Collections")

        # Function to draw all the properties for the collection. Just so we can reuse it for the disabled collections
        def draw_collection(col, in_layout):
            agp = col.xp_agp

            box = in_layout.box()
            top_row = box.row()
            top_row.prop(agp, "is_ui_expanded", text=col.name, icon='TRIA_DOWN' if agp.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
            top_row.prop(agp, "exportable", text="Export Enabled")
            if agp.is_ui_expanded:
                box.prop(agp, "name")
                
                box.separator()

                box.prop(agp, "render_tiles")
                box.prop(agp, "tile_lod")

                box.separator()

                box.prop(agp, "vegetation_asset")

                box.separator()
                box.prop(agp, "is_texture_tiling")
                
                if agp.is_texture_tiling:
                    row = box.row()
                    row.prop(agp, "texture_tiling_x_pages")
                    row.prop(agp, "texture_tiling_y_pages")
                    row = box.row()
                    row.prop(agp, "texture_tiling_map_x_res")
                    row.prop(agp, "texture_tiling_map_y_res")
                    box.prop(agp, "texture_tiling_map_texture")

        # Draw enabled collections
        for col in bpy.data.collections:
            if col.xp_agp.exportable:
                if scene.xp_ext.agp_collection_search != "" and not (col.name.startswith(scene.xp_ext.agp_collection_search) or col.name.endswith(scene.xp_ext.agp_collection_search)):
                    continue
                draw_collection(col, layout)

        # Draw disabled collections
        disabled_collections = layout.box()
        disabled_collections.prop(scene.xp_ext, "agp_disabled_collections_expanded", text="Disabled Collections", icon='TRIA_DOWN' if scene.xp_ext.agp_disabled_collections_expanded else 'TRIA_RIGHT', emboss=False)
        if scene.xp_ext.agp_disabled_collections_expanded:
            for col in bpy.data.collections:
                if not col.xp_agp.exportable:
                    if scene.xp_ext.agp_collection_search != "" and not (col.name.startswith(scene.xp_ext.agp_collection_search) or col.name.endswith(scene.xp_ext.agp_collection_search)):
                        continue
                    draw_collection(col, disabled_collections)

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
            layout.operator("xp_ext.update_material_nodes", text="Update Material")

            #---------------------------------Texture Properties---------------------------------

            box = layout.box()

            box.label(text="Textures")
            box.prop(xp_materials, "do_separate_material_texture")

            box.prop(xp_materials, "alb_texture", text="Albedo Texture")

            if xp_materials.draped:
                row = box.row()            
                row.prop(xp_materials, "normal_texture", text="Normal Texture")
                row.prop(xp_materials, "normal_tile_ratio")
            else:
                box.prop(xp_materials, "normal_texture", text="Normal Texture")

            if xp_materials.do_separate_material_texture:
                box.prop(xp_materials, "material_texture", text="Material Texture")

            box.prop(xp_materials, "lit_texture", text="Lit Texture")
            if (xp_materials.lit_texture != ""):
                box.prop(xp_materials, "brightness", text="Brightness")

            box.prop(xp_materials, "weather_texture", text="Weather Texture")

            #---------------------------------Surface Properties---------------------------------

            box = layout.box()
            box.label(text="Surface Properties")

            box.prop(xp_materials, "blend_mode")
            if xp_materials.blend_mode == "CLIP":
                box.prop(xp_materials, "blend_cutoff")
            elif xp_materials.blend_mode == "SHADOW":
                box.prop(xp_materials, "blend_cutoff", text="Shadow Cutoff")

            box.separator()

            row = box.row()
            row.prop(xp_materials, "layer_group")
            row.prop(xp_materials, "layer_group_offset")

            box.separator()

            box.prop(xp_materials, "cast_shadow")
            box.prop(xp_materials, "draped")
            box.prop(xp_materials, "polygon_offset")
            
            box.separator()

            box.prop(xp_materials, "surface_type")
            box.prop(xp_materials, "surface_is_deck")
            

            box = layout.box()

            box.label(text="Lighting Properties")
            box.prop(xp_materials, "light_level_override")
            if xp_materials.light_level_override:
                box.prop(xp_materials, "light_level_v1")
                box.prop(xp_materials, "light_level_v2")
                box.prop(xp_materials, "light_level_photometric")
                if xp_materials.light_level_photometric:
                    box.prop(xp_materials, "light_level_brightness")
                box.prop(xp_materials, "light_level_dataref")

            #---------------------------------Decal Properties---------------------------------

            box = layout.box()

            box.label(text="Decals:")

            box.prop(xp_materials, "decal_modulator")
            box.separator()

            if len(xp_materials.decals) == 0:
                box.label(text="Change any XP Material setting to trigger an update to add the decals slots")
            
            for i, decal in enumerate(xp_materials.decals):
                draw_decal_prop(box, decal, i, material.name)

            box = layout.box()

            #---------------------------------Aircraft Properties---------------------------------

            box.label(text="Aircraft Properties")

            box.prop(xp_materials, "camera_collision_enabled")
            box.prop(xp_materials, "drawing_enabled")

            box.separator()

            box.prop(xp_materials, "use_2d_panel_texture")
            if xp_materials.use_2d_panel_texture:
                box.prop(xp_materials, "panel_texture_region")

            box.separator()
            box.prop(xp_materials, "cockpit_device")
            if xp_materials.cockpit_device != "NONE":
                if xp_materials.cockpit_device == "Plugin Device":
                    box.prop(xp_materials, "custom_cockpit_device")
                row = box.row()

                row.prop(xp_materials, "cockpit_device_use_bus_1")
                row.prop(xp_materials, "cockpit_device_use_bus_2")
                row.prop(xp_materials, "cockpit_device_use_bus_3")

                row = box.row()

                row.prop(xp_materials, "cockpit_device_use_bus_4")
                row.prop(xp_materials, "cockpit_device_use_bus_5")
                row.prop(xp_materials, "cockpit_device_use_bus_6")

                box.prop(xp_materials, "cockpit_device_lighting_channel")

            #---------------------------------Conversion Operators---------------------------------
            layout.separator()
            layout.label(text="Conversion Operators")
            separate_op = layout.operator("xp_ext.convert_combined_xp_nml_to_separate", text="Separate combined normal map")
            separate_op.material_name = material.name
            combine_op = layout.operator("xp_ext.convert_separate_maps_to_combined_xp_nml", text="Combine separated material maps")
            combine_op.material_name = material.name

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
        layout.label(text="X-Plane Exporter Sync")
        layout.operator("xp_ext.update_collection_textures", text="Update X-Plane Export Texture Settings")

        layout.operator("xp_ext.update_all_material_nodes", text="Update All Materials")

        layout.operator("xp_ext.find_textures", text="Find Missing Textures")

        layout.separator()

        box = layout.box()
        box.prop(xp_ext, "menu_export_path_expanded", text="Export Path", icon='TRIA_DOWN' if xp_ext.menu_export_path_expanded else 'TRIA_RIGHT', emboss=False)
        if xp_ext.menu_export_path_expanded:
            box.prop(xp_ext, "export_path")
            box.operator("xp_ext.set_export_paths", text="Set All Export Paths")

        layout.separator()
        
        box = layout.box()
        box.prop(xp_ext, "menu_bake_expanded", text="High Poly to Low Poly Bake", icon='TRIA_DOWN' if xp_ext.menu_bake_expanded else 'TRIA_RIGHT', emboss=False)
        if xp_ext.menu_bake_expanded:
            box.prop(xp_ext, "low_poly_bake_do_alb")
            box.prop(xp_ext, "low_poly_bake_do_opacity")
            box.prop(xp_ext, "low_poly_bake_do_nrm")
            if xp_ext.low_poly_bake_do_separate_normals:
                box.prop(xp_ext, "low_poly_bake_do_mat")
            box.prop(xp_ext, "low_poly_bake_do_lit")
            box.separator()
            box.prop(xp_ext, "low_poly_bake_resolution")
            box.prop(xp_ext, "low_poly_bake_ss_factor")
            box.prop(xp_ext, "low_poly_bake_margin")
            box.separator()
            box.prop(xp_ext, "low_poly_bake_extrusion_distance")
            box.prop(xp_ext, "low_poly_bake_max_ray_distance")
            box.separator()
            box.prop(xp_ext, "low_poly_bake_do_separate_normals")
            box.operator("xp_ext.bake_low_poly", text="Bake Selected Objects to Active")

        layout.separator()

        box = layout.box()
        box.prop(xp_ext, "menu_autoanim_expanded", text="Auto Animation", icon='TRIA_DOWN' if xp_ext.menu_autoanim_expanded else 'TRIA_RIGHT', emboss=False)
        if xp_ext.menu_autoanim_expanded:
            box.prop(xp_ext, "autoanim_autodetect")
            box.separator()
            if not xp_ext.autoanim_autodetect:
                row = box.row()
                row.prop(xp_ext, "autoanim_frame_start")
                row.prop(xp_ext, "autoanim_frame_end")
                box.prop(xp_ext, "autoanim_keyframe_interval")
                box.separator()
                box.prop(xp_ext, "autoanim_dataref")
                
                row = box.row()
                row.prop(xp_ext, "autoanim_start_value")
                row.prop(xp_ext, "autoanim_end_value")
                box.prop(xp_ext, "autoanim_loop_value")
            else:
                box.prop(xp_ext, "autoanim_autodetect_fps")
                box.prop(xp_ext, "autoanim_keyframe_interval")
                box.separator()
                box.prop(xp_ext, "autoanim_dataref")
            box.separator()
            box.prop(xp_ext, "autoanim_apply_parent_transform")
            box.prop(xp_ext, "autoanim_add_intermediate_keyframes")
            box.separator()
            box.operator("xp_ext.generate_flipbook_animation")
            box.operator("xp_ext.auto_keyframe_animation")

        layout.separator()

        box = layout.box()
        box.prop(xp_ext, "menu_lod_preview_expanded", text="Level of Detail (LOD) Preview", icon='TRIA_DOWN' if xp_ext.menu_lod_preview_expanded else 'TRIA_RIGHT', emboss=False)
        if xp_ext.menu_lod_preview_expanded:
            box.prop(xp_ext, "lod_distance_preview")
            box.operator("xp_ext.preview_lods_for_distance", text="Preview LODs for Distance")

        do_test_operators = False
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
                    draw_fac_floor(spelling_box, floor, col.name, i, len(fac.floors))
                
                btn_add = spelling_box.operator("xp_ext.add_rem_fac", text="Add Floor", icon='ADD')
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
    bl_label = "X-Plane Facade Attached Object"
    bl_idname = "OBJECT_PT_attached_object"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # Only show the panel if the active object is an EMPTY
        result = context.object and context.object.type == 'EMPTY'

        #Get our prefs for whether we hide this in none-facade collections
        addon_prefs = bpy.context.preferences.addons["io_scene_xplane_ext"].preferences

        if result:
            
            #Check if there are any facades enabled in the scene
            if addon_prefs.show_only_relevant_settings:
                result = False

                for col in bpy.data.collections:
                    if col.xp_fac.exportable:
                        result = True
                        
        return result

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
        result = context.object and context.object.type == 'MESH'

        #Get our prefs for whether we hide this in none-facade collections
        addon_prefs = bpy.context.preferences.addons["io_scene_xplane_ext"].preferences

        if result:
            #Check if there are any facades enabled in the scene
            if addon_prefs.show_only_relevant_settings:
                result = False
                for col in bpy.data.collections:
                    if col.xp_fac.exportable:
                        result = True

        return result

    def draw(self, context):

        layout = self.layout

        fac_mesh = context.object.xp_fac_mesh

        #If this is a mesh, we show the mesh options of cut, and exportable
        if context.object.type == 'MESH':
            layout.prop(fac_mesh, "far_lod")
            layout.prop(fac_mesh, "group")
            layout.prop(fac_mesh, "cuts")
            layout.prop(fac_mesh, "exportable")

class MENU_pol_exporter(bpy.types.Panel):
    bl_label = "X-Plane Polygon Exporter"
    bl_idname = "SCENE_PT_pol_exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #Export button
        layout.operator("xp_ext.export_polygons", text="Export Polygons")
        layout.separator()

        layout.prop(scene.xp_ext, "pol_collection_search")

        if scene.xp_ext.pol_collection_search != "":
            layout.label(text="Filtered Collections")

        # Function to draw all the properties for the collection. Just so we can reuse it for the disabled collections
        def draw_collection(col, in_layout):
            pol = col.xp_pol

            box = in_layout.box()
            top_row = box.row()
            top_row.prop(col.xp_pol, "is_ui_expanded", text=col.name, icon='TRIA_DOWN' if col.xp_pol.is_ui_expanded else 'TRIA_RIGHT', emboss=False)
            top_row.prop(col.xp_pol, "exportable", text="Export Enabled")
            if col.xp_pol.is_ui_expanded:
                box.prop(pol, "name")
                box.prop(pol, "texture_is_nowrap")
                box.separator()
                box.prop(pol, "is_load_centered")

                if pol.is_load_centered:
                    row = box.row()
                    row.prop(pol, "load_center_lat")
                    row.prop(pol, "load_center_lon")
                    box.prop(pol, "load_center_resolution")
                    box.prop(pol, "load_center_size")

                box.separator()
                box.prop(pol, "is_texture_tiling")
                
                if pol.is_texture_tiling:
                    row = box.row()
                    row.prop(pol, "texture_tiling_x_pages")
                    row.prop(pol, "texture_tiling_y_pages")
                    row = box.row()
                    row.prop(pol, "texture_tiling_map_x_res")
                    row.prop(pol, "texture_tiling_map_y_res")
                    box.prop(pol, "texture_tiling_map_texture")

                box.separator()
                box.prop(pol, "is_runway_markings")

                if pol.is_runway_markings:
                    row = box.row()
                    row.prop(pol, "runway_markings_r")
                    row.prop(pol, "runway_markings_g")
                    row.prop(pol, "runway_markings_b")
                    row.prop(pol, "runway_markings_a")
                    box.prop(pol, "runway_markings_texture")

        # Draw enabled collections
        for col in bpy.data.collections:
            if col.xp_pol.exportable:
                if scene.xp_ext.pol_collection_search != "" and not (col.name.startswith(scene.xp_ext.pol_collection_search) or col.name.endswith(scene.xp_ext.pol_collection_search)):
                    continue
                draw_collection(col, layout)

        # Draw disabled collections
        disabled_collections = layout.box()
        disabled_collections.prop(scene.xp_ext, "pol_disabled_collections_expanded", text="Disabled Collections", icon='TRIA_DOWN' if scene.xp_ext.pol_disabled_collections_expanded else 'TRIA_RIGHT', emboss=False)
        if scene.xp_ext.pol_disabled_collections_expanded:
            for col in bpy.data.collections:
                if not col.xp_pol.exportable:
                    if scene.xp_ext.pol_collection_search != "" and not (col.name.startswith(scene.xp_ext.pol_collection_search) or col.name.endswith(scene.xp_ext.pol_collection_search)):
                        continue
                    draw_collection(col, disabled_collections)

def register():
    bpy.utils.register_class(MENU_lin_exporter)
    bpy.utils.register_class(MENU_lin_layer)
    bpy.utils.register_class(MENU_agp_exporter)
    bpy.utils.register_class(MENU_mats)
    bpy.utils.register_class(MENU_operations)
    bpy.utils.register_class(MENU_facade)
    bpy.utils.register_class(MENU_attached_object)
    bpy.utils.register_class(MENU_fac_mesh)
    bpy.utils.register_class(MENU_pol_exporter)
    bpy.utils.register_class(MENU_agp_obj)

def unregister():
    bpy.utils.unregister_class(MENU_lin_exporter)
    bpy.utils.unregister_class(MENU_lin_layer)
    bpy.utils.unregister_class(MENU_agp_exporter)
    bpy.utils.unregister_class(MENU_mats)
    bpy.utils.unregister_class(MENU_operations)
    bpy.utils.unregister_class(MENU_facade)
    bpy.utils.unregister_class(MENU_attached_object)
    bpy.utils.unregister_class(MENU_fac_mesh)
    bpy.utils.unregister_class(MENU_pol_exporter)
    bpy.utils.unregister_class(MENU_agp_obj)