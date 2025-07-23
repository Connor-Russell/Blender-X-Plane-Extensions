#Project:   Blender-X-Plane-Extensions
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
    ('CONCRETE', "Concrete", "Concrete"),
    ('ASPHALT', "Asphalt", "Asphalt"),
    ('GRASS', "Grass", "Grass"),
    ('DIRT', "Dirt", "Dirt"),
    ('GRAVEL', "Gravel", "Gravel"),
    ('LAKEBED', "Lakebed", "Lakebed"),
    ('SNOW', "Snow", "Snow"),
    ('SHOULDER', "Shoulder", "Shoulder"),
    ('BLASTPAD', "Blastpad", "Blastpad"),
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
    if context != None:
        if context.area != None:
            context.area.tag_redraw()

#General properties

class PROP_attached_obj(bpy.types.PropertyGroup):
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the object is exportable", default=True) # type: ignore
    draped: bpy.props.BoolProperty(name="Draped", description="Whether the object is draped", default=False)    # type: ignore
    resource: bpy.props.StringProperty(name="Resource", description="The resource for the object")  # type: ignore

class PROP_xp_ext_scene(bpy.types.PropertyGroup):
    last_save_plugin_version: bpy.props.IntProperty(
        name="Last Saved Plugin Version",
        default=1
    ) #type: ignore

    agp_collection_search: bpy.props.StringProperty(
        name="Search",
        default="",
        description="Search for a collection to configure export",
        update=update_ui
    ) # type: ignore

    agp_disabled_collections_expanded: bpy.props.BoolProperty(
        name="Exportable Collections Expanded",
        default=False,
        update=update_ui
    ) # type: ignore

    pol_collection_search: bpy.props.StringProperty(
        name="Search",
        default="",
        description="Search for a collection to configure export",
        update=update_ui
    ) # type: ignore

    pol_disabled_collections_expanded: bpy.props.BoolProperty(
        name="Exportable Collections Expanded",
        default=False,
        update=update_ui
    ) # type: ignore

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
    
    lod_distance_preview: bpy.props.FloatProperty(
        name="LOD Distance Preview",
        description="Show objects whose LODs would make them visible at this range",
        default=0.0,
        min=0.0
    ) # type: ignore

    autoanim_frame_start: bpy.props.IntProperty(
        name="Auto Animation Frame Start",
        description="The frame to start the auto animation on",
        default=1,
        min=0,
        update=update_ui
    ) # type: ignore

    autoanim_frame_end: bpy.props.IntProperty(
        name="Auto Animation Frame End",
        description="The frame to end the auto animation on",
        default=250,
        min=0,
        update=update_ui
    ) # type: ignore

    autoanim_dataref: bpy.props.StringProperty(
        name="Auto Animation Dataref",
        description="The dataref to use for the auto animation",
        default="",
        subtype='NONE',
        update=update_ui
    ) # type: ignore

    autoanim_start_value: bpy.props.FloatProperty(
        name="Auto Animation Start Value",
        description="The starting value of the dataref for flipbook animation",
        default=0.0,
        min=0.0,
        update=update_ui
    ) # type: ignore

    autoanim_end_value: bpy.props.FloatProperty(
        name="Auto Animation End Value",
        description="The ending value of the dataref for auto animation",
        default=1.0,
        min=0.0,
        update=update_ui
    ) # type: ignore

    autoanim_loop_value: bpy.props.FloatProperty(
        name="Auto Animation Loop Value",
        description="The value to loop the auto animation at",
        default=0.0,
        min=0.0,
        update=update_ui
    ) # type: ignore

    autoanim_keyframe_interval: bpy.props.IntProperty(
        name="Auto Animation Keyframe Interval",
        description="The interval between keyframes for the auto animation. In Blender Frames",
        default=1,
        min=1,
        update=update_ui
    ) # type: ignore

    autoanim_autodetect: bpy.props.BoolProperty(
        name="Auto Detect",
        description="Automatically detect the start and end frames",
        default=False
    ) # type: ignore

    autoanim_autodetect_fps: bpy.props.FloatProperty(
        name="Auto Detect FPS",
        description="The Frame Rate used to pick values when autodectecting",
        default=30.0
    ) # type: ignore

    menu_bake_expanded: bpy.props.BoolProperty(
        name="Bake Menu Expanded",
        description="Whether the bake menu is expanded",
        default=False,
        update=update_ui
    ) # type: ignore

    menu_lod_preview_expanded: bpy.props.BoolProperty(
        name="LOD Preview Menu Expanded",
        description="Whether the LOD preview menu is expanded",
        default=False,
        update=update_ui
    ) # type: ignore

    menu_autoanim_expanded: bpy.props.BoolProperty(
        name="Auto Animation Menu Expanded",
        description="Whether the auto animation menu is expanded",
        default=False,
        update=update_ui
    ) # type: ignore

