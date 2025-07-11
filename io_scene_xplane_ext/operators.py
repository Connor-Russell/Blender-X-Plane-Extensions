#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Operators
#Purpose:   Provide a single file containing all operators for the X-Plane Line Exporter

import bpy  # type: ignore
from bpy_extras.io_utils import ImportHelper # type: ignore

from . import exporter
from . import importer
from . import material_config
from .Helpers import file_utils
from .Helpers import collection_utils
from .Helpers import decal_utils
from .Helpers import misc_utils
from .Helpers import log_utils
from .Helpers import facade_utils
from . import anim_actions
from . import auto_baker
import os

class BTN_lin_exporter(bpy.types.Operator):
    bl_idname = "xp_ext.export_lines"
    bl_label = "Export X-Plane Lines"
    bl_description = "Export X-Plane lines from the visible collections."

    def execute(self, context):

        #Iterate through every collection. If it is exportable, and visible, export
        for col in bpy.data.collections:
            if col.xp_lin.exportable and collection_utils.get_collection_is_visible(col):
                exporter.export_lin(col)

        return {'FINISHED'}
    
class BTN_pol_exporter(bpy.types.Operator):
    bl_idname = "xp_ext.export_polygons"
    bl_label = "Export X-Plane Polygons"
    bl_description = "Export X-Plane polygons from the visible collections."

    def execute(self, context):

        # Iterate through every collection. If it is exportable and visible, export
        for col in bpy.data.collections:
            if col.xp_pol.exportable and collection_utils.get_collection_is_visible(col):
                exporter.export_pol(col)

        return {'FINISHED'}
    
class BTN_agp_exporter(bpy.types.Operator):
    bl_idname = "xp_ext.export_agps"
    bl_label = "Export X-Plane Autogen Points"
    bl_description = "Export X-Plane autogen points from the visible collections."

    def execute(self, context):

        # Iterate through every collection. If it is exportable and visible, export
        for col in bpy.data.collections:
            if col.xp_agp.exportable and collection_utils.get_collection_is_visible(col):
                exporter.export_agp(col)

        return {'FINISHED'}  

class IMPORT_lin(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xp_lin"
    bl_label = "Import X-Plane Lines"
    filename_ext = ".lin"
    filter_glob: bpy.props.StringProperty(default="*.lin", options={'HIDDEN'}) # type: ignore
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)  # type: ignore To support multiple files

    def execute(self, context):
        # Implement your import logic here
        directory = self.filepath
        directory = directory[:directory.rfind(os.sep)]

        for cf in self.files:
            filepath = f"{directory}{os.sep}{cf.name}"
            importer.import_lin(filepath)

        return {'FINISHED'}

class IMPORT_pol(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xp_pol"
    bl_label = "Import X-Plane Polygons"
    filename_ext = ".pol"
    filter_glob: bpy.props.StringProperty(default="*.pol", options={'HIDDEN'}) # type: ignore
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)  # type: ignore To support multiple files

    def execute(self, context):
        # Implement your import logic here
        directory = self.filepath
        directory = directory[:directory.rfind(os.sep)]

        for cf in self.files:
            filepath = f"{directory}{os.sep}{cf.name}"
            importer.import_pol(filepath)

        return {'FINISHED'}

class IMPORT_fac(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xp_fac"
    bl_label = "Import X-Plane Facade"
    filename_ext = ".fac"
    filter_glob: bpy.props.StringProperty(default="*.fac", options={'HIDDEN'}) # type: ignore
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)  # type: ignore To support multiple files

    def execute(self, context):
        # Implement your import logic here
        directory = self.filepath
        directory = directory[:directory.rfind(os.sep)]

        for cf in self.files:
            filepath = f"{directory}{os.sep}{cf.name}"
            importer.import_fac(filepath)

        return {'FINISHED'}
    
class IMPORT_obj(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xp_obj"
    bl_label = "Import X-Plane Object"
    filename_ext = ".fac"
    filter_glob: bpy.props.StringProperty(default="*.obj", options={'HIDDEN'}) # type: ignore
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)  # type: ignore To support multiple files

    def execute(self, context):
        # Implement your import logic here
        directory = self.filepath
        directory = directory[:directory.rfind(os.sep)]

        for cf in self.files:
            filepath = f"{directory}{os.sep}{cf.name}"
            importer.import_obj(filepath)

        return {'FINISHED'}

class IMPORT_agp(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xp_agp"
    bl_label = "Import X-Plane Autogen Points"
    filename_ext = ".agp"
    filter_glob: bpy.props.StringProperty(default="*.agp", options={'HIDDEN'}) # type: ignore
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)  # type: ignore To support multiple files

    def execute(self, context):
        # Implement your import logic here
        directory = self.filepath
        directory = directory[:directory.rfind(os.sep)]

        for cf in self.files:
            filepath = f"{directory}{os.sep}{cf.name}"
            importer.import_agp(filepath)

        return {'FINISHED'}

class TEST_IMPORT_obj(bpy.types.Operator):
    bl_idname = "xp_ext.test_import_obj"
    bl_label = "Test Import X-Plane Lines"
    bl_description = "Test the import of X-Plane lines. This is a development tool and should not be used in production."
    import_path: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        importer.import_obj(self.import_path)

        return {'FINISHED'}
    
