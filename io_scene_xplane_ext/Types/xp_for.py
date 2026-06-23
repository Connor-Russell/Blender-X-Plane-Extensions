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
from ..Helpers import log_utils


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
        self.verticies, self.indicies = forest_geometry_utils.get_for_draw_call_from_obj(in_obj)
        self.mesh_name = in_obj.name
        self.mesh_name = file_utils.sanitize_path(in_obj.name).replace(" ", "_")

    def to_obj(self, in_name : str, in_mat : bpy.types.Material):
        print("Creating mesh " + self.mesh_name + " with " + str(len(self.verticies)) + " verticies and " + str(len(self.indicies)) + " indicies")
        obj = forest_geometry_utils.create_for_obj_from_draw_call(self.verticies, self.indicies, in_name)
        obj.xp_for.near_lod = self.near_lod
        obj.xp_for.far_lod = self.far_lod
        obj.xp_for.no_shadow = self.no_shadow
        obj.xp_for.wind_bend_ratio = self.wind_bend_ratio
        obj.xp_for.branch_bending = self.branch_bending
        obj.xp_for.max_wind_speed = self.max_wind_speed
        obj.data.materials.append(in_mat)
        return obj

    def to_string(self):
        out = f"MESH {self.mesh_name} {self.near_lod} {self.far_lod} {len(self.verticies)} {len(self.indicies)} {self.wind_bend_ratio} {self.branch_bending} {self.max_wind_speed}\n"
        if self.no_shadow:
            out += "NO_SHADOW\n"
        for vert in self.verticies:
            out += f"VERTEX {ftos(vert.loc_x, 8)} {ftos(vert.loc_z, 8)} {ftos(vert.loc_y, 8)} {ftos(vert.normal_x, 8)} {ftos(vert.normal_z, 8)} {ftos(vert.normal_y, 8)} {ftos(vert.uv_x, 8)} {ftos(vert.uv_y, 8)} {ftos(vert.stiffness, 8)} {ftos(vert.edge_stiffness, 8)} {ftos(vert.phase, 8)}\n"
        i = 0
        while i < len(self.indicies) - 9:
            out += f"IDX {self.indicies[i]} {self.indicies[i+1]} {self.indicies[i+2]} {self.indicies[i+3]} {self.indicies[i+4]} {self.indicies[i+5]} {self.indicies[i+6]} {self.indicies[i+7]} {self.indicies[i+8]} {self.indicies[i+9]}\n"
            i += 10
        i = 0
        while i < len(self.indicies) % 10:
            out += f"IDX {self.indicies[int(len(self.indicies) / 10) + i]}\n"
            i += 1
        return out + "\n"


class Tree():
    def __init__(self):
        self.meshes : list[TreeMesh] = []
        self.weight_choice = 1.0
        self.min_tree_height = 0.5
        self.normal_height = 0.0
        self.max_tree_height = 1.0
        self.base_height = 1.0
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

    def from_obj(self, in_obj : bpy.types.Object, layer : int, total_weight: float):
        #Copy the basic params
        xp_for = in_obj.xp_for
        self.layer = layer
        self.name = in_obj.name
        self.frequency = (xp_for.weight_choice / total_weight) * 100
        self.min_tree_height = xp_for.min_tree_height
        self.max_tree_height = xp_for.max_tree_height
        self.custom_lod = xp_for.custom_lod
        self.group = xp_for.group
        
        
        for child in in_obj.children:
            log_utils.info("Checking child " + child.name + " of tree " + in_obj.name)
            if child.type == "MESH":
                if for_utils.is_forest_quad_obj(child):
                    log_utils.info("Found forest quad " + child.name + " for tree " + in_obj.name)
                    qd = for_utils.get_forest_quad_from_obj(child)
                    self.quad_x = qd.left_x
                    self.quad_y = qd.bottom_y
                    self.quad_width = qd.width
                    self.quad_height = qd.height
                    self.quad_center_offset = qd.offset_to_center
                    self.base_height = qd.height_meters
                else:
                    new_mesh = TreeMesh()
                    new_mesh.from_obj(child)
                    self.meshes.append(new_mesh)
                    self.mesh_names.append(file_utils.sanitize_path(child.name).replace(" ", "_"))
                    log_utils.info("Added mesh " + child.name + " to tree " + in_obj.name)

    def to_obj(self, target_collection : bpy.types.Collection, in_mat_2d : bpy.types.Material, in_mat_3d : bpy.types.Material):
        print("Creating tree " + self.name + " with " + str(len(self.meshes)) + " meshes")
        obj = bpy.data.objects.new(self.name, None)
        obj.empty_display_type = "ARROWS"

        #Link the object to the collection and view layer
        target_collection.objects.link(obj)
        
        #TODO: We need a helper to create a quad from the data

        #Copy the basic params
        obj.xp_for.weight_choice = self.weight_choice
        obj.xp_for.min_tree_height = self.min_tree_height
        obj.xp_for.max_tree_height = self.max_tree_height
        obj.xp_for.custom_lod = self.custom_lod
        obj.xp_for.group = self.group

        #Create the mesh objects
        for mesh in self.meshes:
            new_obj = mesh.to_obj(self.name + "_mesh", in_mat_3d)
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
        qd_obj.parent = obj
        qd_obj.data.materials.append(in_mat_2d)

    def to_string(self, res_x : int, res_y : int):
        #TREE2  <s1> <t1> <w> <h> <sw> <percent> <min_height> <max_height> <nominal_height> <lod_far> <quads> <type> <notes>
        out = f"TREE2 {self.quad_x * res_x} {self.quad_y * res_y} {self.quad_width * res_x} {self.quad_height * res_y} {self.quad_center_offset * res_x} {self.frequency} {self.min_tree_height} {self.max_tree_height} {self.base_height} {self.custom_lod} {self.quads} {self.layer} {self.name}\n"

        #Add references to the 3d meshess
        for mn in self.mesh_names:
            out += f"MESH_3D {mn}\n"

        return out


