#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      6/1/2025
#Module:    xp_for.py
#Purpose:   Provide a class that defines the X-Plane forest type

from ..Helpers import file_utils
from ..Helpers import forest_geometry_utils
from ..Helpers import decal_utils
from ..Helpers import for_utils
from ..Helpers.misc_utils import ftos
from ..Helpers import decal_utils

import bpy
import os

class TreeMesh():
    def __init__(self):
        self.near_lod = 0
        self.far_lod = 1000
        self.no_shadow = False
        self.wind_bend_ratio = 0.0
        self.branch_bending = 1.0
        self.max_wind_speed = 1.0
        self.verticies : list[forest_geometry_utils.for_xp_vertex] = []
        self.indicies : list[int] = []
        self.mesh_name : str = ""
    
    def from_obj(self, in_obj : bpy.types.Object):
        xp_for = in_obj.xp_for
        self.near_lod = xp_for.near_lod
        self.far_lod = xp_for.far_lod
        self.no_shadow = xp_for.no_shadow
        self.wind_bend_ratio = xp_for.wind_bend_ratio
        self.branch_bending = xp_for.branch_bending
        self.max_wind_speed = xp_for.max_wind_speed
        self.verticies, self.indicies = forest_geometry_utils.get_draw_call_from_obj(in_obj)
        self.mesh_name = in_obj.name
        self.mesh_name = self.mesh_name.replace(" " "-")

    def to_obj(self, in_name : str):
        obj = forest_geometry_utils.create_obj_from_draw_call(self.verticies, self.indicies, in_name)
        obj.xp_for.near_lod = self.near_lod
        obj.xp_for.far_lod = self.far_lod
        obj.xp_for.no_shadow = self.no_shadow
        obj.xp_for.wind_bend_ratio = self.wind_bend_ratio
        obj.xp_for.branch_bending = self.branch_bending
        obj.xp_for.max_wind_speed = self.max_wind_speed
        return obj

    def to_string(self):
        out = f"MESH {self.mesh_name} {self.near_lod} {self.far_lod} {len(self.verticies)} {len(self.indicies)} {self.wind_bend_ratio} {self.branch_bending} {self.max_wind_speed}\n"
        if self.no_shadow:
            out += "NO_SHADOW\n"
        for vert in self.verticies:
            out += f"VERTEX {ftos(vert.loc_x, 8)} {ftos(vert.loc_z, 8)} {ftos(vert.loc_y, 8)} {ftos(vert.normal_x, 8)} {ftos(vert.normal_z, 8)} {ftos(vert.normal_y, 8)} {ftos(vert.uv_x, 8)} {ftos(vert.uv_y, 8)} {ftos(vert.stiffness, 8)} {ftos(vert.edge_stiffness, 8)} {ftos(vert.phase, 8)}\n"
        #TODO: Is this index printing logic correct?
        for i in range(0, len(self.indicies), 10):
            out += f"IDX {self.indicies[i]} {self.indicies[i+1]} {self.indicies[i+2]} {self.indicies[i+3]} {self.indicies[i+4]} {self.indicies[i+5]} {self.indicies[i+6]} {self.indicies[i+7]} {self.indicies[i+8]} {self.indicies[i+9]}\n"
        for i in range(0, len(self.indicies) % 10):
            out += f"IDX {self.indicies[len(self.indicies) / 10 + i]}"

    def from_lines(self, lines : list[str]):
        for line in lines:
            if line.startswith("MESH"):
                tokens = line.split()
                if len(tokens) < 9:
                    raise Exception(f"MESH command must have at least 9 tokens, has {len(tokens)}")
                self.mesh_name = tokens[1]
                self.near_lod = float(tokens[2])
                self.far_lod = float(tokens[3])
                self.wind_bend_ratio = float(tokens[6])
                self.branch_bending = float(tokens[7])
                self.max_wind_speed = float(tokens[8])
            elif line.startswith("VERTEX"):
                tokens = line.split()
                if len(tokens) < 12:
                    raise Exception(f"MESH command must have at least 9 tokens, has {len(tokens)}")
                vert = forest_geometry_utils.for_xp_vertex()
                vert.loc_x = tokens[1]
                vert.loc_y = tokens[3]
                vert.loc_z = tokens[2]
                vert.normal_x = tokens[4]
                vert.normal_y = tokens[6]
                vert.normal_z = tokens[5]
                vert.uv_x = tokens[7]
                vert.uv_y = tokens[8]
                vert.stiffness = tokens[9]
                vert.edge_stiffness = tokens[10]
                vert.phase = tokens[11]
            elif line.startswith("IDX"):
                tokens = line.split()
                if len(tokens) < 2:
                    raise Exception("IDX must be followed by one or more indicies")
                for i in range(1, len(tokens)):
                    self.indicies.append(int(float(tokens[i])))