class TEST_import_lin(bpy.types.Operator):
    bl_idname = "xp_ext.test_import_lin"
    bl_label = "Test Import X-Plane Lines"
    bl_description = "Test the import of X-Plane lines. This is a development tool and should not be used in production."
    import_path: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        importer.import_lin(self.import_path)

        return {'FINISHED'}
    
class TEST_import_pol(bpy.types.Operator):
    bl_idname = "xp_ext.test_import_pol"
    bl_label = "Test Import X-Plane Polygons"
    bl_description = "Test the import of X-Plane polygons. This is a development tool and should not be used in production."
    import_path: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        importer.import_pol(self.import_path)

        return {'FINISHED'}
    
class TEST_import_fac(bpy.types.Operator):
    bl_idname = "xp_ext.test_import_fac"
    bl_label = "Test Import X-Plane Facade"
    bl_description = "Test the import of X-Plane facades. This is a development tool and should not be used in production."
    import_path: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        importer.import_fac(self.import_path)

        return {'FINISHED'}

class BTN_mats_autoodetect_textures(bpy.types.Operator):
    """Autodetects the texture"""
    bl_idname = "xp_ext.autodetect_texture"
    bl_label = "Autodetect Texture"
    bl_description = "Autodetects the textures for the material based on the <name>.png <name>_NML.png and <name>_LIT.png naming scheme. If the albedo texture is set, it is used as <name>, otherwise the material name is used as <name>"

    def execute(self, context):
        #Get the material
        material = context.material

        #Get the name
        name = material.name

        #Get our prefs for suffixes
        addon_prefs = bpy.context.preferences.addons["io_scene_xplane_ext"].preferences

        #If the material has an albedo texture, use that as our name
        if material.xp_materials.alb_texture != "":
            name = material.xp_materials.alb_texture

        #Remove the extension from the name
        name = name.replace(".png", "")
        name = name.replace(".dds", "")
        
        alb_check_path = file_utils.rel_to_abs(name + addon_prefs.suffix_albedo + ".png")
        
        #Define the paths for the NML, and LIT
        nml_check_path = file_utils.rel_to_abs(name + addon_prefs.suffix_combined_normal + ".png")
        lit_check_path = file_utils.rel_to_abs(name + addon_prefs.suffix_lit + ".png")
        mat_check_path = ""

        if material.xp_materials.do_separate_material_texture:
            nml_check_path = file_utils.rel_to_abs(name + addon_prefs.suffix_normal + ".png")
            mat_check_path = file_utils.rel_to_abs(name + addon_prefs.suffix_material + ".png")

        #Set properties if the paths exist
        material.xp_materials.alb_texture = file_utils.abs_to_rel(file_utils.check_for_dds_or_png(alb_check_path))
        material.xp_materials.normal_texture = file_utils.abs_to_rel(file_utils.check_for_dds_or_png(nml_check_path))
        material.xp_materials.lit_texture = file_utils.abs_to_rel(file_utils.check_for_dds_or_png(lit_check_path))
        material.xp_materials.material_texture = file_utils.abs_to_rel(file_utils.check_for_dds_or_png(mat_check_path))


        #Return success
        return {'FINISHED'}

class BTN_mats_update_nodes(bpy.types.Operator):
    bl_idname = "xp_ext.update_material_nodes"
    bl_label = "Updates material nodes"
    bl_description = "Updates the material nodes to match the current settings, so the material visually matches your X-Plane material settings. Also reloads images."
    bl_options = {'REGISTER', 'UNDO'}  # Add 'REGISTER' here

    def execute(self, context):

        #Call the function to update the settings. Currently these functions just take None as argument, they get the material from context because when they are called from an update param, they can't get the appropraite args anyway. 
        #In the future we will wrap them for the update call so we can pass the material as an argument here and override materials, but that is a job for another day
        material_config.operator_wrapped_update_settings(None)

        material_config.operator_wrapped_update_nodes(None)

        return {'FINISHED'}

class BTN_mats_update_all_mat_nodes(bpy.types.Operator):
    """Updates all materials in the scene to match the current settings"""
    bl_idname = "xp_ext.update_all_material_nodes"
    bl_label = "Update All Materials"
    bl_description = "Updates all materials in the scene to match the current settings. This is a slow operation and should only be used when necessary. It will also reload all images."
    bl_options = {'REGISTER', 'UNDO'}  # Add 'REGISTER' here

    def execute(self, context):
        #Get all the materials
        for mat in bpy.data.materials:
            if mat.xp_materials.alb_texture != "":
                material_config.update_settings(mat)
                material_config.update_nodes(mat)

        return {'FINISHED'}