#Material properties

class PROP_decal(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="Enabled", description="Whether this decal slot is enabled", update=update_ui)# type: ignore
    texture: bpy.props.StringProperty(name="Texture", description="The texture for the decal", default="", subtype='FILE_PATH', update=update_ui)# type: ignore
    is_normal: bpy.props.BoolProperty(name="Normal", description="Whether the decal is a normal map decal", default=False, update=update_ui)# type: ignore

    projected: bpy.props.BoolProperty(name="Projected", description="Whether the decal's UVs are projected, independant of the base UVs'", update=update_ui)# type: ignore
    tile_ratio: bpy.props.FloatProperty(name="Tile Ratio", description="The ratio of the decal's tiling to the base texture's tiling", default=1.0)# type: ignore
    scale_x: bpy.props.FloatProperty(name="Scale X", description="The scale of the decal in the x direction", default=1.0)# type: ignore
    scale_y: bpy.props.FloatProperty(name="Scale Y", description="The scale of the decal in the y direction", default=1.0)# type: ignore

    dither_ratio: bpy.props.FloatProperty(name="Dither Ratio", description="How much the alpha of the decal modulates the alpha of the base. Probably want this at 0 in a facade...")# type: ignore

    strength_constant: bpy.props.FloatProperty(name="RGB Strength Constant", description="How strong the RGB decal always is", default=1.0)# type: ignore
    strength_modulator: bpy.props.FloatProperty(name="RGB Strength Modulator", description="How strong the effect of the keying or modulator texture is on RGB decal's application", default=0.0)# type: ignore

    strength_key_red: bpy.props.FloatProperty(name="Red key for RGB Decal", description="The red key for the RGB decal key", default=0.0)# type: ignore
    strength_key_green: bpy.props.FloatProperty(name="Green key for RGB Decal", description="The green key for the RGB decal key", default=0.0)# type: ignore
    strength_key_blue: bpy.props.FloatProperty(name="Blue key for RGB Decal", description="The blue key for the RGB decal key", default=0.0)# type: ignore
    strength_key_alpha: bpy.props.FloatProperty(name="Alpha key for RGB Decal", description="The alpha key for the RGB decal key", default=0.0)# type: ignore

    strength2_constant: bpy.props.FloatProperty(name="Alpha Strength Constant", description="How strong the alpha decal always is", default=1.0)# type: ignore
    strength2_modulator: bpy.props.FloatProperty(name="Alpha Strength Modulator", description="How strong the effect of the keying or modulator texture is on alpha decal's application", default=0.0)# type: ignore

    strength2_key_red: bpy.props.FloatProperty(name="Red key for Alpha Decal", description="The red key for the alpha decal key", default=0.0)# type: ignore
    strength2_key_green: bpy.props.FloatProperty(name="Green key for Alpha Decal", description="The green key for the alpha decal key", default=0.0)# type: ignore
    strength2_key_blue: bpy.props.FloatProperty(name="Blue key for Alpha Decal", description="The blue key for the alpha decal key", default=0.0)# type: ignore
    strength2_key_alpha: bpy.props.FloatProperty(name="Alpha key for Alpha Decal", description="The alpha key for the alpha decal key", default=0.0)# type: ignore

    #Internals
    is_ui_expanded: bpy.props.BoolProperty(name="Expanded", description="Whether the decal is expanded in the UI", default=False, update=update_ui) # type: ignore