class Tree():
    def __init__(self):
        self.meshes : list[TreeMesh] = []
        self.weight_choice = 1.0
        self.min_tree_height = 0.5
        self.normal_height = 0.0
        self.max_tree_height = 1.0
        self.base_height = 1.0
        self.use_custom_lod = False
        self.custom_lod = 1000
        self.group = 0

        self.quad_x = 0.0
        self.quad_y = 0.0
        self.quad_width = 1.0
        self.quad_height = 1.0
        self.quad_center_offset = 0.5
        self.frequency = 1.0    #The docs for tree say these must add up to 100%, but the existing X-Plane exporter indicates this is an arbitrary weight. I'm inclined to go with the later as it matches other X-Plane behavior
        self.quads = 2 #Always 2
        self.layer = 0  #Trees are stored in lists based on their layer, but this is *also* stored in the tree command
        self.name = ""  #Arbitrary string to make trees easier to identify if reading the file by hand
        # Meshes are a bit weird, we create them seperately then reference them by name.
        # Good for VRAM savings if you can share meshes, but we need to reference them.
        # Because of Blender's unique name enforcement however, these will be resolved and meshes made real
        # during the read phase when importing, and will stay real during the whole right phase
        self.mesh_names : list[str] = []

    def from_obj(self, in_obj : bpy.types.Object, layer : int):
        #TODO: We need a helper to extract the quad data, including the base height

        #Copy the basic params
        xp_for = in_obj.xp_for
        self.layer = layer
        self.name = in_obj.name
        self.weight_choice = xp_for.weight_choice
        self.min_tree_height = xp_for.min_tree_height
        self.max_tree_height = xp_for.max_tree_height
        self.use_custom_lod = xp_for.use_custom_lod
        self.custom_lod = xp_for.custom_lod
        self.group = xp_for.group
        
        for child in in_obj.children:
            if child.type == "MESH":
                if for_utils.is_forest_quad_obj(child):
                    qd = for_utils.get_forest_quad_from_obj(child)
                    self.quad_x = qd.left_x
                    self.quad_y = qd.bottom_y
                    self.quad_width = qd.width
                    self.quad_height = qd.height
                    self.quad_center_offset = qd.offset_to_center
                    self.normal_height = qd.height_meters
                else:
                    new_mesh = TreeMesh()
                    new_mesh.from_obj(child)
                    self.meshes.append(new_mesh)
                    self.mesh_names.append(child.name)

    def to_obj(self, target_collection : bpy.types.Collection):
        obj = bpy.data.objects.new(self.name, None)
        obj.type = "EMPTY"
        obj.empty_display_type = "ARROWS"

        #Link the object to the collection and view layer
        target_collection.objects.link(obj)
        
        #TODO: We need a helper to create a quad from the data

        #Copy the basic params
        obj.xp_for.weight_choice = self.weight_choice
        obj.xp_for.min_tree_height = self.min_tree_height
        obj.xp_for.max_tree_height = self.max_tree_height
        obj.xp_for.use_custom_lod = self.use_custom_lod
        obj.xp_for.custom_lod = self.custom_lod
        obj.xp_for.group = self.group

        #Create the mesh objects
        for mesh in self.meshes:
            new_obj = mesh.to_obj(self.name + "_mesh")
            target_collection.objects.link(new_obj)

        #Create the quad object
        qd = for_utils.TreeQuad()
        qd.left_x = self.quad_x
        qd.bottom_y = self.quad_y
        qd.width = self.quad_width
        qd.height = self.quad_height
        qd.offset_to_center = self.quad_center_offset
        qd.height_meters = self.base_height
        qd_obj = for_utils.create_obj_from_forest_quad(qd, 1.0) #TODO: Get this ratio from the texture
        target_collection.objects.link(qd_obj)

    def to_string(self, res_x : int, res_y : int):
        #TREE2  <s1> <t1> <w> <h> <sw> <percent> <min_height> <max_height> <nominal_height> <lod_far> <quads> <type> <notes>
        out = f"TREE2 {self.quad_x * res_x} {self.quad_y * res_y} {self.quad_width * res_x} {self.quad_height * res_y} {self.quad_center_offset * res_x} {self.frequency} {self.min_tree_height} {self.max_tree_height} {self.base_height} {self.custom_lod} {self.quads} {self.layer} {self.name}\n"

        #Add references to the 3d meshess
        for mn in self.mesh_names:
            out += f"MESH_3D {mn}"

        return out

    def from_lines(self, lines : list[str], res_x : int, res_y : int, all_meshes : list[TreeMesh]):
        for line in lines:
            if line.startswith("TREE2"):
                tokens = line.split()
                if len(tokens) < 13:
                    raise Exception("TREE2 command must have at least 12 arguments!")
                self.quad_x = float(tokens[1]) * res_x
                self.quad_y = float(tokens[2]) * res_y
                self.quad_width = float(tokens[3]) * res_x
                self.quad_height = float(tokens[4]) * res_y
                self.quad_center_offset = float(tokens[5]) * res_x
                self.frequency = float(tokens[6])
                self.min_tree_height = float(tokens[7])
                self.max_tree_height = float(tokens[8])
                self.base_height = float(tokens[9]) #I don't think this is used anywhere when reading
                self.custom_lod = float(tokens[10])
                self.quads = 2  #Because it's always 2
                self.layer = int(float(tokens[12]))
                if len(tokens) >= 14:
                    self.name = str.join(" ", tokens[13:])
                else:
                    self.name = "Imported Tree"
            elif line.startswith("MESH_3D"):
                tokens = line.split()
                if len(tokens) < 2:
                    raise Exception("MESH_3D command must have at least 1 argument")
                for mesh in all_meshes:
                    if mesh.mesh_name == tokens[1]:
                        self.meshes.append(mesh)