class BTN_generate_flipbook_animation(bpy.types.Operator):
    """Generates a flipbook animation for the selected object"""
    bl_idname = "xp_ext.generate_flipbook_animation"
    bl_label = "Generate Flipbook Animation"
    bl_description = "Generates a flipbook animation for the selected object. The object must have a dataref set, and the dataref must be a flipbook dataref. The animation will be created in the same collection as the object."

    def execute(self, context):
        #Get our params
        start_frame = bpy.context.scene.xp_ext.flipbook_frame_start
        end_frame = bpy.context.scene.xp_ext.flipbook_frame_end
        keyframe_interval = bpy.context.scene.xp_ext.flipbook_keyframe_interval
        dataref = bpy.context.scene.xp_ext.flipbook_dataref
        loop_value = bpy.context.scene.xp_ext.flipbook_loop_value
        start_value = bpy.context.scene.xp_ext.flipbook_start_value
        end_value = bpy.context.scene.xp_ext.flipbook_end_value

        #Iterate over selected objects
        for obj in bpy.context.selected_objects:
            anim_actions.create_flipbook_animation(obj, dataref, start_value, end_value, loop_value, start_frame, end_frame, keyframe_interval)

        return {'FINISHED'}

class BTN_update_xp_export_settings(bpy.types.Operator):
    """Operator to update all the collections texture settings to the current material settings"""
    bl_idname = "xp_ext.update_collection_textures"
    bl_label = "Update Collection Textures"
    bl_description = "Updates the X-Plane collection export material settings to match that of the first object in the collection. This applies to all collections that are exportable X-Plane objects."

    def execute(self, context):
        #For each collection:
        # get all the objects in that collection
        # for each object, get the material
        # IF that material has textures set, update that collection, set flag that that collection has been updated. Keep looping through the object, if we find one that is draped, update with that material
        for col in bpy.context.scene.collection.children:
            material_config.update_xplane_collection_settings(col)

        return {'FINISHED'}

class BTN_bake_low_poly(bpy.types.Operator):
    """Automatically bakes selected objects to active objects for base, normal, roughness, metalness, and lit, then saves into XP formats in the same folder as the .blend"""
    bl_idname = "xp_ext.bake_low_poly"
    bl_label = "Bake to Low Poly"
    bl_description = "Automatically bakes the selected objects to the active object. Handles base, normal, and lit textures in the X-Plane format, and saves them as <collection_name>_LOD01_<suffix>.png in the Blender folder. Be sure to set extrusion distance and max ray distance in the Blender bake settings"

    def execute(self, context):

        #For all the sleected objects, if it isn't a mesh, deselect it
        for obj in bpy.context.selected_objects:
            if obj.type != 'MESH':
                obj.select_set(False)
                print("Deselected non-mesh object " + obj.name)

        #Some initial checks: We are saved. Every selected object has a material. Check each individually, give appropriate error messages
        if not bpy.data.filepath:
            self.report({'ERROR'}, "You must save your file before baking")
            return {'CANCELLED'}
        
        for obj in bpy.context.selected_objects:
            if not obj.data.materials:
                self.report({'ERROR'}, "All selected objects must have a material")
                return {'CANCELLED'}


        #Bake the object to low poly
        auto_baker.auto_bake_current_to_active()

        return {'FINISHED'}

class MENU_BT_fac_add_or_rem_in_fac(bpy.types.Operator):
    bl_idname = "xp_ext.add_rem_fac"
    bl_label = "Spelling Operation"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty() # type: ignore
    floor_index: bpy.props.IntProperty() # type: ignore
    wall_index: bpy.props.IntProperty() # type: ignore
    spelling_index: bpy.props.IntProperty() # type: ignore
    spelling_entry_index: bpy.props.IntProperty() # type: ignore
    level: bpy.props.StringProperty() # type: ignore    spelling, wall, or floor
    add: bpy.props.BoolProperty() # type: ignore . True to add a new item after the target, false to remove the target
    duplicate: bpy.props.BoolProperty() # type: ignore . True to duplicate the target when adding. Can only be done for spellings

    def execute(self, context):
        #Get the collection
        col = None
        for search_col in bpy.data.collections:
            if search_col.name == self.collection_name:
                col = search_col
        
        if col is None:
            self.report({'ERROR'}, "Collection not found")
            return {'CANCELLED'}

        #Add a new floor if desired        
        if self.level == "floor" and self.add:
            new_floor = col.xp_fac.floors.add()
            new_floor.name = "New Floor"
            return {'FINISHED'}

        #Get the floor to remove it
        floor = col.xp_fac.floors[self.floor_index]
        if floor is None:
            self.report({'ERROR'}, "Floor not found")
            return {'CANCELLED'}
        
        if self.level == "floor" and not self.add:
            col.xp_fac.floors.remove(self.floor_index)
            return {'FINISHED'}
        
        #Add a new wall if desired
        if self.level == "wall" and self.add:
            new_wall = floor.walls.add()
            new_wall.name = "New Wall"
            return {'FINISHED'}
        
        #Get the wall
        wall = floor.walls[self.wall_index]

        if wall is None:
            self.report({'ERROR'}, "Wall not found")
            return {'CANCELLED'}

        if self.level == "wall" and not self.add:
            floor.walls.remove(self.wall_index)
            return {'FINISHED'}
        
        #Add a new spelling if desired
        if self.level == "spelling" and self.add:
            if not self.duplicate:
                new_spelling = wall.spellings.add()
                new_spelling.name = "New Spelling"
                new_spelling.entries.add()  #Add the first spelling entry
                return {'FINISHED'}
            else:
                #If we are duplicating, we need to get the spelling, and duplicate it
                spelling = wall.spellings[self.spelling_index]
                if spelling is None:
                    self.report({'ERROR'}, "Spelling not found")
                    return {'CANCELLED'}
                
                new_spelling = wall.spellings.add()
                new_spelling.name = "New Spelling"
                for e in spelling.entries:
                    new_entry = new_spelling.entries.add()
                    new_entry.collection = e.collection
                
                return {'FINISHED'}
        
        #Get the spelling
        spelling = wall.spellings[self.spelling_index]

        if spelling is None:
            self.report({'ERROR'}, "Spelling not found")
            return {'CANCELLED'}

        if self.level == "spelling" and not self.add:
            wall.spellings.remove(self.spelling_index)
            return {'FINISHED'}
        
        #If we are adding a new entry, do that
        if self.level == "spelling_entry" and self.add:
            new_entry = spelling.entries.add()
            new_entry.name = "New Entry"
            return {'FINISHED'}
        
        #Get the spelling entry
        spelling_entry = spelling.entries[self.spelling_entry_index]
        if spelling_entry is None:
            self.report({'ERROR'}, "Spelling entry not found")
            return {'CANCELLED'}
        
        #If we are removing an entry, do that
        if self.level == "spelling_entry" and not self.add:
            spelling.entries.remove(self.spelling_entry_index)
            #If there are 0 entries, remove the whole spelling
            if len(spelling.entries) == 0:
                wall.spellings.remove(self.spelling_index)
            return {'FINISHED'}

        return {'FINISHED'}

