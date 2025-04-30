#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Props
#Purpose:   Provide a single file containing all properties for an X-Plane Line Object

import bpy # type: ignore
from . import material_config
from .Helpers import facade_utils
from bpy.app.handlers import persistent # type: ignore

#Enum for types. Can be START END or SEGMENT
line_type = [
    ("START", "Start", "Start"),
    ("END", "End", "End"),
    ("SEGMENT", "Segment", "Segment")
]

#Enum for layer groups
layer_group_enum = [
    ('TERRAIN', "Terrain", "Terrain layer group"),
    ('BEACHES', "Beaches", "Beaches layer group"),
    ('SHOULDERS', "Shoulders", "Shoulders layer group"),
    ('TAXIWAYS', "Taxiways", "Taxiways layer group"),
    ('RUNWAYS', "Runways", "Runways layer group"),
    ('MARKINGS', "Markings", "Markings layer group"),
    ('AIRPORTS', "Airports", "Airports layer group"),
    ('ROADS', "Roads", "Roads layer group"),
    ('OBJECTS', "Objects", "Objects layer group"),
    ('LIGHT_OBJECTS', "Light Objects", "Light Objects layer group"),
    ('CARS', "Cars", "Cars layer group"),
]

#Enum for collision types
collision_type_enum = [
    ('NONE', "None", "No collision"),
    ('CONCRETE', "Concrete", "Concrete collision"),
    ('ASPHALT', "Asphalt", "Asphalt collision")
]

#TODO: Kill this code and all it's references. ENUMs cause problems
def get_all_collection_names(self, context):
    enum_results = []
    for col in bpy.data.collections:
        enum_results.append((col.name, col.name, col.name))
        
    if len(enum_results) == 0:
        enum_results.append(("NO_COLLECTIONS", "No Collections", "No Collections"))

    return enum_results

#Triggers UI redraw
def update_ui(self, context):
    context.area.tag_redraw()

#General properties

class PROP_attached_obj(bpy.types.PropertyGroup):
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the object is exportable", default=True) # type: ignore
    draped: bpy.props.BoolProperty(name="Draped", description="Whether the object is draped", default=False)    # type: ignore
    resource: bpy.props.StringProperty(name="Resource", description="The resource for the object")  # type: ignore

class PROP_xp_ext_scene(bpy.types.PropertyGroup):
    lin_collection_search: bpy.props.StringProperty(
        name="Search",
        default="",
        description="Search for a collection to configure export",
        update=update_ui
    ) # type: ignore

    lin_disabled_collections_expanded: bpy.props.BoolProperty(
        name="Exportable Collections Expanded",
        default=False,
        update=update_ui
    ) # type: ignore

    fac_collection_search: bpy.props.StringProperty(
        name="Search",
        default="",
        description="Search for a collection to configure export",
        update=update_ui
    ) # type: ignore

    fac_disabled_collections_expanded: bpy.props.BoolProperty(
        name="Exportable Collections Expanded",
        default=False,
        update=update_ui
    ) # type: ignore

    low_poly_bake_resolution: bpy.props.FloatProperty(
        name="Bake Resolution",
        description="The resolution of the low poly bake",
        default=1024,
        min=32.0,
        max=8192
    ) #type: ignore

    low_poly_bake_ss_factor: bpy.props.FloatProperty(
         name="Bake Super-Sampling Factor",
         description="The Sumper-Sampling factor of the low poly bake",
         default=1.0,
         min=1.0,
         max=4.0
     ) #type: ignore

#Material properties