class ForestMaterial():
    def __init__(self):
        self.alb_texture = ""
        self.lit_texture = ""
        self.nml_texture = ""
        self.mod_texture = ""
        self.weather_texture = ""
        self.layer = "objects"
        self.layer_offset = 0
        self.blend_cutoff = 0   #Clip level for 
        self.blend_mode = "CLIP"    #Can be SHADOW, BLEND, CLIP, or HASH (hash is like dither)
        self.mat_mode = "NORMAL_METALNESS"  #Can be NONE, NORMAL_METALNESS, or NORMAL_TRANSLUCENT
        self.decals = []
        self.imported_decal_commands = []

    def from_material(self, in_material : bpy.types.Material):
        mat = in_material.xp_materials
        self.alb_texture = file_utils.to_relative(mat.alb_texture)
        self.lit_texture = file_utils.to_relative(mat.lit_texture)
        self.nml_texture = file_utils.to_relative(mat.normal_texture)
        self.mod_texture = file_utils.to_relative(mat.modulator_texture)
        self.layer = mat.layer_group
        self.layer_offset = mat.layer_group_offset
        self.mat_mode = "NORMAL_METALNESS"  #TODO: Add a mod selector to material properties
        self.blend_cutoff = mat.blend_cutoff
        self.blend_mode = mat.blend_mode
        self.decals = mat.decals
        
    def to_material(self, in_material : bpy.types.Material):
        mat = in_material.xp_materials
        mat.alb_texture = self.alb_texture
        mat.lit_texture = self.lit_texture
        mat.normal_texture = self.nml_texture
        mat.modulator_texture = self.mod_texture
        mat.layer_group = self.layer
        mat.layer_group_offset = self.layer_offset
        mat.blend_cutoff = self.blend_cutoff
        mat.blend_mode = self.blend_mode
        mat.decals = self.decals

    def to_string(self, output_folder : str):
        out = ""
        
        #TODO: When this gets merged into main, change this to use the file_utils.is_empty check
        if self.alb_texture != "":
            out += f"TEXTURE {os.path.relpath(file_utils.to_absolute(self.alb_texture), output_folder)}\n"
        if self.nml_texture != "":
            out += f"TEXTURE_NORMAL {os.path.relpath(file_utils.to_absolute(self.nml_texture), output_folder)}\n"
        if self.lit_texture != "":
            out += f"TEXTURE_LIT {os.path.relpath(file_utils.to_absolute(self.lit_texture), output_folder)}\n"
        if self.mod_texture != "":
            out += f"TEXTURE_MODULATOR {os.path.relpath(file_utils.to_absolute(self.mod_texture), output_folder)}\n"
        
        out += f"LAYER_GROUP {self.layer} {self.layer_offset}"

        if self.mat_mode == "NORMAL_METALNESS":
            out += "NORMAL_METALNESS\n"
        elif self.mat_mode == "NORMAL_TRANSLUCENCY":
            out += "NORMAL_TRANSLUCENCY"
        
        if self.blend_mode == "CLIP":
            out += f"NO_BLEND {self.blend_cutoff}"
        if self.blend_cutoff == "HASHED":
            out += f"ALPHA_HASHED"
        
        for dcl in self.decals:
            out += decal_utils.get_decal_command(dcl, output_folder)

    def from_lines(self, lines : list[str]):
        for line in lines:
            if line.startswith("TEXTURE"):
                tokens = line.split(maxsplit=1)
                if len(tokens) > 1:
                    self.alb_texture = file_utils.to_relative(tokens[1], True)
            elif line.startswith("TEXTURE_NORMAL"):
                tokens = line.split(maxsplit=1)
                if len(tokens) > 1:
                    self.nml_texture = file_utils.to_relative(tokens[1], True)
            elif line.startswith("TEXTURE_LIT"):
                tokens = line.split(maxsplit=1)
                if len(tokens) > 1:
                    self.lit_texture = file_utils.to_relative(tokens[1], True)
            elif line.startswith("TEXTURE_MODULATOR"):
                tokens = line.split(maxsplit=1)
                if len(tokens) > 1:
                    self.mod_texture = file_utils.to_relative(tokens[1], True)
            elif line.startswith("LAYER_GROUP"):
                tokens = line.split()
                if len(tokens) >= 3:
                    self.layer = tokens[1]
                    self.layer_offset = int(tokens[2])
            elif line.startswith("NORMAL_METALNESS"):
                self.mat_mode = "NORMAL_METALNESS"
            elif line.startswith("NORMAL_TRANSLUCENCY"):
                self.mat_mode = "NORMAL_TRANSLUCENCY"
            elif line.startswith("NO_BLEND"):
                tokens = line.split()
                self.blend_mode = "CLIP"
                if len(tokens) >= 2:
                    self.blend_cutoff = int(tokens[1])
            elif line.startswith("ALPHA_HASHED"):
                self.blend_mode = "HASHED"