class MENU_BT_fac_swap_floors(bpy.types.Operator):
    bl_idname = "xp_ext.fac_swap_floors"
    bl_label = "Spelling Operation"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty() # type: ignore
    floor_index_1: bpy.props.IntProperty() # type: ignore
    floor_index_2: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        #Get the collection
        col = None
        for search_col in bpy.data.collections:
            if search_col.name == self.collection_name:
                col = search_col
        
        if col is None:
            self.report({'ERROR'}, "Collection not found")
            return {'CANCELLED'}
        
        #Get the floors
        floor_1 = col.xp_fac.floors[self.floor_index_1]
        floor_2 = col.xp_fac.floors[self.floor_index_2]

        #Load them into a temporary class, then swap them
        floor_1_temp = facade_utils.FacFloor()
        floor_2_temp = facade_utils.FacFloor()

        floor_1_temp.from_prop(floor_1)
        floor_2_temp.from_prop(floor_2)

        floor_1_temp.to_prop(floor_2)
        floor_2_temp.to_prop(floor_1)

        return {'FINISHED'}

class MENU_BT_fac_swap_walls(bpy.types.Operator):
    bl_idname = "xp_ext.fac_swap_walls"
    bl_label = "Spelling Operation"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty() # type: ignore
    floor_index: bpy.props.IntProperty() # type: ignore
    wall_index_1: bpy.props.IntProperty() # type: ignore
    wall_index_2: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        #Get the collection
        col = None
        for search_col in bpy.data.collections:
            if search_col.name == self.collection_name:
                col = search_col
        
        if col is None:
            self.report({'ERROR'}, "Collection not found")
            return {'CANCELLED'}
        
        #Get the floor
        floor = col.xp_fac.floors[self.floor_index]

        if floor is None:
            self.report({'ERROR'}, "Floor not found")
            return {'CANCELLED'}
        
        #Get the walls
        wall_1 = floor.walls[self.wall_index_1]
        wall_2 = floor.walls[self.wall_index_2]

        #Load them into a temporary class, then swap them
        wall_1_temp = facade_utils.FacWall()
        wall_2_temp = facade_utils.FacWall()

        wall_1_temp.from_prop(wall_1)
        wall_2_temp.from_prop(wall_2)

        wall_1_temp.to_prop(wall_2)
        wall_2_temp.to_prop(wall_1)

        return {'FINISHED'}

class MENU_BT_fac_swap_spellings(bpy.types.Operator):
    bl_idname = "xp_ext.fac_swap_spellings"
    bl_label = "Spelling Operation"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty() # type: ignore
    floor_index: bpy.props.IntProperty() # type: ignore
    wall_index: bpy.props.IntProperty() # type: ignore
    spelling_index_1: bpy.props.IntProperty() # type: ignore
    spelling_index_2: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        #Get the collection
        col = None
        for search_col in bpy.data.collections:
            if search_col.name == self.collection_name:
                col = search_col

        if col is None:
            self.report({'ERROR'}, "Collection not found")
            return {'CANCELLED'}

        #Get the floor
        floor = col.xp_fac.floors[self.floor_index]

        if floor is None:
            self.report({'ERROR'}, "Floor not found")
            return {'CANCELLED'}

        #Get the wall
        wall = floor.walls[self.wall_index]

        if wall is None:
            self.report({'ERROR'}, "Wall not found")
            return {'CANCELLED'}

        #Get the spellings
        spelling_1 = wall.spellings[self.spelling_index_1]
        spelling_2 = wall.spellings[self.spelling_index_2]

        #Load them into a temporary class, then swap them
        spelling_1_temp = facade_utils.FacSpelling()
        spelling_2_temp = facade_utils.FacSpelling()

        spelling_1_temp.from_prop(spelling_1)
        spelling_2_temp.from_prop(spelling_2)

        spelling_1_temp.to_prop(spelling_2)
        spelling_2_temp.to_prop(spelling_1)

        return {'FINISHED'}

