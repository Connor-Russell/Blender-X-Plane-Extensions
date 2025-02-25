#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Props
#Purpose:   Provide a single file containing all properties for an X-Plane Line Object

import bpy # type: ignore
from . import material_config

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

#Function to force a UI update after a property has been changed
def update_ui(self, context):
    context.area.tag_redraw()

class PROP_lin_layer(bpy.types.PropertyGroup):
    is_exportable: bpy.props.BoolProperty(
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

    is_exportable: bpy.props.BoolProperty(
        name="Exportable",
        default=True,
        description="Whether or not this layer should be exported",
        update=update_ui
    ) # type: ignore
    
    export_path: bpy.props.StringProperty(
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

class PROP_xp_ext_scene(bpy.types.PropertyGroup):
    collection_search: bpy.props.StringProperty(
        name="Search",
        default="",
        description="Search for a collection to configure export",
        update=update_ui
    ) # type: ignore

    exportable_collections_expanded: bpy.props.BoolProperty(
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
        update=material_config.update_settings
    ) # type: ignore

    normal_texture: bpy.props.StringProperty(
        name="Normal Texture",
        description="The normal texture",
        default="",
        subtype='FILE_PATH',
        update=material_config.update_settings
    ) # type: ignore

    lit_texture: bpy.props.StringProperty(
        name="Lit Texture",
        description="The lit texture",
        default="",
        subtype='FILE_PATH',
        update=material_config.update_settings
    ) # type: ignore

    brightness: bpy.props.FloatProperty(
        name="Brightness",
        description="The brightness of the LIT texture in NITs. -1 to leave default",
        default=-1,
        update=material_config.update_settings
    ) # type: ignore

    draped: bpy.props.BoolProperty(
        name="Draped",
        description="Is the material draped?",
        default=False,
        update=material_config.update_settings
    ) # type: ignore

    hard: bpy.props.BoolProperty(
        name="Hard",
        description="Is the material hard?",
        default=False,
        update=material_config.update_settings
    ) # type: ignore

    blend_alpha: bpy.props.BoolProperty(
        name="Blend Alpha",
        description="Does the material have blended alpha?",
        default=False,
        update=material_config.update_settings
    ) # type: ignore

    blend_cutoff: bpy.props.FloatProperty(
        name="Blend Cutoff",
        description="The alpha cutoff value",
        default=0.5,
        min=0,
        max=1,
        update=material_config.update_settings
    ) # type: ignore

    cast_shadow: bpy.props.BoolProperty(
        name="Casts Shadows",
        description="Does the material cast shadows?",
        default=True,
        update=material_config.update_settings
    ) # type: ignore

    polygon_offset: bpy.props.IntProperty(
        name="Polygon Offset",
        description="The polygon offset",
        default=0,
        min=0,
        max=3,
        update=material_config.update_settings
    ) # type: ignore

    #Layer group property
    layer_group: bpy.props.EnumProperty(
        name="Layer Group",
        description="Select the layer group",
        items=layer_group_enum,
        default='OBJECTS',
        update=material_config.update_settings
    ) # type: ignore

    #Layer group offset property
    layer_group_offset: bpy.props.IntProperty(
        name="Layer Group Offset",
        description="The layer group offset",
        default=0,
        min=-5,
        max=5,
        update=material_config.update_settings
    ) # type: ignore

    #Bool seperate normal and albedo decals
    seperate_decals: bpy.props.BoolProperty(
        name="Seperate Normal and Albedo Decals",
        description="Seperate the normal and albedo decals",
        default=False,
        update=material_config.update_settings
    ) # type: ignore

    #String modulator texture for the decals
    decal_modulator: bpy.props.StringProperty(
        name="Decal Modulator",
        description="The modulator texture for the decals",
        default="",
        subtype='FILE_PATH',
        update=material_config.update_settings
    ) # type: ignore

    #Decal properties
    decal_one: bpy.props.PointerProperty(type=DecalProperties.PROP_Decal) # type: ignore
    decal_two: bpy.props.PointerProperty(type=DecalProperties.PROP_Decal) # type: ignore

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

class PROP_legacy_mats(bpy.types.PropertyGroup):

    bpy.types.Material.alb_texture = bpy.props.StringProperty(
        name="LEGACY Albedo Texture",
        description="The albedo texture",
        default="",
        subtype='FILE_PATH'
    ) # type: ignore

    bpy.types.Material.normal_texture = bpy.props.StringProperty(
        name="LEGACY Normal Texture",
        description="The normal texture",
        default="",
        subtype='FILE_PATH'
    ) # type: ignore

    bpy.types.Material.lit_texture = bpy.props.StringProperty(
        name="LEGACY Lit Texture",
        default="",
        subtype='FILE_PATH'
    ) # type: ignore

    bpy.types.Material.brightness = bpy.props.FloatProperty(
        name="LEGACY Brightness",
        description="The brightness of the LIT texture in NITs",
        default=1000
    ) # type: ignore

    bpy.types.Material.draped = bpy.props.BoolProperty(
        name="LEGACY Draped",
        default=False
    ) # type: ignore

    bpy.types.Material.hard = bpy.props.BoolProperty(
        name="LEGACY Hard",
        default=False
    ) # type: ignore

    bpy.types.Material.blend_alpha = bpy.props.BoolProperty(
        name="LEGACY Blend Alpha",
        description="Does the material have blended alpha?",
        default=False
    ) # type: ignore

    bpy.types.Material.blend_cutoff = bpy.props.FloatProperty(
        name="LEGACY Blend Cutoff",
        description="The alpha cutoff value",
        default=0.5
    ) # type: ignore

    bpy.types.Material.cast_shadow = bpy.props.BoolProperty(
        name="LEGACY Casts Shadows",
        description="Does the material cast shadows?",
        default=True
    ) # type: ignore

    bpy.types.Material.polygon_offset = bpy.props.IntProperty(
        name="LEGACY Polygon Offset",
        description="The polygon offset",
        default=0
    ) # type: ignore

    #Layer group property
    bpy.types.Material.layer_group = bpy.props.EnumProperty(
        name="LEGACY Layer Group",
        description="Select the layer group",
        items=MaterialPanel.layer_group_enum,
        default='OBJECTS'
    ) # type: ignore

    #Layer group offset property
    bpy.types.Material.layer_group_offset = bpy.props.IntProperty(
        name="LEGACY Layer Group Offset",
        description="The layer group offset",
        default=0
    ) # type: ignore

def register():
    
    bpy.utils.register_class(PROP_lin_layer)
    bpy.utils.register_class(PROP_lin_collection)
    bpy.utils.register_class(PROP_xp_ext_scene)
    bpy.utils.register_class(PROP_mats)
    bpy.utils.register_class(PROP_decal)
    bpy.utils.register_class(PROP_legacy_mats)

    bpy.types.Object.xp_lin = bpy.props.PointerProperty(type=PROP_lin_layer)
    bpy.types.Collection.xp_lin = bpy.props.PointerProperty(type=PROP_lin_collection)
    bpy.types.Scene.xp_ext = bpy.props.PointerProperty(type=PROP_xp_ext_scene)
    bpy.types.Material.xp_materials = bpy.props.PointerProperty(type=PROP_mats)
    bpy.types.Material.xp_decals = bpy.props.PointerProperty(type=PROP_decal)

def unregister():

    bpy.utils.unregister_class(PROP_lin_layer)
    bpy.utils.unregister_class(PROP_lin_collection)
    bpy.utils.unregister_class(PROP_xp_ext_scene)
    bpy.utils.unregister_class(PROP_mats)
    bpy.utils.unregister_class(PROP_decal)

    del bpy.types.Object.xp_lin
    del bpy.types.Collection.xp_lin
    del bpy.types.Scene.xp_ext
    del bpy.types.Material.xp_materials