class Forest():
    def __init__(self):
        self.name = ""

        self.mat_2d : ForestMaterial | None = None
        self.mat_3d : ForestMaterial | None = None

        self.do_seasons = False

        self.mat_spring_2d : ForestMaterial | None = None
        self.mat_spring_3d : ForestMaterial | None = None

        self.mat_summer_2d : ForestMaterial | None = None
        self.mat_summer_3d : ForestMaterial | None = None

        self.mat_fall_2d : ForestMaterial | None = None
        self.mat_fall_3d : ForestMaterial | None = None

        self.mat_winter_2d : ForestMaterial | None = None
        self.mat_winter_3d : ForestMaterial | None = None

        self.spacing_x = 1.0
        self.spacing_y = 1.0
        self.random_x = 1.0
        self.random_y = 1.0

        self.cast_shadws = True
        
        self.density_params = False
        self.density_wavelength_0 = 0
        self.density_wavestrength_0 = 0
        self.density_wavelength_1 = 0
        self.density_wavestrength_1 = 0
        self.density_wavelength_2 = 0
        self.density_wavestrength_2 = 0
        self.density_wavelength_3 = 0
        self.density_wavestrength_3 = 0

        self.choice_params = False
        self.choice_wavelength_0 = 0
        self.choice_wavestrength_0 = 0
        self.choice_wavelength_1 = 0
        self.choice_wavestrength_1 = 0
        self.choice_wavelength_2 = 0
        self.choice_wavestrength_2 = 0
        self.choice_wavelength_3 = 0
        self.choice_wavestrength_3 = 0

        self.height_params = False
        self.height_wavelength_0 = 0
        self.height_wavestrength_0 = 0
        self.height_wavelength_1 = 0
        self.height_wavestrength_1 = 0
        self.height_wavelength_2 = 0
        self.height_wavestrength_2 = 0
        self.height_wavelength_3 = 0
        self.height_wavestrength_3 = 0

        self.layers : list[list[Tree]] = []

    def from_collection(self, in_collection : bpy.types.Collection):
        #Copy the properties from the collections .xp_for property group into our local copy
        # If a material is None in the PG, leave it as none here
        
        props = in_collection.xp_for_collection
        
        self.name = props.name
        self.spacing_x = props.spacing_x
        self.spacing_y = props.spacing_y
        self.random_x = props.random_x
        self.random_y = props.random_y
        self.cast_shadws = props.cast_shadow
        self.do_seasons = props.has_seasons
        
        # Handle 2D and 3D materials
        if props.has_seasons:
            if props.spring_material_2d:
                self.mat_spring_2d = ForestMaterial()
                self.mat_spring_2d.from_material(props.spring_material_2d)
            if props.spring_material_3d:
                self.mat_spring_3d = ForestMaterial()
                self.mat_spring_3d.from_material(props.spring_material_3d)
            if self.mat_spring_2d is None and self.mat_spring_3d is not None:
                self.mat_spring_2d = self.mat_spring_3d
            elif self.mat_spring_3d is None and self.mat_spring_2d is not None:
                self.mat_spring_3d = self.mat_spring_2d
            
            if props.summer_material_2d:
                self.mat_summer_2d = ForestMaterial()
                self.mat_summer_2d.from_material(props.summer_material_2d)
            if props.summer_material_3d:
                self.mat_summer_3d = ForestMaterial()
                self.mat_summer_3d.from_material(props.summer_material_3d)
            if self.mat_summer_2d is None and self.mat_summer_3d is not None:
                self.mat_summer_2d = self.mat_summer_3d
            elif self.mat_summer_3d is None and self.mat_summer_2d is not None:
                self.mat_summer_3d = self.mat_summer_2d
            
            if props.fall_material_2d:
                self.mat_fall_2d = ForestMaterial()
                self.mat_fall_2d.from_material(props.fall_material_2d)
            if props.fall_material_3d:
                self.mat_fall_3d = ForestMaterial()
                self.mat_fall_3d.from_material(props.fall_material_3d)
            if self.mat_fall_2d is None and self.mat_fall_3d is not None:
                self.mat_fall_2d = self.mat_fall_3d
            elif self.mat_fall_3d is None and self.mat_fall_2d is not None:
                self.mat_fall_3d = self.mat_fall_2d
            
            if props.winter_material_2d:
                self.mat_winter_2d = ForestMaterial()
                self.mat_winter_2d.from_material(props.winter_material_2d)
            if props.winter_material_3d:
                self.mat_winter_3d = ForestMaterial()
                self.mat_winter_3d.from_material(props.winter_material_3d)
            if self.mat_winter_2d is None and self.mat_winter_3d is not None:
                self.mat_winter_2d = self.mat_winter_3d
            elif self.mat_winter_3d is None and self.mat_winter_2d is not None:
                self.mat_winter_3d = self.mat_winter_2d
        
        #TODO: If there are no seasons, auto detect the materials from the meshes. We need the rest of the forst infrastructure written first though
        
        # Handle density parameters
        self.density_params = props.density_params
        self.density_wavelength_0 = props.density_0_length
        self.density_wavestrength_0 = props.density_0_value
        self.density_wavelength_1 = props.density_1_length
        self.density_wavestrength_1 = props.density_1_value
        self.density_wavelength_2 = props.density_2_length
        self.density_wavestrength_2 = props.density_2_value
        self.density_wavelength_3 = props.density_3_length
        self.density_wavestrength_3 = props.density_3_value
        
        # Handle choice parameters
        self.choice_params = props.choice_params
        self.choice_wavelength_0 = props.choice_0_length
        self.choice_wavestrength_0 = props.choice_0_value
        self.choice_wavelength_1 = props.choice_1_length
        self.choice_wavestrength_1 = props.choice_1_value
        self.choice_wavelength_2 = props.choice_2_length
        self.choice_wavestrength_2 = props.choice_2_value
        self.choice_wavelength_3 = props.choice_3_length
        self.choice_wavestrength_3 = props.choice_3_value
        
        # Handle height parameters
        self.height_params = props.height_params
        self.height_wavelength_0 = props.height_0_length
        self.height_wavestrength_0 = props.height_0_value
        self.height_wavelength_1 = props.height_1_length
        self.height_wavestrength_1 = props.height_1_value
        self.height_wavelength_2 = props.height_2_length
        self.height_wavestrength_2 = props.height_2_value
        self.height_wavelength_3 = props.height_3_length
        self.height_wavestrength_3 = props.height_3_value

        #Get the layers of trees
        sorted_child_collections : list[bpy.types.Collection] = []
        for child in in_collection.children:
            sorted_child_collections.append(child)
        sorted_child_collections.sort()

        for i, child in enumerate(sorted_child_collections):
            self.layers.append([])
            for obj in child.objects:
                if obj.type == "MESH":
                    new_tree = Tree()
                    new_tree.from_obj(obj, i)
                    self.layers[-1].append(new_tree)

    def to_collection(self):
        #First create a new collection
        col = bpy.data.collections.new(self.name)
        props = col.xp_for_collection

        #Now copy over all the collection level settings
        props.spacing_x = self.spacing_x
        props.spacing_y = self.spacing_y
        props.random_x = self.random_x
        props.random_y = self.random_y
        props.cast_shadow = self.cast_shadws
        props.has_seasons = self.do_seasons
        
        # Handle materials
        if self.do_seasons:
            #Ensure that if we have a season in *either* the 2d or the 3d, both are populated for that season
            if self.mat_spring_2d is None and self.mat_spring_3d is not None:
                self.mat_spring_2d = self.mat_spring_3d
            elif self.mat_spring_3d is None and self.mat_spring_2d is not None:
                self.mat_spring_3d = self.mat_spring_2d

            if self.mat_summer_2d is None and self.mat_summer_3d is not None:
                self.mat_summer_2d = self.mat_summer_3d
            elif self.mat_summer_3d is None and self.mat_summer_2d is not None:
                self.mat_summer_3d = self.mat_summer_2d
            
            if self.mat_fall_2d is None and self.mat_fall_3d is not None:
                self.mat_fall_2d = self.mat_fall_3d
            elif self.mat_fall_3d is None and self.mat_fall_2d is not None:
                self.mat_fall_3d = self.mat_fall_2d

            if self.mat_winter_2d is None and self.mat_winter_3d is not None:
                self.mat_winter_2d = self.mat_winter_3d
            elif self.mat_winter_3d is None and self.mat_winter_2d is not None:
                self.mat_winter_3d = self.mat_winter_2d

            if self.mat_spring_2d:
                # Create a new material for spring 2D
                mat_spring_2d = bpy.data.materials.new("Spring_2D")
                self.mat_spring_2d.to_material(mat_spring_2d)
                props.spring_material_2d = mat_spring_2d
            
            if self.mat_spring_3d:
                mat_spring_3d = bpy.data.materials.new("Spring_3D")
                self.mat_spring_3d.to_material(mat_spring_3d)
                props.spring_material_3d = mat_spring_3d
            
            if self.mat_summer_2d:
                mat_summer_2d = bpy.data.materials.new("Summer_2D")
                self.mat_summer_2d.to_material(mat_summer_2d)
                props.summer_material_2d = mat_summer_2d
            
            if self.mat_summer_3d:
                mat_summer_3d = bpy.data.materials.new("Summer_3D")
                self.mat_summer_3d.to_material(mat_summer_3d)
                props.summer_material_3d = mat_summer_3d
            
            if self.mat_fall_2d:
                mat_fall_2d = bpy.data.materials.new("Fall_2D")
                self.mat_fall_2d.to_material(mat_fall_2d)
                props.fall_material_2d = mat_fall_2d
            
            if self.mat_fall_3d:
                mat_fall_3d = bpy.data.materials.new("Fall_3D")
                self.mat_fall_3d.to_material(mat_fall_3d)
                props.fall_material_3d = mat_fall_3d
            
            if self.mat_winter_2d:
                mat_winter_2d = bpy.data.materials.new("Winter_2D")
                self.mat_winter_2d.to_material(mat_winter_2d)
                props.winter_material_2d = mat_winter_2d
            
            if self.mat_winter_3d:
                mat_winter_3d = bpy.data.materials.new("Winter_3D")
                self.mat_winter_3d.to_material(mat_winter_3d)
                props.winter_material_3d = mat_winter_3d
        else:
            if self.mat_2d:
                mat_2d = bpy.data.materials.new("Material_2D")
                self.mat_2d.to_material(mat_2d)
                props.summer_material_2d = mat_2d
            
            if self.mat_3d:
                mat_3d = bpy.data.materials.new("Material_3D")
                self.mat_3d.to_material(mat_3d)
                props.summer_material_3d = mat_3d
        
        # Handle density parameters
        props.density_params = self.density_params
        props.density_0_length = self.density_wavelength_0
        props.density_0_value = self.density_wavestrength_0
        props.density_1_length = self.density_wavelength_1
        props.density_1_value = self.density_wavestrength_1
        props.density_2_length = self.density_wavelength_2
        props.density_2_value = self.density_wavestrength_2
        props.density_3_length = self.density_wavelength_3
        props.density_3_value = self.density_wavestrength_3
        
        # Handle choice parameters
        props.choice_params = self.choice_params
        props.choice_0_length = self.choice_wavelength_0
        props.choice_0_value = self.choice_wavestrength_0
        props.choice_1_length = self.choice_wavelength_1
        props.choice_1_value = self.choice_wavestrength_1
        props.choice_2_length = self.choice_wavelength_2
        props.choice_2_value = self.choice_wavestrength_2
        props.choice_3_length = self.choice_wavelength_3
        props.choice_3_value = self.choice_wavestrength_3
        
        # Handle height parameters
        props.height_params = self.height_params
        props.height_0_length = self.height_wavelength_0
        props.height_0_value = self.height_wavestrength_0
        props.height_1_length = self.height_wavelength_1
        props.height_1_value = self.height_wavestrength_1
        props.height_2_length = self.height_wavelength_2
        props.height_2_value = self.height_wavestrength_2
        props.height_3_length = self.height_wavelength_3
        props.height_3_value = self.height_wavestrength_3
        
        #Now add the trees
        for i, layer in enumerate(self.layers):
            layer_col = bpy.data.collections.new("Forest layer " + i)
            col.children.link(layer_col)
            for t in layer:
                t.to_obj(layer_col)
                

        return col