class MENU_BT_fac_duplicate_floor(bpy.types.Operator):
    bl_idname = "xp_ext.fac_duplicate_floor"
    bl_label = "Duplicate Floor"
    bl_description = "Duplicates the selected floor in the facade collection"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty() # type: ignore
    floor_index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        #Get the collection
        col = None
        for search_col in bpy.data.collections:
            if search_col.name == self.collection_name:
                col = search_col
        
        if col is None:
            self.report({'ERROR'}, "Collection not found")
            return {'CANCELLED'}
        
        #Get the floor to duplicate
        floor = col.xp_fac.floors[self.floor_index]
        if floor is None:
            self.report({'ERROR'}, "Floor not found")
            return {'CANCELLED'}
        
        #Add a new floor, then we will iterate through all the floors *after* the current index, and move them *down* one.
        #This will leave the index directly after ours available for the new floor
        col.xp_fac.floors.add()  # Add a new floor at the end
        for i in range(self.floor_index + 1, len(col.xp_fac.floors) - 1):
            floor_1 = col.xp_fac.floors[i]
            floor_2 = col.xp_fac.floors[i + 1]

            floor_1_temp = facade_utils.FacFloor()
            floor_2_temp = facade_utils.FacFloor()

            floor_1_temp.from_prop(floor_1)
            floor_2_temp.from_prop(floor_2)

            floor_1_temp.to_prop(floor_2)
            floor_2_temp.to_prop(floor_1)

        #Now we can load our currently floor, and set index+1 floor to it
        floor_temp = facade_utils.FacFloor()
        floor_temp.from_prop(floor)
        floor_temp.to_prop(col.xp_fac.floors[self.floor_index + 1])

        return {'FINISHED'}
    
class MENU_BT_fac_duplicate_wall(bpy.types.Operator):
    bl_idname = "xp_ext.fac_duplicate_wall"
    bl_label = "Duplicate Wall"
    bl_description = "Duplicates the selected wall in the facade collection"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty() # type: ignore
    floor_index: bpy.props.IntProperty() # type: ignore
    wall_index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        #Get the collection
        col = None
        for search_col in bpy.data.collections:
            if search_col.name == self.collection_name:
                col = search_col

        if col is None:
            self.report({'ERROR'}, "Collection not found")
            return {'CANCELLED'}

        #Get the floor
        floor = col.xp_fac.floors[self.floor_index]

        if floor is None:
            self.report({'ERROR'}, "Floor not found")
            return {'CANCELLED'}

        #Get the wall
        wall = floor.walls[self.wall_index]

        if wall is None:
            self.report({'ERROR'}, "Wall not found")
            return {'CANCELLED'}

        #Add a new wall, then we will iterate through all the walls *after* the current index, and move them *down* one.
        #This will leave the index directly after ours available for the new wall
        floor.walls.add()  # Add a new wall at the end
        for i in range(self.wall_index + 1, len(floor.walls) - 1):
            wall_1 = floor.walls[i]
            wall_2 = floor.walls[i + 1]

            wall_1_temp = facade_utils.FacWall()
            wall_2_temp = facade_utils.FacWall()

            wall_1_temp.from_prop(wall_1)
            wall_2_temp.from_prop(wall_2)

            wall_1_temp.to_prop(wall_2)
            wall_2_temp.to_prop(wall_1)

        #Now we can load our currently wall, and set index+1 wall to it
        wall_temp = facade_utils.FacWall()
        wall_temp.from_prop(wall)
        wall_temp.to_prop(floor.walls[self.wall_index + 1])

        return {'FINISHED'}

class MENU_BT_fac_duplicate_spelling(bpy.types.Operator):
    bl_idname = "xp_ext.fac_duplicate_spelling"
    bl_label = "Duplicate Spelling"
    bl_description = "Duplicates the selected spelling in the facade collection"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty() # type: ignore
    floor_index: bpy.props.IntProperty() # type: ignore
    wall_index: bpy.props.IntProperty() # type: ignore
    spelling_index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        #Get the collection
        col = None
        for search_col in bpy.data.collections:
            if search_col.name == self.collection_name:
                col = search_col

        if col is None:
            self.report({'ERROR'}, "Collection not found")
            return {'CANCELLED'}

        #Get the floor
        floor = col.xp_fac.floors[self.floor_index]

        if floor is None:
            self.report({'ERROR'}, "Floor not found")
            return {'CANCELLED'}

        #Get the wall
        wall = floor.walls[self.wall_index]

        if wall is None:
            self.report({'ERROR'}, "Wall not found")
            return {'CANCELLED'}

        #Add a new spelling, then we will iterate through all the spellings *after* the current index, and move them *down* one.
        #This will leave the index directly after ours available for the new spelling
        wall.spellings.add()  # Add a new spelling at the end
        for i in range(self.spelling_index + 1, len(wall.spellings) - 1):
            spelling_1 = wall.spellings[i]
            spelling_2 = wall.spellings[i + 1]

            spelling_1_temp = facade_utils.FacSpelling()
            spelling_2_temp = facade_utils.FacSpelling()

            spelling_1_temp.from_prop(spelling_1)
            spelling_2_temp.from_prop(spelling_2)

            spelling_1_temp.to_prop(spelling_2)
            spelling_2_temp.to_prop(spelling_1)

        #Now we can load our currently spelling, and set index+1 spelling to it
        spelling_temp = facade_utils.FacSpelling()
        spelling_temp.from_prop(wall.spellings[self.spelling_index])
        spelling_temp.to_prop(wall.spellings[self.spelling_index + 1])

        return {'FINISHED'}