class PROP_mats(bpy.types.PropertyGroup):
    #Properties for the material:
    # - Alb texture - String
    # - Normal texture - String
    # - Lit textures - String
    # - Draped - Bool
    # - Hard - Bool
    # - Blend alpha - bool
    # - Polygon offset - int

    #Internal state properties
    was_draped_last_update: bpy.props.BoolProperty(
        name="Was Draped Last Update",
        default=False
    ) # type: ignore

    was_separate_material_texture_last_update: bpy.props.BoolProperty(
        name="Was separate Material Texture Last Update",
        default=False
    ) # type: ignore

    was_programmatically_updated: bpy.props.BoolProperty(
        name="Was Programmatically Updated",
        default=False
    ) # type: ignore

    alb_texture: bpy.props.StringProperty(
        name="Albedo Texture",
        description="The albedo texture",
        default="",
        subtype='FILE_PATH',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    material_texture: bpy.props.StringProperty(
        name="Material Texture",
        description="The material texture",
        default="",
        subtype='FILE_PATH',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    do_separate_material_texture: bpy.props.BoolProperty(
        name="Use separate Material Texture",
        description="Whether to use a separate material texture for the material",
        default=False,
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

    weather_texture: bpy.props.StringProperty(
        name="Weather Texture",
        description="The texture used to control weather effects",
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

    surface_type: bpy.props.EnumProperty(
        name="Surface Type",
        description="The surface type of the material",
        items=collision_type_enum,
        default="NONE",
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    surface_is_deck: bpy.props.BoolProperty(
        name="Surface is Deck",
        description="Is the surface a deck you can fly under, or solid all the way to the ground?",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    layer_group: bpy.props.EnumProperty(
        name="Layer Group",
        description="The layer group of the material",
        items=layer_group_enum,
        default='OBJECTS',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    layer_group_offset: bpy.props.IntProperty(
        name="Layer Group Offset",
        description="The layer group offset of the material",
        default=0,
        min=-5,
        max=5,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    camera_collision_enabled: bpy.props.BoolProperty(
        name="Camera Collision",
        description="Does the material have hard camera collision?",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    drawing_enabled: bpy.props.BoolProperty(
        name="Drawing Enabled",
        description="Is the material drawing enabled?",
        default=True,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    use_2d_panel_texture: bpy.props.BoolProperty(
        name="Use 2D Panel Texture",
        description="Whether to use the 2D panel texture for the material. LEGACY USE ONLY",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    panel_texture_region: bpy.props.IntProperty(
        name="Panel Texture Region",
        description="The region of the 2D panel texture to use for the material. LEGACY USE ONLY",
        default=0,
        min=0,
        max=4,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    cockpit_device: bpy.props.EnumProperty(
        name="Cockpit Device Name",
        description="The cockpit device name for the material",
        items=[
            ('NONE', "None", "No cockpit device"),
            ('GNS430_1', "GNS430_1", "GNS430_1"),
            ('GNS430_2', "GNS430_2", "GNS430_2"),
            ('GNS530_1', "GNS530_1", "GNS530_1"),
            ('GNS530_2', "GNS530_2", "GNS530_2"),
            ('CDU739_1', "CDU739_1", "CDU739_1"),
            ('CDU739_2', "CDU739_2", "CDU739_2"),
            ('G1000_PFD1', "G1000_PFD1", "G1000_PFD1"),
            ('G1000_PFD2', "G1000_PFD2", "G1000_PFD2"),
            ('G1000_MFD', "G1000_MFD", "G1000_MFD"),
            ('MCDU_1', "MCDU_1", "MCDU_1"),
            ('MCDU_2', "MCDU_2", "MCDU_2"),
            ('Primus_RMU_1', "Primus_RMU_1", "Primus_RMU_1"),
            ('Primus_RMU_2', "Primus_RMU_2", "Primus_RMU_2"),
            ('Primus_PFD_1', "Primus_PFD_1", "Primus_PFD_1"),
            ('Primus_PFD_2', "Primus_PFD_2", "Primus_PFD_2"),
            ('Primus_MFD_1', "Primus_MFD_1", "Primus_MFD_1"),
            ('Primus_MFD_2', "Primus_MFD_2", "Primus_MFD_2"),
            ('Primus_MFD_3', "Primus_MFD_3", "Primus_MFD_3"),
            ('Plugin Device', "Custom", "Custom Plugin Drawn Device")
        ],
        default='NONE',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    custom_cockpit_device: bpy.props.StringProperty(
        name="Custom Cockpit Device",
        description="The custom cockpit device name for the material",
        default="",
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    cockpit_device_use_bus_1: bpy.props.BoolProperty(name="Use Bus 1", description="Whether the cockpit device uses bus 1", default=False, update=material_config.operator_wrapped_update_settings) # type: ignore
    cockpit_device_use_bus_2: bpy.props.BoolProperty(name="Use Bus 2", description="Whether the cockpit device uses bus 2", default=False, update=material_config.operator_wrapped_update_settings) # type: ignore
    cockpit_device_use_bus_3: bpy.props.BoolProperty(name="Use Bus 3", description="Whether the cockpit device uses bus 3", default=False, update=material_config.operator_wrapped_update_settings) # type: ignore
    cockpit_device_use_bus_4: bpy.props.BoolProperty(name="Use Bus 4", description="Whether the cockpit device uses bus 4", default=False, update=material_config.operator_wrapped_update_settings) # type: ignore
    cockpit_device_use_bus_5: bpy.props.BoolProperty(name="Use Bus 5", description="Whether the cockpit device uses bus 5", default=False, update=material_config.operator_wrapped_update_settings) # type: ignore
    cockpit_device_use_bus_6: bpy.props.BoolProperty(name="Use Bus 6", description="Whether the cockpit device uses bus 6", default=False, update=material_config.operator_wrapped_update_settings) # type: ignore

    cockpit_device_lighting_channel: bpy.props.IntProperty(
        name="Rheostat Lighting Channel",
        description="The lighting channel for the cockpit device",
        default=0,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    blend_mode: bpy.props.EnumProperty(
        name="Blend Mode",
        description="The blend mode of the material",
        items=[
            ('CLIP', "Alpha Clip", "Alpha is clipped at the cutoff value"),
            ('BLEND', "Alpha Blend", "Alpha is blended"),
            ('SHADOW', "Alpha Blend, Shadow Clip", "Alpha is blended, shadows are clipped")
        ],
        default='BLEND',
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

    use_transparent_blending: bpy.props.BoolProperty(
        name="Use Transparent Blending",
        description="Enables special X-Plane transparency blending mode. Applies to entire object. Requires XP 12.2.1+. Translates to ATTR_layer_group blended",
        default=False,
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

    light_level_override: bpy.props.BoolProperty(
        name="Light Level Override",
        description="Whether the material overrides the light level",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    light_level_v1: bpy.props.FloatProperty(
        name="Light Level Value 1",
        description="Dataref value for no light",
        default=0.0,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    light_level_v2: bpy.props.FloatProperty(
        name="Light Level Value 2",
        description="Dataref value for full light",
        default=0.0,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    light_level_dataref: bpy.props.StringProperty(
        name="Light Level Dataref",
        description="The dataref to use for the light level override",
        default="",
        subtype='NONE',
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    light_level_photometric: bpy.props.BoolProperty(
        name="Photometric Light Level",
        description="Whether the light level override is photometric",
        default=False,
        update=material_config.operator_wrapped_update_settings
    ) # type: ignore

    light_level_brightness: bpy.props.IntProperty(
        name="Light Level Brightness",
        description="The brightness of the light level override in candelas",
        default=1,
        min=0,
        max=65535,
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

    #Decal properties. Currently XP only supports 2 alb and 2 nml decals. However in the future this may change
    #So, rather than hardcode decal_one etc, we use a collection property. in update_settings we will set it to always have 4 items, with 2 being alb and 2 being nml
    decals: bpy.props.CollectionProperty(
        type=PROP_decal,
        name="Decals",
        description="The decals for the material, aka detail textures."
    ) # type: ignore

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

#Polygon properties

class PROP_pol_collection(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", description="The name of the polygon layer") # type: ignore
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the polygon is exportable", default=False) # type: ignore
    is_ui_expanded: bpy.props.BoolProperty(name="UI Expanded", description="Whether the polygon is expanded in the UI", default=False, update=update_ui) # type: ignore
    
    texture_is_nowrap: bpy.props.BoolProperty(name="Non-tiling textures", description="Whether the texture can tile or not", default=False) # type: ignore

    is_load_centered: bpy.props.BoolProperty(name="Enable Load Center", description="Whether the polygon uses location base texture scaling", default=False) # type: ignore
    load_center_lat: bpy.props.FloatProperty(name="Load Center Latitude", description="The latitude used for texture scaling", default=0.0) # type: ignore
    load_center_lon: bpy.props.FloatProperty(name="Load Center Longitude", description="The longitude used for texture scaling", default=0.0) # type: ignore
    load_center_resolution: bpy.props.IntProperty(name="Load Center Resolution", description="The resolution used for texture scaling", default=4096) # type: ignore
    load_center_size: bpy.props.FloatProperty(name="Load Center Size", description="The size used for texture scaling", default=1000) # type: ignore

    is_texture_tiling: bpy.props.BoolProperty(name="Enable Texture Tiling", description="Whether the polygon uses texture tiling", default=False) # type: ignore
    texture_tiling_x_pages: bpy.props.IntProperty(name="Texture Tiling X Pages", description="The number of pages in the x direction", default=1) # type: ignore
    texture_tiling_y_pages: bpy.props.IntProperty(name="Texture Tiling Y Pages", description="The number of pages in the y direction", default=1) # type: ignore
    texture_tiling_map_x_res: bpy.props.IntProperty(name="Texture Tiling Map X Resolution", description="The resolution of the texture tiling map in the x direction", default=4096) # type: ignore
    texture_tiling_map_y_res: bpy.props.IntProperty(name="Texture Tiling Map Y Resolution", description="The resolution of the texture tiling map in the y direction", default=4096) # type: ignore
    texture_tiling_map_texture: bpy.props.StringProperty(name="Texture Tiling Map Texture", description="The texture used for the texture tiling map", default="", subtype="FILE_PATH") # type: ignore

    is_runway_markings: bpy.props.BoolProperty(name="LR Runway Markings (Advanced)", description="Whether the polygon uses runway markings. These can only be used for polygons used by X-Plane runways, which currently are only default polygons", default=False) # type: ignore
    runway_markings_r: bpy.props.FloatProperty(name="Runway Markings Red", description="The red value for the runway markings", default=1.0) # type: ignore
    runway_markings_g: bpy.props.FloatProperty(name="Runway Markings Green", description="The green value for the runway markings", default=1.0) # type: ignore
    runway_markings_b: bpy.props.FloatProperty(name="Runway Markings Blue", description="The blue value for the runway markings", default=1.0) # type: ignore
    runway_markings_a: bpy.props.FloatProperty(name="Runway Markings Alpha", description="The alpha value for the runway markings", default=1.0) # type: ignore
    runway_markings_texture: bpy.props.StringProperty(name="Runway Markings Texture", description="The texture used for the runway markings", default="", subtype="FILE_PATH") # type: ignore

#Autogen Point Properties

class PROP_agp_obj(bpy.types.PropertyGroup):
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the object is exportable", default=False) # type: ignore
    type: bpy.props.EnumProperty(
        name="Type",
        description="The of object this is in the autogen point",
        items=[
            ('BASE_TILE', "Base Tile", "The base tile for the autogen point"),
            ('ATTACHED_OBJ', "Attached Object", "An attached object to the parent tile"),
            ('FACADE', "Facade", "A facade perimeter"),
            ('TREE', "Tree", "A tree object randomly picked from the set layer from the .agp's forest asset"),
            ('TREE_LINE', "Tree Line", "A tree line object randomly picked from the set layer from the .agp's forest asset"),
            ('CROP_POLY', "Crop Polygon", "A polygon used to crop the shape of the parent tile"),
            ('AUTO_SPLIT_OBJ', "Auto Split Object", "An empty whose children will be automatically split by material, exported as separate objects, and attached here in the .agp"),
        ],
        default='BASE_TILE'
    ) # type: ignore

    attached_obj_draped: bpy.props.BoolProperty(
        name="Draped",
        description="Whether the attached object is draped",
        default=False
    ) # type: ignore

    attached_obj_resource: bpy.props.StringProperty(
        name="Resource",
        description="The resource for the attached object",
        default=""
    ) # type: ignore

    attached_obj_show_between_low: bpy.props.IntProperty(
        name="Show Between Low",
        description="The lowest setting this obj will start to show at",
        default=0,
        min=0,
        max=6
    ) # type: ignore

    attached_obj_show_between_high: bpy.props.IntProperty(
        name="Show Between High",
        description="The setting this obj will always show at",
        default=0,
        min=0,
        max=6
    ) # type: ignore

    facade_resource: bpy.props.StringProperty(
        name="Facade Resource",
        description="The resource for the facade",
        default=""
    ) # type: ignore

    facade_height: bpy.props.FloatProperty(
        name="Facade Height",
        description="The height of the facade",
        default=10.0
    ) # type: ignore

    tree_layer: bpy.props.IntProperty(
        name="Tree Layer",
        description="The layer for the tree",
        default=0
    ) # type: ignore

    autosplit_obj_name: bpy.props.StringProperty(
        name="Autosplit Object Name",
        description="The name of the autosplit object. If present, this will be used in the name of the autosplit objects (_PT_<name>_<material name>)",
        default=""
    ) # type: ignore

    autosplit_do_fake_lods: bpy.props.BoolProperty(
        name="Fake LODs",
        description="Whether to add objects of a fixed size to all LODs of the autosplit object for consistent LOD behavior",
        default=False
    ) # type: ignore

    autosplit_fake_lods_size: bpy.props.FloatProperty(
        name="Fake LODs Size",
        description="The size of the fake LODs for the autosplit object. This is the size of the bounding box of the fake LODs",
        default=100.0,
        min=1.0
    ) # type: ignore

    #Autosplit lod settings
    autosplit_lod_count: bpy.props.IntProperty(name="Autosplit LOD Count", description="The number of LODs to use for autosplit objects", default=0, min=0, max=4) # type: ignore
    autosplit_lod_1_min: bpy.props.FloatProperty(name="Autosplit LOD 1 Min Distance", description="The minimum distance for the first LOD of autosplit objects", default=0.0, min=0.0) # type: ignore
    autosplit_lod_1_max: bpy.props.FloatProperty(name="Autosplit LOD 1 Max Distance", description="The maximum distance for the first LOD of autosplit objects", default=0.0, min=0.0) # type: ignore
    autosplit_lod_2_min: bpy.props.FloatProperty(name="Autosplit LOD 2 Min Distance", description="The minimum distance for the second LOD of autosplit objects", default=0.0, min=0.0) # type: ignore
    autosplit_lod_2_max: bpy.props.FloatProperty(name="Autosplit LOD 2 Max Distance", description="The maximum distance for the second LOD of autosplit objects", default=0.0, min=0.0) # type: ignore
    autosplit_lod_3_min: bpy.props.FloatProperty(name="Autosplit LOD 3 Min Distance", description="The minimum distance for the third LOD of autosplit objects", default=0.0, min=0.0) # type: ignore
    autosplit_lod_3_max: bpy.props.FloatProperty(name="Autosplit LOD 3 Max Distance", description="The maximum distance for the third LOD of autosplit objects", default=0.0, min=0.0) # type: ignore
    autosplit_lod_4_min: bpy.props.FloatProperty(name="Autosplit LOD 4 Min Distance", description="The minimum distance for the fourth LOD of autosplit objects", default=0.0, min=0.0) # type: ignore
    autosplit_lod_4_max: bpy.props.FloatProperty(name="Autosplit LOD 4 Max Distance", description="The maximum distance for the fourth LOD of autosplit objects", default=0.0, min=0.0) # type: ignore

class PROP_agp_collection(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", description="The name of the autogen point collection") # type: ignore
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the autogen point collection is exportable", default=False) # type: ignore
    is_ui_expanded: bpy.props.BoolProperty(name="UI Expanded", description="Whether the autogen point collection is expanded in the UI", default=False, update=update_ui) # type: ignore

    is_texture_tiling: bpy.props.BoolProperty(name="Enable Texture Tiling", description="Whether the polygon uses texture tiling", default=False) # type: ignore
    texture_tiling_x_pages: bpy.props.IntProperty(name="Texture Tiling X Pages", description="The number of pages in the x direction", default=1) # type: ignore
    texture_tiling_y_pages: bpy.props.IntProperty(name="Texture Tiling Y Pages", description="The number of pages in the y direction", default=1) # type: ignore
    texture_tiling_map_x_res: bpy.props.IntProperty(name="Texture Tiling Map X Resolution", description="The resolution of the texture tiling map in the x direction", default=4096) # type: ignore
    texture_tiling_map_y_res: bpy.props.IntProperty(name="Texture Tiling Map Y Resolution", description="The resolution of the texture tiling map in the y direction", default=4096) # type: ignore
    texture_tiling_map_texture: bpy.props.StringProperty(name="Texture Tiling Map Texture", description="The texture used for the texture tiling map", default="", subtype="FILE_PATH") # type: ignore

    vegetation_asset: bpy.props.StringProperty(name="Vegetation Asset", description="The asset to use for the vegetation in the autogen point collection", default="", update=update_ui) # type: ignore

    render_tiles: bpy.props.BoolProperty(name="Render Tile", description="Whether the tile is rendered", default=True, update=update_ui) # type: ignore
    tile_lod: bpy.props.IntProperty(name="Tile LOD", description="The LOD for the tile", default=20000, min=0) # type: ignore

#Facade properties

class PROP_fac_mesh(bpy.types.PropertyGroup):
    far_lod: bpy.props.IntProperty(name="Far LOD", description="The far LOD for the object", default=1000)  # type: ignore
    group: bpy.props.IntProperty(name="Group", description="The group for the object. Use for layering transparency") # type: ignore
    cuts: bpy.props.IntProperty(name="Segments", description="The number of segments in the mesh (used for curves. If it is a flat plane with 3 subdivisions, you have 4 segments)")   # type: ignore
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the object is exportable", default=True) # type: ignore

class PROP_fac_filtered_spelling_choices(bpy.types.PropertyGroup):
    collection: bpy.props.StringProperty(name="Name")  #type: ignore

class PROP_fac_spelling(bpy.types.PropertyGroup):
    is_ui_expanded: bpy.props.BoolProperty(name="UI Expanded", description="Whether the spelling is expanded in the UI", default=False, update=update_ui)# type: ignore
    entries: bpy.props.CollectionProperty(type=PROP_fac_filtered_spelling_choices)# type: ignore

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
    roof_collection: bpy.props.StringProperty(name="Name")  #type: ignore
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
    bpy.utils.register_class(PROP_pol_collection)
    bpy.utils.register_class(PROP_lin_layer)
    bpy.utils.register_class(PROP_lin_collection)
    bpy.utils.register_class(PROP_agp_obj)
    bpy.utils.register_class(PROP_agp_collection)
    bpy.utils.register_class(PROP_xp_ext_scene)
    bpy.utils.register_class(PROP_decal)
    bpy.utils.register_class(PROP_mats)
    bpy.utils.register_class(PROP_attached_obj)
    bpy.utils.register_class(PROP_fac_mesh)
    bpy.utils.register_class(PROP_fac_spelling)
    bpy.utils.register_class(PROP_fac_wall)
    bpy.utils.register_class(PROP_fac_floor)
    bpy.utils.register_class(PROP_facade)
    

    bpy.types.Object.xp_lin = bpy.props.PointerProperty(type=PROP_lin_layer)
    bpy.types.Object.xp_attached_obj = bpy.props.PointerProperty(type=PROP_attached_obj)
    bpy.types.Object.xp_agp = bpy.props.PointerProperty(type=PROP_agp_obj)
    bpy.types.Object.xp_fac_mesh = bpy.props.PointerProperty(type=PROP_fac_mesh)
    bpy.types.Collection.xp_pol = bpy.props.PointerProperty(type=PROP_pol_collection)
    bpy.types.Collection.xp_lin = bpy.props.PointerProperty(type=PROP_lin_collection)
    bpy.types.Collection.xp_fac = bpy.props.PointerProperty(type=PROP_facade)
    bpy.types.Collection.xp_agp = bpy.props.PointerProperty(type=PROP_agp_collection)
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
    del bpy.types.Collection.xp_pol
    del bpy.types.Collection.xp_agp
    del bpy.types.Object.xp_fac_mesh
    del bpy.types.Object.xp_attached_obj
    del bpy.types.Object.xp_lin
    del bpy.types.Object.xp_agp

    bpy.utils.unregister_class(PROP_facade)
    bpy.utils.unregister_class(PROP_fac_floor)
    bpy.utils.unregister_class(PROP_fac_wall)
    bpy.utils.unregister_class(PROP_fac_spelling)
    bpy.utils.unregister_class(PROP_fac_mesh)
    bpy.utils.unregister_class(PROP_mats)
    bpy.utils.unregister_class(PROP_decal)
    bpy.utils.unregister_class(PROP_xp_ext_scene)
    bpy.utils.unregister_class(PROP_pol_collection)
    bpy.utils.unregister_class(PROP_lin_collection)
    bpy.utils.unregister_class(PROP_agp_obj)
    bpy.utils.unregister_class(PROP_agp_collection)
    bpy.utils.unregister_class(PROP_lin_layer)
    bpy.utils.unregister_class(PROP_attached_obj)
    bpy.utils.unregister_class(PROP_fac_filtered_spelling_choices)