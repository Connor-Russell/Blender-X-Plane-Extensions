#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Operators
#Purpose:   Provide a single file containing all operators for the X-Plane Line Exporter

import bpy  # type: ignore
from bpy_extras.io_utils import ImportHelper # type: ignore

from . import exporter
from . import importer
from . import material_config

class BTN_lin_exporter(bpy.types.Operator):
    bl_idname = "xp_ext.lin_exporter"
    bl_label = "Export X-Plane Lines"

    def execute(self, context):

        #Iterate through every collection. If it is exportable, and visible, export
        for col in bpy.data.collections:
            if col.xp_lin.is_exportable and (not col.hide_viewport):
                exporter.export_lin(col)

        return {'FINISHED'}
    
class IMPORT_lin(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xp_lin"
    bl_label = "Import X-Plane Lines"
    filename_ext = ".lin"
    filter_glob: bpy.props.StringProperty(default="*.lin", options={'HIDDEN'}) # type: ignore
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)  # To support multiple files

    def execute(self, context):
        # Implement your import logic here
        directory = self.filepath
        directory = directory[:directory.rfind("\\")]

        for cf in self.files:
            filepath = f"{directory}\\{cf.name}"
            importer.import_lin(filepath)

        return {'FINISHED'}

class BTN_mats_autoodetect_textures(bpy.types.Operator):
    """Autodetects the texture"""
    bl_idname = "xp_ext.autodetect_texture"
    bl_label = "Autodetect Texture"

    def execute(self, context):
        #Get the material
        material = context.material

        #Get the name
        name = material.name

        #If the name as an albedo texture, use that as our name
        if material.xp_materials.alb_texture != "":
            name = material.xp_materials.alb_texture

            #Remove the .png from the name
            name = name.replace(".png", "")
            name = name.replace(".dds", "")
        else:
            alb_check_path = FileUtils.resolve_relative_path(name + ".png")
            if os.path.exists(alb_check_path):
                material.xp_materials.alb_texture = name + ".png"

        #Define the paths for the NML, and LIT
        nml_check_path = FileUtils.resolve_relative_path(name + "_NML.png")
        lit_check_path = FileUtils.resolve_relative_path(name + "_LIT.png")

        #If the paths exist, set the properties
        if os.path.exists(nml_check_path):
            material.xp_materials.normal_texture = name + "_NML.png"
        if os.path.exists(lit_check_path):
            material.xp_materials.lit_texture = name + "_LIT.png"

        #Return success
        return {'FINISHED'}

class BTN_mats_update_nodes(bpy.types.Operator):
    """Called when the user hits Update Nodes in the XPMaterialProperties panel. This removes all material nodes and creates new ones with the new properties."""
    bl_idname = "xp_ext.update_material_nodes"
    bl_label = "Updates material nodes"

    def execute(self, context):
        #Call the function to update the settings
        material_config.update_settings(context.material.xp_materials, bpy.context.active_object)

        material_config.update_nodes(context.material)

        return {'FINISHED'}