class BTN_fac_export_all(bpy.types.Operator):
    """Export all facades in the scene"""
    bl_idname = "xp_ext.export_facades"
    bl_label = "Export Facades"
    bl_description = "Export X-Plane facades from the visible collections."

    def execute(self, context):
        #Iterate over all the collections in the scene
        for col in bpy.data.collections:
            #If the collection is a facade, and is not hidden, export it
            if col.xp_fac.exportable and collection_utils.get_collection_is_visible(col):
                exporter.export_fac(col)

        return {'FINISHED'}

class BTN_run_tests(bpy.types.Operator):
    """Run all tests in the addon"""
    bl_idname = "xp_ext.run_tests"
    bl_label = "Run Tests"
    bl_description = "Run all tests in the addon. This is a development tool and should not be used in production. Will delete ALL scene content"

    def execute(self, context):
        #Import the test module and run the tests
        from .Helpers import test_utils
        test_utils.run_all_tests()

        return {'FINISHED'}

class BTN_TEST_config_bake_settings(bpy.types.Operator):
    """Test the config_bake_settings function"""
    bl_idname = "xp_ext.test_config_bake_settings"
    bl_label = "Test Config Bake Settings"
    bl_options = {'REGISTER', 'UNDO'}

    bake_type: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        from .Helpers import bake_utils
        mats = bake_utils.get_source_materials()

        if self.bake_type == "BASE":
            print("Testing config for base bake settings")
            bake_utils.config_source_materials(bake_utils.BakeType.BASE, mats)
        elif self.bake_type == "NORMAL":
            print("Testing config for normal bake settings")
            bake_utils.config_source_materials(bake_utils.BakeType.NORMAL, mats)
        elif self.bake_type == "ROUGHNESS":
            print("Testing config for roughness bake settings")
            bake_utils.config_source_materials(bake_utils.BakeType.ROUGHNESS, mats)
        elif self.bake_type == "METALNESS":
            print("Testing config for metalness bake settings")
            bake_utils.config_source_materials(bake_utils.BakeType.METALNESS, mats)
        elif self.bake_type == "LIT":
            print("Testing config for lit bake settings")
            bake_utils.config_source_materials(bake_utils.BakeType.LIT, mats)
        else:
            print("Resetting material settings")
            bake_utils.reset_source_materials(mats)

        return {'FINISHED'}

class BTN_copy_decal(bpy.types.Operator):
    """Copy a PROP_decal from a material's collection property"""
    bl_idname = "xp_ext.copy_decal"
    bl_label = "Copy Decal"
    bl_description = "Copies a decal from the material's decals collection property to the clipboard in a format that can be pasted into another material's decal collection property. This is useful for copying decals between materials."
    bl_options = {'REGISTER', 'UNDO'}  # Add 'REGISTER' here

    material_name: bpy.props.StringProperty() # type: ignore
    decal_index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        # Boilerplate: get material and decal
        mat = bpy.data.materials.get(self.material_name)
        if not mat:
            self.report({'ERROR'}, f"Material '{self.material_name}' not found.")
            return {'CANCELLED'}
        if self.decal_index < 0 or self.decal_index >= len(mat.xp_materials.decals):
            self.report({'ERROR'}, f"Decal index {self.decal_index} out of range.")
            return {'CANCELLED'}
        decal = mat.xp_materials.decals[self.decal_index]

        misc_utils.copy_to_clipboard(decal_utils.get_decal_command(decal, ""))

        return {'FINISHED'}

