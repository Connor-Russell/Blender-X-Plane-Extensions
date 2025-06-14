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

        #If the material has an albedo texture, use that as our name
        if material.xp_materials.alb_texture != "":
            name = material.xp_materials.alb_texture

        #Remove the extension from the name
        name = name.replace(".png", "")
        name = name.replace(".dds", "")
        
        alb_check_path = file_utils.rel_to_abs(name + ".png")
        
        #Define the paths for the NML, and LIT
        nml_check_path = file_utils.rel_to_abs(name + "_NML.png")
        lit_check_path = file_utils.rel_to_abs(name + "_LIT.png")
        mat_check_path = ""

        if material.xp_materials.do_separate_material_texture:
            nml_check_path = file_utils.rel_to_abs(name + "_NRM.png")
            mat_check__path = file_utils.rel_to_abs(name + "_MAT.png")

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
    bl_idname = "xp.add_rem_fac"
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
    bpy.utils.register_class(BTN_bake_low_poly)
    bpy.utils.register_class(BTN_update_xp_export_settings)
    bpy.utils.register_class(MENU_BT_fac_add_or_rem_in_fac)
    bpy.utils.register_class(BTN_fac_export_all)
    bpy.utils.register_class(BTN_run_tests)
    bpy.utils.register_class(BTN_TEST_config_bake_settings)
    bpy.utils.register_class(BTN_agp_exporter)
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
    bpy.utils.unregister_class(BTN_bake_low_poly)
    bpy.utils.unregister_class(BTN_update_xp_export_settings)
    bpy.utils.unregister_class(MENU_BT_fac_add_or_rem_in_fac)
    bpy.utils.unregister_class(BTN_fac_export_all)
    bpy.utils.unregister_class(BTN_run_tests)
    bpy.utils.unregister_class(BTN_TEST_config_bake_settings)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_options)