class PROP_decal(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="Enabled", description="Whether this decal slot is enabled", update=update_ui)# type: ignore
    normal_follows_albedo: bpy.props.BoolProperty(name="Normal Follows Albedo", description="Whether the normal map should be the same as the albedo map", update=update_ui, default=True)# type: ignore
    decal_lib: bpy.props.StringProperty(name="Decal Asset", description=".dcl to use instead of putting it directly in the facade", update=update_ui)# type: ignore
    alb: bpy.props.StringProperty(name="Decal Albedo", description="The albedo to use in the decal", subtype="FILE_PATH")   # type: ignore
    nml: bpy.props.StringProperty(name="Decal Normal", description="The normal to use in the decal (uses RGB keys)", subtype="FILE_PATH")    # type: ignore

    projected: bpy.props.BoolProperty(name="Projected", description="Whether the decal's UVs are projected, independant of the base UVs'", update=update_ui)# type: ignore
    tile_ratio: bpy.props.FloatProperty(name="Tile Ratio", description="The ratio of the decal's tiling to the base texture's tiling", default=1.0)# type: ignore
    scale_x: bpy.props.FloatProperty(name="Scale X", description="The scale of the decal in the x direction", default=1.0)# type: ignore
    scale_y: bpy.props.FloatProperty(name="Scale Y", description="The scale of the decal in the y direction", default=1.0)# type: ignore

    nml_projected: bpy.props.BoolProperty(name="Projected", description="Whether the normal map's UVs are projected, independant of the base UVs'", update=update_ui)# type: ignore
    nml_tile_ratio: bpy.props.FloatProperty(name="Tile Ratio", description="The ratio of the normal map's tiling to the base texture's tiling", default=1.0)# type: ignore
    nml_scale_x: bpy.props.FloatProperty(name="Scale X", description="The scale of the normal map in the x direction", default=1.0)# type: ignore
    nml_scale_y: bpy.props.FloatProperty(name="Scale Y", description="The scale of the normal map in the y direction", default=1.0)# type: ignore

    dither_ratio: bpy.props.FloatProperty(name="Dither Ratio", description="How much the alpha of the decal modulates the alpha of the base. Probably want this at 0 in a facade...")# type: ignore

    rgb_strength_constant: bpy.props.FloatProperty(name="RGB Strength Constant", description="How strong the RGB decal always is", default=1.0)# type: ignore
    rgb_strength_modulator: bpy.props.FloatProperty(name="RGB Strength Modulator", description="How strong the effect of the keying or modulator texture is on RGB decal's application", default=0.0)# type: ignore

    rgb_decal_key_red: bpy.props.FloatProperty(name="Red key for RGB Decal", description="The red key for the RGB decal key", default=0.0)# type: ignore
    rgb_decal_key_green: bpy.props.FloatProperty(name="Green key for RGB Decal", description="The green key for the RGB decal key", default=0.0)# type: ignore
    rgb_decal_key_blue: bpy.props.FloatProperty(name="Blue key for RGB Decal", description="The blue key for the RGB decal key", default=0.0)# type: ignore
    rgb_decal_key_alpha: bpy.props.FloatProperty(name="Alpha key for RGB Decal", description="The alpha key for the RGB decal key", default=0.0)# type: ignore

    alpha_strength_constant: bpy.props.FloatProperty(name="Alpha Strength Constant", description="How strong the alpha decal always is", default=1.0)# type: ignore
    alpha_strength_modulator: bpy.props.FloatProperty(name="Alpha Strength Modulator", description="How strong the effect of the keying or modulator texture is on alpha decal's application", default=0.0)# type: ignore

    alpha_decal_key_red: bpy.props.FloatProperty(name="Red key for Alpha Decal", description="The red key for the alpha decal key", default=0.0)# type: ignore
    alpha_decal_key_green: bpy.props.FloatProperty(name="Green key for Alpha Decal", description="The green key for the alpha decal key", default=0.0)# type: ignore
    alpha_decal_key_blue: bpy.props.FloatProperty(name="Blue key for Alpha Decal", description="The blue key for the alpha decal key", default=0.0)# type: ignore
    alpha_decal_key_alpha: bpy.props.FloatProperty(name="Alpha key for Alpha Decal", description="The alpha key for the alpha decal key", default=0.0)# type: ignore

    nml_strength_constant: bpy.props.FloatProperty(name="Normal Strength Constant", description="How strong the normal decal always is", default=1.0)# type: ignore
    nml_strength_modulator: bpy.props.FloatProperty(name="Normal Strength Modulator", description="How strong the effect of the keying or modulator texture is on normal decal's application", default=0.0)# type: ignore

    nml_decal_key_red: bpy.props.FloatProperty(name="Red key for Normal Decal", description="The red key for the normal decal key", default=0.0)# type: ignore
    nml_decal_key_green: bpy.props.FloatProperty(name="Green key for Normal Decal", description="The green key for the normal decal key", default=0.0)# type: ignore
    nml_decal_key_blue: bpy.props.FloatProperty(name="Blue key for Normal Decal", description="The blue key for the normal decal key", default=0.0)# type: ignore
    nml_decal_key_alpha: bpy.props.FloatProperty(name="Alpha key for Normal Decal", description="The alpha key for the normal decal key", default=0.0)# type: ignore

    #Internals
    visible: bpy.props.BoolProperty(name="Visible", description="Whether this decal is visible in the UI", default=True)# type: ignore