class BTN_paste_decal(bpy.types.Operator):
    """Paste to a PROP_decal in a material's collection property"""
    bl_idname = "xp_ext.paste_decal"
    bl_label = "Paste Decal"
    bl_description = "Pastes a PROP_decal from the clipboard to a material's collection property. The clipboard must contain a valid decal command."
    bl_options = {'REGISTER', 'UNDO'}  # Add 'REGISTER' here

    material_name: bpy.props.StringProperty() # type: ignore
    decal_index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        # Boilerplate: get material and decal
        mat = bpy.data.materials.get(self.material_name)
        if not mat:
            self.report({'ERROR'}, f"Material '{self.material_name}' not found.")
            return {'CANCELLED'}
        if self.decal_index < 0 or self.decal_index >= len(mat.xp_materials.decals):
            self.report({'ERROR'}, f"Decal index {self.decal_index} out of range.")
            return {'CANCELLED'}
        decal = mat.xp_materials.decals[self.decal_index]

        # Place paste logic here
        clipboard_content = misc_utils.get_from_clipboard()

        #Make sure it starts with the appropriate command
        if clipboard_content.startswith("NORMAL_DECAL"):
            if decal.is_normal:
                #Now more in depth check
                tokens = clipboard_content.split()
                if tokens[0] == "NORMAL_DECAL_PARAMS_PROJ":
                    if len(tokens) == 11:
                        decal_utils.get_decal_from_command(clipboard_content, decal)
                    else:
                        log_utils.new_section("Decal Paste")
                        log_utils.error("Invalid NORMAL_DECAL command format. Expected 'NORMAL_DECAL_PARAMS_PROJ' with 11 parameters. Got: " + clipboard_content)
                        log_utils.display_messages()
                elif tokens[0] == "NORMAL_DECAL_PARAMS":
                    if len(tokens) == 10:
                        decal_utils.get_decal_from_command(clipboard_content, decal)
                    else:
                        log_utils.new_section("Decal Paste")
                        log_utils.error("Invalid NORMAL_DECAL command format. Expected 'NORMAL_DECAL_PARAMS' with 10 parameters. Got: " + clipboard_content)
                        log_utils.display_messages()
                else:
                    log_utils.new_section("Decal Paste")
                    log_utils.error("Invalid NORMAL_DECAL command format. Expected 'NORMAL_DECAL_PARAMS_PROJ' or 'NORMAL_DECAL_PARAMS' with correct number of parameters. Got: " + clipboard_content)
                    log_utils.display_messages()
            else:
                log_utils.new_section("Decal Paste")
                log_utils.error("Cannot paste a NORMAL_DECAL command into a non-normal map decal slot. The clipboard content is: " + clipboard_content)
                log_utils.display_messages()
                return {'CANCELLED'}
                
        elif clipboard_content.startswith("DECAL"):
            if not decal.is_normal:
                #Now more in depth check
                tokens = clipboard_content.split()
                if tokens[0] == "DECAL_PARAMS_PROJ":
                    if len(tokens) == 17:
                        decal_utils.get_decal_from_command(clipboard_content, decal)
                    else:
                        log_utils.new_section("Decal Paste")
                        log_utils.error("Invalid DECAL command format. Expected 'DECAL_PARAMS_PROJ' with 17 parameters. Got: " + clipboard_content)
                        log_utils.display_messages()
                elif tokens[0] == "DECAL_PARAMS":
                    if len(tokens) == 16:
                        decal_utils.get_decal_from_command(clipboard_content, decal)
                    else:
                        log_utils.new_section("Decal Paste")
                        log_utils.error("Invalid DECAL command format. Expected 'DECAL_PARAMS' with 16 parameters. Got: " + clipboard_content)
                        log_utils.display_messages()
                else:
                    log_utils.new_section("Decal Paste")
                    log_utils.error("Invalid DECAL command format. Expected 'DECAL_PARAMS_PROJ' or 'DECAL_PARAMS' with correct number of parameters. Got: " + clipboard_content)
                    log_utils.display_messages()
            else:
                log_utils.new_section("Decal Paste")
                log_utils.error("Cannot paste a DECAL command into a normal map decal slot. The clipboard content is: " + clipboard_content)
                log_utils.display_messages()
        else:
            log_utils.new_section("Decal Paste")
            log_utils.error("Clipboard content does not start with 'NORMAL_DECAL' or 'DECAL'. Got: " + clipboard_content)
            log_utils.display_messages()
            return {'CANCELLED'}

        return {'FINISHED'}

class BTN_preview_lods_for_distance(bpy.types.Operator):
    """Preview LODs for a given distance"""
    bl_idname = "xp_ext.preview_lods_for_distance"
    bl_label = "Preview LODs for Distance"
    bl_description = "Preview the LODs for a given distance. This is a development tool and should not be used in production."
    bl_options = {'REGISTER', 'UNDO'}  # Add 'REGISTER' here

    def execute(self, context):
        #Iterate over all objects.
        # Get their parent collection to learn the LOD settings
        # Get the object's LOD bucket, and thereby whether it's visible or not
        # Then show or hide the object
        for obj in bpy.data.objects:
            #Get the parent collection
            parent_col = obj.users_collection[0] if obj.users_collection else None

            if parent_col is None:
                continue
            
            lod_ranges = []

            if obj.xplane.lod[0]:
                lod_ranges.append([parent_col.xplane.layer.lod[0].near, parent_col.xplane.layer.lod[0].far])
            
            if obj.xplane.lod[1]:
                lod_ranges.append([parent_col.xplane.layer.lod[1].near, parent_col.xplane.layer.lod[1].far])

            if obj.xplane.lod[2]:
                lod_ranges.append([parent_col.xplane.layer.lod[2].near, parent_col.xplane.layer.lod[2].far])

            if obj.xplane.lod[3]:
                lod_ranges.append([parent_col.xplane.layer.lod[3].near, parent_col.xplane.layer.lod[3].far])

            for range in lod_ranges:
                if range[0] <= bpy.context.scene.xp_ext.lod_distance_preview <= range[1]:
                    #If the distance is within the range, show the object
                    obj.hide_viewport = False
                    break
                else:
                    #If the distance is not within the range, hide the object
                    obj.hide_viewport = True

        return {'FINISHED'}