class ForestMaterial():
    def __init__(self):
        self.alb_texture = ""
        self.lit_texture = ""
        self.nml_texture = ""
        self.mod_texture = ""
        self.weather_texture = ""
        self.blend_cutoff = 0   #Clip level for 
        self.blend_mode = "CLIP"    #Can be SHADOW, BLEND, CLIP, or HASH (hash is like dither)
        self.mat_mode = "NORMAL_METALNESS"  #Can be NONE, NORMAL_METALNESS, or NORMAL_TRANSLUCENT
        self.imported_decal_commands = []

    def from_material(self, in_material : bpy.types.Material):
        mat = in_material.xp_materials
        self.alb_texture = file_utils.to_relative(mat.alb_texture)
        self.lit_texture = file_utils.to_relative(mat.lit_texture)
        self.nml_texture = file_utils.to_relative(mat.normal_texture)
        self.mod_texture = file_utils.to_relative(mat.decal_modulator)
        self.mat_mode = mat.material_mode
        self.blend_cutoff = mat.blend_cutoff
        self.blend_mode = mat.blend_mode
        
    def to_material(self, in_material : bpy.types.Material):
        mat = in_material.xp_materials
        mat.alb_texture = self.alb_texture
        mat.lit_texture = self.lit_texture
        mat.normal_texture = self.nml_texture
        mat.decal_modulator = self.mod_texture
        mat.blend_cutoff = self.blend_cutoff
        mat.blend_mode = self.blend_mode

    def to_string(self, output_folder : str):
        out = ""
        
        #TODO: When this gets merged into main, change this to use the file_utils.is_empty check
        if self.alb_texture != "":
            out += f"\tTEXTURE {file_utils.to_relative(file_utils.to_absolute(self.alb_texture), False, output_folder)}\n"
        if self.nml_texture != "":
            #TECHNICALLY we could specify the normal tile ratio, the format allows it... but... *why*??? (the format does it so it's a standard parser, but I can't imagine a reason someone would use it)
            out += f"\tTEXTURE_NORMAL 1 {file_utils.to_relative(file_utils.to_absolute(self.nml_texture), False, output_folder)}\n"
        if self.lit_texture != "":
            out += f"\tTEXTURE_LIT {file_utils.to_relative(file_utils.to_absolute(self.lit_texture), False, output_folder)}\n"
        if self.mod_texture != "":
            out += f"\tTEXTURE_MODULATOR {file_utils.to_relative(file_utils.to_absolute(self.mod_texture), False, output_folder)}\n"

        if self.mat_mode == "NORMAL_METALNESS":
            out += "\tNORMAL_METALNESS\n"
        elif self.mat_mode == "NORMAL_TRANSLUCENCY":
            out += "\tNORMAL_TRANSLUCENCY\n"
        
        if self.blend_mode == "CLIP":
            out += f"\tNO_BLEND {self.blend_cutoff}\n"
        if self.blend_cutoff == "HASHED":
            out += f"\tALPHA_HASHED\n"

        return out + "\n"


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

        self.tex_scale_x = 4096
        self.tex_scale_y = 4096

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
        
        props = in_collection.xp_for
        
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
        
        all_col_objects = []
        for child in in_collection.children:
            for obj in child.objects:
                all_col_objects.append(obj)
        for obj in all_col_objects:
            if for_utils.is_forest_quad_obj(obj):
                self.mat_2d = ForestMaterial()
                self.mat_2d.from_material(obj.active_material)
            elif obj.type == "MESH":
                self.mat_3d = ForestMaterial()
                self.mat_3d.from_material(obj.active_material)

        #Make sure we have a 2d and 3d material
        if self.mat_2d is None and self.mat_3d is not None:
            self.mat_2d = self.mat_3d
        elif self.mat_3d is None and self.mat_2d is not None:
            self.mat_3d = self.mat_2d
        elif self.mat_2d is None and self.mat_3d is None:
            raise Exception("No material found for forest!")
        
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
            #Before we do the trees, we need to get the total weight per layer so we can get correct frequencies
            total_weight = 0.0
            for obj in child.objects:
                log_utils.info("Checking object " + obj.name + " in collection " + child.name + " for tree data")
                if obj.type == "EMPTY" and obj.xp_for.exportable:
                    total_weight += obj.xp_for.weight_choice

            for obj in child.objects:
                log_utils.info("Checking object " + obj.name + " in collection " + child.name + " for tree data")
                if obj.type == "EMPTY" and obj.xp_for.exportable:
                    new_tree = Tree()
                    new_tree.from_obj(obj, i, total_weight)
                    self.layers[-1].append(new_tree)

    def to_collection(self):
        #First create a new collection
        col = bpy.data.collections.new(self.name)
        bpy.context.scene.collection.children.link(col)

        props = col.xp_for

        #Now copy over all the collection level settings
        props.spacing_x = self.spacing_x
        props.spacing_y = self.spacing_y
        props.random_x = self.random_x
        props.random_y = self.random_y
        props.cast_shadow = self.cast_shadws
        props.has_seasons = self.do_seasons

        
        
        # Handle materials
        mat_2d = None
        mat_3d = None
        if self.mat_2d:
            mat_2d = bpy.data.materials.new("Material_2D")
            self.mat_2d.to_material(mat_2d)
            props.summer_material_2d = mat_2d
        
        if self.mat_3d:
            mat_3d = bpy.data.materials.new("Material_3D")
            self.mat_3d.to_material(mat_3d)
            props.summer_material_3d = mat_3d

        if mat_2d is not None and mat_3d is None:
            mat_3d = mat_2d
        elif mat_3d is not None and mat_2d is None:
            mat_2d = mat_3d

        if mat_2d is None:
            raise Exception("No material found for forest!")        
        
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
            layer_col = bpy.data.collections.new("Forest layer " + str(i))
            col.children.link(layer_col)
            for t in layer:
                t.to_obj(layer_col, mat_2d, mat_3d)
                

        return col

    def read(self, input_path: str):
        #Min token dict
        min_tokens = {
            "TEXTURE": 2,
            "TEXTURE_NORMAL": 3,
            "TEXTURE_LIT": 2,
            "TEXTURE_MODULATOR": 2,
            "LAYER_GROUP": 3,
            "NO_BLEND": 2,
            "SCALE_X": 2,
            "SCALE_Y": 2,
            "SPACING": 3,
            "RANDOM": 3,
            "DENSITY_PARAMS": 9,
            "HEIGHT_PARAMS": 9,
            "CHOICE_PARAMS": 9,
            "MESH": 9,
            "VERTEX": 12,
            "TREE2": 13,
            "TREE": 11,
            "IDX": 2,
            "MESH_3D": 2
        }

        self.name = os.path.splitext(os.path.basename(input_path))[0]

        with open(input_path, 'r') as f:
            lines = f.readlines()

        self.mat_2d = ForestMaterial()
        self.mat_3d = ForestMaterial()

        current_shader = None
        current_mesh = None
        current_tree = None
        all_meshes = []

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            tokens = line.split()
            cmd = tokens[0]

            #Get the min tokens and make sure we meet the min token threshold for this command
            if cmd in min_tokens and len(tokens) < min_tokens[cmd]:
                log_utils.warning(f"Line '{line}' does not have enough tokens for command {cmd}, skipping", f"Command {cmd} doesn't have enough tokens")
                continue

            # When in a mesh, if we get a command other than a vertex or idx, we need to end the mesh
            if current_mesh is not None and cmd not in ["VERTEX", "IDX"]:
                all_meshes.append(current_mesh)
                current_mesh = None

            # Section markers
            if cmd == "SHADER_2D":
                current_shader = "2D"
                continue
            if cmd == "SHADER_3D":
                current_shader = "3D"
                continue

            # Material commands — only apply inside SHADER_2D / SHADER_3D
            if current_shader is not None:
                mat = self.mat_2d if current_shader == "2D" else self.mat_3d
                if cmd == "TEXTURE":
                    mat.alb_texture = file_utils.to_relative(tokens[1], True)
                    continue
                if cmd == "TEXTURE_NORMAL":
                    mat.nml_texture = file_utils.to_relative(tokens[2], True)
                    continue
                if cmd == "TEXTURE_LIT":
                    mat.lit_texture = file_utils.to_relative(tokens[1], True)
                    continue
                if cmd == "TEXTURE_MODULATOR":
                    mat.mod_texture = file_utils.to_relative(tokens[1], True)
                    continue
                if cmd == "NORMAL_METALNESS":
                    mat.mat_mode = "NORMAL_METALNESS"
                    continue
                if cmd == "NORMAL_TRANSLUCENCY":
                    mat.mat_mode = "NORMAL_TRANSLUCENCY"
                    continue
                if cmd == "NO_BLEND":
                    mat.blend_mode = "CLIP"
                    if len(tokens) >= 2:
                        mat.blend_cutoff = int(float(tokens[1]))
                    continue
                if cmd == "ALPHA_HASHED":
                    mat.blend_mode = "HASHED"
                    continue

            # Global forest commands
            if cmd == "SCALE_X":
                self.tex_scale_x = int(float(tokens[1]))
            elif cmd == "SCALE_Y":
                self.tex_scale_y = int(float(tokens[1]))
            elif cmd == "SPACING":
                self.spacing_x = float(tokens[1])
                self.spacing_y = float(tokens[2])
            elif cmd == "RANDOM":
                self.random_x = float(tokens[1])
                self.random_y = float(tokens[2])
            elif cmd == "DENSITY_PARAMS":
                self.density_params = True
                self.density_wavelength_0 = float(tokens[1])
                self.density_wavestrength_0 = float(tokens[2])
                self.density_wavelength_1 = float(tokens[3])
                self.density_wavestrength_1 = float(tokens[4])
                self.density_wavelength_2 = float(tokens[5])
                self.density_wavestrength_2 = float(tokens[6])
                self.density_wavelength_3 = float(tokens[7])
                self.density_wavestrength_3 = float(tokens[8])
            elif cmd == "HEIGHT_PARAMS":
                self.height_params = True
                self.height_wavelength_0 = float(tokens[1])
                self.height_wavestrength_0 = float(tokens[2])
                self.height_wavelength_1 = float(tokens[3])
                self.height_wavestrength_1 = float(tokens[4])
                self.height_wavelength_2 = float(tokens[5])
                self.height_wavestrength_2 = float(tokens[6])
                self.height_wavelength_3 = float(tokens[7])
                self.height_wavestrength_3 = float(tokens[8])
            elif cmd == "CHOICE_PARAMS":
                self.choice_params = True
                self.choice_wavelength_0 = float(tokens[1])
                self.choice_wavestrength_0 = float(tokens[2])
                self.choice_wavelength_1 = float(tokens[3])
                self.choice_wavestrength_1 = float(tokens[4])
                self.choice_wavelength_2 = float(tokens[5])
                self.choice_wavestrength_2 = float(tokens[6])
                self.choice_wavelength_3 = float(tokens[7])
                self.choice_wavestrength_3 = float(tokens[8])

            # Mesh definition commands
            elif cmd == "MESH":
                if current_shader is None:
                    log_utils.error(f"MESH command before shaders are defined. Is this a pre X-Plane 12 forest?", "Mesh command found outside of shader block")
                if current_mesh is not None:
                    all_meshes.append(current_mesh)
                current_mesh = TreeMesh()
                current_mesh.mesh_name = tokens[1]
                current_mesh.near_lod = float(tokens[2])
                current_mesh.far_lod = float(tokens[3])
                # tokens[4] = vertex count, tokens[5] = index count (informational only)
                current_mesh.wind_bend_ratio = float(tokens[6])
                current_mesh.branch_bending = float(tokens[7])
                current_mesh.max_wind_speed = float(tokens[8])
            elif cmd == "NO_SHADOW" and current_mesh is not None:
                current_mesh.no_shadow = True
            elif cmd == "VERTEX":
                if current_mesh is None:
                    log_utils.warning(f"VERTEX command found outside of a MESH block, skipping: '{line}'")
                    continue
                # File format: VERTEX loc_x loc_z loc_y normal_x normal_z normal_y uv_x uv_y stiffness edge_stiffness phase
                vert = forest_geometry_utils.for_xp_vertex(
                    float(tokens[1]), float(tokens[3]), float(tokens[2]),
                    float(tokens[4]), float(tokens[6]), float(tokens[5]),
                    float(tokens[7]), float(tokens[8])
                )
                vert.stiffness = float(tokens[9])
                vert.edge_stiffness = float(tokens[10])
                vert.phase = float(tokens[11])
                current_mesh.verticies.append(vert)
            elif cmd == "IDX":
                if current_mesh is None:
                    log_utils.warning(f"IDX command found outside of a MESH block, skipping: '{line}'")
                    continue
                for i in range(1, len(tokens)):
                    current_mesh.indicies.append(int(float(tokens[i])))

            # Tree definition commands
            elif cmd == "TREE2":
                if current_mesh is not None:
                    all_meshes.append(current_mesh)
                    current_mesh = None
                current_tree = Tree()
                current_tree.quad_x = float(tokens[1]) / self.tex_scale_x
                current_tree.quad_y = float(tokens[2]) / self.tex_scale_y
                current_tree.quad_width = float(tokens[3]) / self.tex_scale_x
                current_tree.quad_height = float(tokens[4]) / self.tex_scale_y
                current_tree.quad_center_offset = float(tokens[5]) / self.tex_scale_x
                current_tree.frequency = float(tokens[6])
                current_tree.min_tree_height = float(tokens[7])
                current_tree.max_tree_height = float(tokens[8])
                current_tree.base_height = float(tokens[9])
                current_tree.custom_lod = float(tokens[10])
                current_tree.quads = 2
                current_tree.layer = int(float(tokens[12]))
                current_tree.name = " ".join(tokens[13:]) if len(tokens) >= 14 else "Imported Tree"
                while len(self.layers) <= current_tree.layer:
                    self.layers.append([])
                self.layers[current_tree.layer].append(current_tree)
            elif cmd == "TREE":
                if current_mesh is not None:
                    all_meshes.append(current_mesh)
                    current_mesh = None
                current_tree = Tree()
                current_tree.quad_x = float(tokens[1]) / self.tex_scale_x
                current_tree.quad_y = float(tokens[2]) / self.tex_scale_y
                current_tree.quad_width = float(tokens[3]) / self.tex_scale_x
                current_tree.quad_height = float(tokens[4]) / self.tex_scale_y
                current_tree.quad_center_offset = float(tokens[5]) / self.tex_scale_x
                current_tree.frequency = float(tokens[6])
                current_tree.min_tree_height = float(tokens[7])
                current_tree.max_tree_height = float(tokens[8])
                current_tree.quads = 2
                current_tree.layer = int(float(tokens[9]))
                current_tree.name = " ".join(tokens[10:]) if len(tokens) >= 11 else "Imported Tree"
                while len(self.layers) <= current_tree.layer:
                    self.layers.append([])
                self.layers[current_tree.layer].append(current_tree)
            elif cmd == "MESH_3D":
                if current_tree is None:
                    log_utils.warning(f"MESH_3D command found outside of a TREE block, skipping: '{line}'", "Mesh command found outside of tree block")
                    continue
                mesh_name = tokens[1]
                found_mesh = False
                for mesh in all_meshes:
                    if mesh.mesh_name == mesh_name:
                        found_mesh = True
                        current_tree.meshes.append(mesh)
                        current_tree.mesh_names.append(file_utils.sanitize_path(mesh_name).replace(" ", "_"))
                        break
                if not found_mesh:
                    log_utils.warning(f"MESH_3D command references mesh '{mesh_name}' which was not found in the file, skipping this mesh for tree '{current_tree.name}'", f"Mesh '{mesh_name}' not found for tree '{current_tree.name}'")

    def write(self, output_path : str):

        output_folder = os.path.dirname(output_path)
        log_utils.info(f"Writing forest to {output_path} with output folder {output_folder}")

        #Define a string to hold the file contents
        header = ""

        header += "A\n1200\nFOREST\n\n"

        #Write the 2D and 3D materials
        base_material = "SHADER_2D\n"
        
        base_material += self.mat_2d.to_string(output_folder)

        base_material += "SHADER_3D\n"

        base_material += self.mat_3d.to_string(output_folder)

        base_material += "\n"

        # Now we need to write the core of the file.
        # The reason we're doing this in a separate string is so if we are exporting seasons, we can simply
        # Append this string to their header
        body = ""

        body += f"SCALE_X {self.tex_scale_x}\n"
        body += f"SCALE_Y {self.tex_scale_y}\n"
        body += f"SPACING {self.spacing_x} {self.spacing_y}\n"
        body += f"RANDOM {self.random_x} {self.random_y}\n"

        if self.density_params:
            body += f"DENSITY_PARAMS {self.density_wavelength_0} {self.density_wavestrength_0} {self.density_wavelength_1} {self.density_wavestrength_1} {self.density_wavelength_2} {self.density_wavestrength_2} {self.density_wavelength_3} {self.density_wavestrength_3}"
        if self.height_params:
            body += f"HEIGHT_PARAMS {self.height_wavelength_0} {self.height_wavestrength_0} {self.height_wavelength_1} {self.height_wavestrength_1} {self.height_wavelength_2} {self.height_wavestrength_2} {self.height_wavelength_3} {self.height_wavestrength_3}"
        if self.choice_params:
            body += f"CHOICE_PARAMS {self.choice_wavelength_0} {self.choice_wavestrength_0} {self.choice_wavelength_1} {self.choice_wavestrength_1} {self.choice_wavelength_2} {self.choice_wavestrength_2} {self.choice_wavelength_3} {self.choice_wavestrength_3}"
        
        body += "\n"

        for layer in self.layers:
            for tree in layer:
                log_utils.info("Tree mesh count " + str(len(tree.meshes)))
                for mesh in tree.meshes:
                    body += mesh.to_string() + "\n"

        #Now, we sort the trees by their group variable, and write them!
        for layer in self.layers:
            if len(layer) < 1:
                continue

            #Sort
            layer.sort(key=lambda x: x.group)

            different_groups = set()
            for tree in layer:
                different_groups.add(tree.group)
            different_group_count = len(different_groups)

            #Track the group because we'll need to write a command every time the group changes
            last_group = layer[0].group
            
            for tree in layer:
                if tree.group != last_group:
                    last_group = tree.group
                    body += f"GROUP {last_group} {1.0 / different_group_count}"
                body += tree.to_string(self.tex_scale_x, self.tex_scale_y)
        
        # At this point, we have the header, the body, and the material section.
        # If we are in season mode, we just need to get the different paths and the different headrees
        # Otherwise we just write it directly
        if self.do_seasons:
            sp_path = output_path.replace(".for", "_SP.for")
            su_path = output_path.replace(".for", "_SU.for")
            fl_path = output_path.replace(".for", "_FL.for")
            wi_path = output_path.replace(".for", "_WI.for")

            if self.mat_spring_2d is not None:
                sp_material = "SHADER_2D\n"
                sp_material += self.mat_spring_2d.to_string(output_folder)
                sp_material += "SHADER_3D\n"
                sp_material += self.mat_spring_3d.to_string(output_folder)
                with open(sp_path, "w") as f:
                    f.write(header + sp_material + body)
            if self.mat_summer_2d is not None:
                su_material = "SHADER_2D\n"
                su_material += self.mat_summer_2d.to_string(output_folder)
                su_material += "SHADER_3D\n"
                su_material += self.mat_summer_3d.to_string(output_folder)
                with open(su_path, "w") as f:
                    f.write(header + su_material + body)
            if self.mat_fall_2d is not None:
                fl_material = "SHADER_2D\n"
                fl_material += self.mat_fall_2d.to_string(output_folder)
                fl_material += "SHADER_3D\n"
                fl_material += self.mat_fall_3d.to_string(output_folder)
                with open(fl_path, "w") as f:
                    f.write(header + fl_material + body)
            if self.mat_winter_2d is not None:
                wi_material = "SHADER_2D\n"
                wi_material += self.mat_winter_2d.to_string(output_folder)
                wi_material += "SHADER_3D\n"
                wi_material += self.mat_winter_3d.to_string(output_folder)
                with open(wi_path, "w") as f:
                    f.write(header + wi_material + body)
        else:
            with open(output_path, "w") as f:
                f.write(header + base_material + body)
            