class PROP_mats(bpy.types.PropertyGroup):
    #Properties for the material:
    # - Alb texture - String
    # - Normal texture - String
    # - Lit textures - String
    # - Draped - Bool
    # - Hard - Bool
    # - Blend alpha - bool
    # - Polygon offset - int

    alb_texture: bpy.props.StringProperty(
        name="Albedo Texture",
        description="The albedo texture",
        default="",
        subtype='FILE_PATH',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    normal_texture: bpy.props.StringProperty(
        name="Normal Texture",
        description="The normal texture",
        default="",
        subtype='FILE_PATH',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    normal_tile_ratio: bpy.props.FloatProperty(
        name="Normal Tile Ratio",
        description="The number of times the normal tiles to the albedo",
        default=1,
        min=0,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    lit_texture: bpy.props.StringProperty(
        name="Lit Texture",
        description="The lit texture",
        default="",
        subtype='FILE_PATH',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    brightness: bpy.props.FloatProperty(
        name="Brightness",
        description="The brightness of the LIT texture in NITs. -1 to leave default",
        default=-1,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    draped: bpy.props.BoolProperty(
        name="Draped",
        description="Is the material draped?",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    hard: bpy.props.BoolProperty(
        name="Hard",
        description="Is the material hard?",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    blend_alpha: bpy.props.BoolProperty(
        name="Blend Alpha",
        description="Does the material have blended alpha?",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    blend_cutoff: bpy.props.FloatProperty(
        name="Blend Cutoff",
        description="The alpha cutoff value",
        default=0.5,
        min=0,
        max=1,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    cast_shadow: bpy.props.BoolProperty(
        name="Casts Shadows",
        description="Does the material cast shadows?",
        default=True,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    polygon_offset: bpy.props.IntProperty(
        name="Polygon Offset",
        description="The polygon offset",
        default=0,
        min=0,
        max=3,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    #Layer group property
    layer_group: bpy.props.EnumProperty(
        name="Layer Group",
        description="Select the layer group",
        items=layer_group_enum,
        default='OBJECTS',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    #Layer group offset property
    layer_group_offset: bpy.props.IntProperty(
        name="Layer Group Offset",
        description="The layer group offset",
        default=0,
        min=-5,
        max=5,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    #Bool seperate normal and albedo decals
    seperate_decals: bpy.props.BoolProperty(
        name="Seperate Normal and Albedo Decals",
        description="Seperate the normal and albedo decals",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    #String modulator texture for the decals
    decal_modulator: bpy.props.StringProperty(
        name="Decal Modulator",
        description="The modulator texture for the decals",
        default="",
        subtype='FILE_PATH',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    #Decal properties
    decal_one: bpy.props.PointerProperty(type=PROP_decal) # type: ignore
    decal_two: bpy.props.PointerProperty(type=PROP_decal) # type: ignore

#Line properties

class PROP_lin_layer(bpy.types.PropertyGroup):
    exportable: bpy.props.BoolProperty(
        name="Export",
        default=True,
        description="Whether or not this layer should be exported",
        update=update_ui
    ) # type: ignore
    
    type: bpy.props.EnumProperty(
        name="Type",
        items=line_type,
        default="SEGMENT",
        description="What part of the line this is",
        update=update_ui
    ) # type: ignore

class PROP_lin_collection(bpy.types.PropertyGroup):
    is_ui_expanded: bpy.props.BoolProperty(
        name="UI Expanded",
        default=False,
        update=update_ui
    ) # type: ignore

    exportable: bpy.props.BoolProperty(
        name="Exportable",
        default=False,
        description="Whether or not this layer should be exported",
        update=update_ui
    ) # type: ignore
    
    name: bpy.props.StringProperty(
        name="Export Path",
        default="",
        subtype="FILE_PATH",
        description="The path to the file to export to, and name",
        update=update_ui
    ) # type: ignore
    
    mirror: bpy.props.BoolProperty(
        name="Mirror",
        default=True,
        description="Whether or not to mirror the line. Keep this on to avoid stretching, unless the line contains text",
        update=update_ui
    ) # type: ignore
    
    segment_count: bpy.props.IntProperty(
        name="Segment Count",
        default=0,
        min=0,
        description="If non-zero, X-Plane will stretch/compress the texture to always end on a subdivision. Useful for alignment with end caps",
        update=update_ui
    ) # type: ignore

#Facade properties

class PROP_fac_mesh(bpy.types.PropertyGroup):
    far_lod: bpy.props.IntProperty(name="Far LOD", description="The far LOD for the object", default=1000)  # type: ignore
    group: bpy.props.IntProperty(name="Group", description="The group for the object. Use for layering transparency") # type: ignore
    cuts: bpy.props.IntProperty(name="Segments", description="The number of segments in the mesh (used for curves. If it is a flat plane with 3 subdivisions, you have 4 segments)")   # type: ignore
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the object is exportable", default=True) # type: ignore

class PROP_fac_filtered_spelling_choices(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")  #type: ignore

class PROP_fac_spelling_entry(bpy.types.PropertyGroup):
    collection: bpy.props.EnumProperty(
        name="Collection",
        items=get_all_collection_names
    ) # type: ignore

class PROP_fac_spelling(bpy.types.PropertyGroup):
    is_ui_expanded: bpy.props.BoolProperty(name="UI Expanded", description="Whether the spelling is expanded in the UI", default=False, update=update_ui)# type: ignore
    entries: bpy.props.CollectionProperty(type=PROP_fac_spelling_entry)# type: ignore

class PROP_fac_wall(bpy.types.PropertyGroup):
    min_length: bpy.props.FloatProperty(name="Min Length", description="The minimum length of the wall", default=0, min=0, max=10000)# type: ignore
    max_length: bpy.props.FloatProperty(name="Max Length", description="The maximum length of the wall", default=1000, min=0, max=10000)# type: ignore
    min_heading: bpy.props.FloatProperty(name="Min Heading", description="The minimum heading of the wall", default=0, min=0, max=360)# type: ignore
    max_heading: bpy.props.FloatProperty(name="Max Heading", description="The maximum heading of the wall", default=360, min=0, max=360)# type: ignore
    name: bpy.props.StringProperty(name="Wall Name", default="", update=update_ui)# type: ignore
    spellings: bpy.props.CollectionProperty(type=PROP_fac_spelling)# type: ignore
    is_ui_expanded: bpy.props.BoolProperty(name="UI Expanded", description="Whether the wall is expanded in the UI", default=False, update=update_ui)# type: ignore

class PROP_fac_floor(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Floor Name", description="The name of the floor")# type: ignore
    roof_collection: bpy.props.EnumProperty(
        name="Roof Collection",
        items=get_all_collection_names,
        update=update_ui  # type: ignore
    )
    walls: bpy.props.CollectionProperty(type=PROP_fac_wall)# type: ignore
    is_ui_expanded: bpy.props.BoolProperty(name="UI Expanded", description="Whether the floor is expanded in the UI", default=False, update=update_ui)# type: ignore
    roof_collisions: bpy.props.BoolProperty(name="Roof Collisions", description="Whether the roof has collisions enabled", default=True, update=update_ui)# type: ignore
    roof_two_sided: bpy.props.BoolProperty(name="Roof Two Sided", description="Whether the roof is two sided", default=False, update=update_ui)# type: ignore

class PROP_facade(bpy.types.PropertyGroup):

    #Facade name
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the facade is exportable", default=False, update=update_ui)# type: ignore
    name: bpy.props.StringProperty( name="Facade Name", description="The name of the facade")# type: ignore
    is_ui_expanded: bpy.props.BoolProperty(name="UI Expanded", description="Whether the facade is expanded in the UI", default=False, update=update_ui)# type: ignore

    #Global properties
    graded: bpy.props.BoolProperty(name="Graded", description="Whether the facade is graded, otherwise draped")# type: ignore
    ring: bpy.props.BoolProperty(name="Ring", description="Whether the facade is a closed or an open ring")# type: ignore

    #Wall properties
    render_wall: bpy.props.BoolProperty(name="Render Wall", description="Whether the wall is rendered", update=update_ui)# type: ignore
    wall_material: bpy.props.PointerProperty(type=bpy.types.Material, name="Wall Material", description="The material to use for the wall", update=update_ui)# type: ignore

    #Roof properties
    render_roof: bpy.props.BoolProperty(name="Render Roof", description="Whether the roof is rendered", update=update_ui)# type: ignore
    roof_material: bpy.props.PointerProperty(type=bpy.types.Material, name="Roof Material", description="The material to use for the roof", update=update_ui)# type: ignore

    #Floors
    floors: bpy.props.CollectionProperty(type=PROP_fac_floor)# type: ignore

    #Eligable spelling choices
    spelling_choices: bpy.props.CollectionProperty(type=PROP_fac_filtered_spelling_choices)# type: ignore

#This code is for sad blender reasons. In Blender, Enum properties reference by *index* so if collections are added or removed, then the collection the user has selected changes
#So we can't used indexes. But we don't want users to have to type collection names. So we have a string property that we add to the UI with a prop_search
#Prop_serach however needs data. And that data cannot be updated in the UI due to Blender limits. Soo we have to have a handler that gets called *every time the scene changes* *cries in excess code* to keep the list up to date
#And that is what this code is. @persistent is a decorator that makes Blender keep the function even after a file is loaded/closed or whatever vs just that session.
@persistent
def update_fac_spelling_choices():
    for col in bpy.data.collections:
        if col.xp_fac:
            if col.xp_fac.exportable:
                # Clear the existing list
                col.xp_fac.spelling_choices.clear()

                # Add collections that meet your criteria
                for add_col in bpy.data.collections:
                    if not add_col.name.endswith("_Curved"):  # Example filter
                        item = col.xp_fac.spelling_choices.add()
                        item.name = add_col.name

@persistent
def update_fac_spelling_choices_depgraph_handler(scene):
    update_fac_spelling_choices()

@persistent
def update_fac_spelling_choices_load_handler(in_file_path, in_startup_file_path):
    update_fac_spelling_choices()

def register():
    
    bpy.utils.register_class(PROP_fac_filtered_spelling_choices)
    bpy.utils.register_class(PROP_lin_layer)
    bpy.utils.register_class(PROP_lin_collection)
    bpy.utils.register_class(PROP_xp_ext_scene)
    bpy.utils.register_class(PROP_decal)
    bpy.utils.register_class(PROP_mats)
    bpy.utils.register_class(PROP_attached_obj)
    bpy.utils.register_class(PROP_fac_mesh)
    bpy.utils.register_class(PROP_fac_spelling_entry)
    bpy.utils.register_class(PROP_fac_spelling)
    bpy.utils.register_class(PROP_fac_wall)
    bpy.utils.register_class(PROP_fac_floor)
    bpy.utils.register_class(PROP_facade)
    

    bpy.types.Object.xp_lin = bpy.props.PointerProperty(type=PROP_lin_layer)
    bpy.types.Object.xp_attached_obj = bpy.props.PointerProperty(type=PROP_attached_obj)
    bpy.types.Object.xp_fac_mesh = bpy.props.PointerProperty(type=PROP_fac_mesh)
    bpy.types.Collection.xp_lin = bpy.props.PointerProperty(type=PROP_lin_collection)
    bpy.types.Collection.xp_fac = bpy.props.PointerProperty(type=PROP_facade)
    bpy.types.Scene.xp_ext = bpy.props.PointerProperty(type=PROP_xp_ext_scene)
    bpy.types.Material.xp_materials = bpy.props.PointerProperty(type=PROP_mats)

    bpy.app.handlers.depsgraph_update_pre.append(update_fac_spelling_choices_depgraph_handler)
    bpy.app.handlers.load_post.append(update_fac_spelling_choices_load_handler)

def unregister():
    bpy.app.handlers.load_post.remove(update_fac_spelling_choices_load_handler)
    bpy.app.handlers.depsgraph_update_pre.remove(update_fac_spelling_choices_depgraph_handler)

    del bpy.types.Material.xp_materials
    del bpy.types.Scene.xp_ext
    del bpy.types.Collection.xp_fac
    del bpy.types.Collection.xp_lin
    del bpy.types.Object.xp_fac_mesh
    del bpy.types.Object.xp_attached_obj
    del bpy.types.Object.xp_lin

    bpy.utils.unregister_class(PROP_facade)
    bpy.utils.unregister_class(PROP_fac_floor)
    bpy.utils.unregister_class(PROP_fac_wall)
    bpy.utils.unregister_class(PROP_fac_spelling)
    bpy.utils.unregister_class(PROP_fac_spelling_entry)
    bpy.utils.unregister_class(PROP_fac_mesh)
    bpy.utils.unregister_class(PROP_mats)
    bpy.utils.unregister_class(PROP_decal)
    bpy.utils.unregister_class(PROP_xp_ext_scene)
    bpy.utils.unregister_class(PROP_lin_collection)
    bpy.utils.unregister_class(PROP_lin_layer)
    bpy.utils.unregister_class(PROP_attached_obj)
    bpy.utils.unregister_class(PROP_fac_filtered_spelling_choices)