class BTN_update_xp_export_settings(bpy.types.Operator):
    """Operator to update all the collections texture settings to the current material settings"""
    bl_idname = "xp_ext.update_collection_textures"
    bl_label = "Update Collection Textures"

    def execute(self, context):
        #For each collection:
        # get all the objects in that collection
        # for each object, get the material
        # IF that material has textures set, update that collection, set flag that that collection has been updated. Keep looping through the object, if we find one that is draped, update with that material
        for col in bpy.context.scene.collection.children:

            #Define flag
            updated = False

            #Get all the objects in the collection
            for obj in col.objects:
                mat = obj.active_material

                if mat != None:
                    xp_props = mat.xp_materials

                    #Check for textures
                    if xp_props.alb_texture != "":

                        #Set the layer groups
                        col.xplane.layer.layer_group = xp_props.layer_group.lower()
                        col.xplane.layer.layer_group_offset = xp_props.layer_group_offset
                        
                        if xp_props.draped:
                            col.xplane.layer.layer_group_draped = xp_props.layer_group.lower()
                            col.xplane.layer.layer_group_draped_offset = xp_props.layer_group_offset

                        #If we haven't updated yet, update
                        if not updated:
                            if xp_props.lit_texture != "":
                                if xp_props.brightness > 0:
                                    col.xplane.layer.luminance_override = True
                                    col.xplane.layer.luminance = int(xp_props.brightness)
                                else:
                                    col.xplane.layer.luminance_override = False
                                    col.xplane.layer.luminance = 1000

                                if xp_props.normal_texture != "":
                                    col.xplane.layer.normal_metalness_draped = True
                            else:
                                col.xplane.layer.luminance_override = False
                                col.xplane.layer.luminance = 1000

                            col.xplane.layer.texture = xp_props.alb_texture
                            col.xplane.layer.texture_lit = xp_props.lit_texture
                            col.xplane.layer.texture_normal = xp_props.normal_texture
                            col.xplane.layer.normal_metalness = True

                            if xp_props.draped:
                                col.xplane.layer.texture_draped = xp_props.alb_texture
                                col.xplane.layer.texture_draped_normal = xp_props.normal_texture
                                col.xplane.layer.normal_metalness_draped = True
                            else:
                                col.xplane.layer.texture_draped = ""
                                col.xplane.layer.texture_draped_normal = ""
                                col.xplane.layer.normal_metalness_draped = False
                            updated = True

                            #Now we need to set the decal properties
                            #Reset decal properties
                            col.xplane.layer.file_decal1 = ""
                            col.xplane.layer.file_decal2 = ""
                            col.xplane.layer.file_draped_decal1 = ""
                            col.xplane.layer.file_draped_decal2 = ""
                            col.xplane.layer.file_normal_decal1 = ""
                            col.xplane.layer.file_normal_decal2 = ""
                            col.xplane.layer.file_draped_normal_decal1 = ""
                            col.xplane.layer.file_draped_normal_decal2 = ""
                            col.xplane.layer.texture_modulator = ""
                            col.xplane.layer.texture_draped_modulator = ""

                            col.xplane.layer.texture_modulator = xp_props.decal_modulator

                            if xp_props.draped:
                                col.xplane.layer.texture_draped_modulator = xp_props.decal_modulator

                            if xp_props.seperate_decals:
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_one, 1)
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_two, 2)
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_three, 1)
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_four, 2)
                            else:
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_one, 1)
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_two, 2)

                        #If we have updated, but this one is draped, update with this one. Then we can skip the rest of the objects in this collection
                        if xp_props.draped:
                            col.xplane.layer.texture = xp_props.alb_texture
                            col.xplane.layer.texture_lit = xp_props.lit_texture
                            col.xplane.layer.texture_normal = xp_props.normal_texture
                            col.xplane.layer.texture_draped = xp_props.alb_texture
                            col.xplane.layer.texture_draped_normal = xp_props.normal_texture
                            col.xplane.layer.normal_metalness = True
                            col.xplane.layer.normal_metalness_draped = True

                            col.xplane.layer.texture_draped_modulator = xp_props.decal_modulator

                            if xp_props.seperate_decals:
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_one, 1)
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_two, 2)
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_three, 1)
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_four, 2)
                            else:
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_one, 1)
                                DecalProperties.set_xp_decal_prop(col, mat, xp_props.decal_two, 2)
        return {'FINISHED'}

#Class that handles the user hitting the bake to low poly button
class BTN_bake_low_poly(bpy.types.Operator):
    """Automatically bakes selected objects to active objects for base, normal, roughness, metalness, and lit, then saves into XP formats in the same folder as the .blend"""
    bl_idname = "xp_ext.bake_low_poly"
    bl_label = "Bake to Low Poly"

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
        AutoBaker.auto_bake_current_to_active()

        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(IMPORT_lin.bl_idname, text="X-Plane Lines (.lin)")
    
def register():
    bpy.utils.register_class(BTN_lin_exporter)
    bpy.utils.register_class(IMPORT_lin)
    bpy.utils.register_class(BTN_mats_autoodetect_textures)
    bpy.utils.register_class(BTN_mats_update_nodes)
    bpy.utils.register_class(BTN_update_xp_export_settings)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(BTN_lin_exporter)
    bpy.utils.unregister_class(IMPORT_lin)
    bpy.utils.unregister_class(BTN_mats_autoodetect_textures)
    bpy.utils.unregister_class(BTN_mats_update_nodes)
    bpy.utils.unregister_class(BTN_update_xp_export_settings)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)