def menu_func_import_options(self, context):
    self.layout.operator(IMPORT_lin.bl_idname, text="X-Plane Lines (.lin)")
    self.layout.operator(IMPORT_pol.bl_idname, text="X-Plane Polygons (.pol)")
    self.layout.operator(IMPORT_fac.bl_idname, text="X-Plane Facade (.fac)")
    self.layout.operator(IMPORT_obj.bl_idname, text="X-Plane Object (.obj)")
    self.layout.operator(IMPORT_agp.bl_idname, text="X-Plane Autogen Point (.agp)")
    
def register():
    bpy.utils.register_class(BTN_lin_exporter)
    bpy.utils.register_class(BTN_pol_exporter)
    bpy.utils.register_class(IMPORT_lin)
    bpy.utils.register_class(IMPORT_pol)
    bpy.utils.register_class(IMPORT_fac)
    bpy.utils.register_class(IMPORT_obj)
    bpy.utils.register_class(IMPORT_agp)
    bpy.utils.register_class(TEST_IMPORT_obj)
    bpy.utils.register_class(TEST_import_lin)
    bpy.utils.register_class(TEST_import_pol)
    bpy.utils.register_class(TEST_import_fac)
    bpy.utils.register_class(BTN_mats_autoodetect_textures)
    bpy.utils.register_class(BTN_mats_update_nodes)
    bpy.utils.register_class(BTN_mats_update_all_mat_nodes)
    bpy.utils.register_class(BTN_generate_flipbook_animation)
    bpy.utils.register_class(BTN_bake_low_poly)
    bpy.utils.register_class(BTN_update_xp_export_settings)
    bpy.utils.register_class(MENU_BT_fac_add_or_rem_in_fac)
    bpy.utils.register_class(MENU_BT_fac_swap_floors)
    bpy.utils.register_class(MENU_BT_fac_swap_walls)
    bpy.utils.register_class(MENU_BT_fac_swap_spellings)
    bpy.utils.register_class(MENU_BT_fac_duplicate_floor)
    bpy.utils.register_class(MENU_BT_fac_duplicate_wall)
    bpy.utils.register_class(MENU_BT_fac_duplicate_spelling)
    bpy.utils.register_class(BTN_fac_export_all)
    bpy.utils.register_class(BTN_run_tests)
    bpy.utils.register_class(BTN_TEST_config_bake_settings)
    bpy.utils.register_class(BTN_agp_exporter)
    bpy.utils.register_class(BTN_copy_decal)
    bpy.utils.register_class(BTN_paste_decal)
    bpy.utils.register_class(BTN_preview_lods_for_distance)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_options)

def unregister():
    bpy.utils.unregister_class(BTN_agp_exporter)
    bpy.utils.unregister_class(BTN_lin_exporter)
    bpy.utils.unregister_class(BTN_pol_exporter)
    bpy.utils.unregister_class(IMPORT_lin)
    bpy.utils.unregister_class(IMPORT_pol)
    bpy.utils.unregister_class(IMPORT_fac)
    bpy.utils.unregister_class(IMPORT_obj)
    bpy.utils.unregister_class(IMPORT_agp)
    bpy.utils.unregister_class(TEST_IMPORT_obj)
    bpy.utils.unregister_class(TEST_import_lin)
    bpy.utils.unregister_class(TEST_import_pol)
    bpy.utils.unregister_class(TEST_import_fac)
    bpy.utils.unregister_class(BTN_mats_autoodetect_textures)
    bpy.utils.unregister_class(BTN_mats_update_nodes)
    bpy.utils.unregister_class(BTN_mats_update_all_mat_nodes)
    bpy.utils.unregister_class(BTN_generate_flipbook_animation)
    bpy.utils.unregister_class(BTN_bake_low_poly)
    bpy.utils.unregister_class(BTN_update_xp_export_settings)
    bpy.utils.unregister_class(MENU_BT_fac_add_or_rem_in_fac)
    bpy.utils.unregister_class(MENU_BT_fac_swap_floors)
    bpy.utils.unregister_class(MENU_BT_fac_swap_walls)
    bpy.utils.unregister_class(MENU_BT_fac_swap_spellings)
    bpy.utils.unregister_class(MENU_BT_fac_duplicate_floor)
    bpy.utils.unregister_class(MENU_BT_fac_duplicate_wall)
    bpy.utils.unregister_class(MENU_BT_fac_duplicate_spelling)
    bpy.utils.unregister_class(BTN_fac_export_all)
    bpy.utils.unregister_class(BTN_run_tests)
    bpy.utils.unregister_class(BTN_TEST_config_bake_settings)
    bpy.utils.unregister_class(BTN_copy_decal)
    bpy.utils.unregister_class(BTN_paste_decal)
    bpy.utils.unregister_class(BTN_preview_lods_for_distance)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_options)
