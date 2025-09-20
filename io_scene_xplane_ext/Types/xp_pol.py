#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    XP_Pol
#Purpose:   Provide a class that defines the X-Plane polygon type

#Include decal params from our material plugin
from ..Helpers import pol_utils #type: ignore
from ..Helpers import decal_utils #type: ignore
from ..Helpers import file_utils #type: ignore
from ..Helpers import misc_utils #type: ignore
from ..Helpers import geometery_utils
from ..Helpers import log_utils #type: ignore
from .. import material_config #type: ignore
import bpy #type: ignore
import os

class polygon():
    def __init__(self):
        self.name = ""
        self.nowrap = False
        self.alb_texture = ""
        self.lit_texture = ""
        self.nml_texture = ""
        self.mod_texture = ""
        self.weather_texture = ""
        self.layer = "MARKINGS"
        self.layer_offset = 0
        self.scale_x = 0.0
        self.scale_y = 0.0
        self.normal_scale = 1
        self.blend_cutoff = 0
        self.do_blend = False
        self.super_rough = False
        self.decals = []
        self.imported_decal_commands = []
        self.surface = "NONE"

        self.do_load_center = False
        self.load_center_lat = 0
        self.load_center_lon = 0
        self.load_center_size = 0
        self.load_center_res = 0

        self.do_tiling = False
        self.tiling_x_pages = 0
        self.tiling_y_pages = 0
        self.tiling_map_x_res = 0
        self.tiling_map_y_res = 0
        self.tiling_map_texture = ""

        self.do_runway_markings = False
        self.runway_r = 0
        self.runway_g = 0
        self.runway_b = 0
        self.runway_a = 0
        self.runway_marking_texture = ""

        self.do_runway_noise = False

        self.subtextures = [[]] #List of arrays of 4 values (translating to left, bottom, right, top, UVs)

    def write(self, output_path):
        log_utils.new_section(f"Writing .pol {output_path}")

        output_folder = os.path.dirname(output_path)

        #Define a string to hold the file contents
        of = ""

        of += "A\n850\nDRAPED_POLYGON\n\n"

        #Write the material data
        of += "#Materials\n"

        if self.nowrap:
            if self.alb_texture != "":
                of += "TEXTURE_NOWRAP " + os.path.relpath(file_utils.to_absolute(self.alb_texture), output_folder) + "\n"
            if self.lit_texture != "":
                of += "TEXTURE_LIT_NOWRAP " + os.path.relpath(file_utils.to_absolute(self.lit_texture), output_folder) + "\n"
            if self.nml_texture != "":
                of += "TEXTURE_NORMAL " + str(self.normal_scale) + "\t" + os.path.relpath(file_utils.to_absolute(self.nml_texture), output_folder) + "\n"
        else:
            if self.alb_texture != "":
                of += "TEXTURE " + os.path.relpath(file_utils.to_absolute(self.alb_texture), output_folder) + "\n"
            if self.lit_texture != "":
                of += "TEXTURE_LIT " + os.path.relpath(file_utils.to_absolute(self.lit_texture), output_folder) + "\n"
            if self.nml_texture != "":
                of += "TEXTURE_NORMAL " + str(self.normal_scale) + "\t" + os.path.relpath(file_utils.to_absolute(self.nml_texture), output_folder) + "\n"
            if self.weather_texture != "":
                of += "WEATHER " + os.path.relpath(file_utils.to_absolute(self.weather_texture), output_folder) + "\n"
            else:
                of += "WEATHER_TRANSPARENT\n"
        
        if self.mod_texture != "":
                of += "TEXTURE_MODULATOR " + os.path.relpath(file_utils.to_absolute(self.mod_texture), output_folder) + "\n"
        
        if self.super_rough:
            of += "SUPER_ROUGHNESS\n"

        if not self.do_blend:
            of += "NO_BLEND " + misc_utils.ftos(self.blend_cutoff, 2) + "\n"
        
        of += "\n"

        #Write the decals
        if len(self.decals) > 0:
            of += "#Decals\n"
            for decal in self.decals:
                #Get the decal command
                decal_command = decal_utils.get_decal_command(decal, output_folder)
                if decal_command:
                    of += decal_command

            of += "\n"

        #Write the main polygon params
        of += "LAYER_GROUP " + self.layer.lower() + " " + str(self.layer_offset) + "\n"
        of += "SCALE " + str(float(self.scale_x)) + " " + str(float(self.scale_y)) + "\n"
        if self.surface != None:
            of += "SURFACE " + self.surface + "\n"
        if self.do_load_center:
            of += "LOAD_CENTER " + misc_utils.ftos(self.load_center_lat, 8) + " " + misc_utils.ftos(self.load_center_lon, 8) + " " + str(int(self.load_center_size)) + " " + str(int(self.load_center_res)) + "\n"
        if self.do_tiling:
            of += "TEXTURE_TILE " + str(int(self.tiling_x_pages)) + " " + str(int(self.tiling_y_pages)) + " " + str(int(self.tiling_map_x_res)) + " " + str(int(self.tiling_map_y_res)) + " " + os.path.relpath(file_utils.to_absolute(self.tiling_map_texture), output_folder) + "\n"
        if self.do_runway_markings:
            of += "RUNWAY_MARKINGS " + misc_utils.ftos(self.runway_r, 4) + " " + misc_utils.ftos(self.runway_g, 4) + " " + misc_utils.ftos(self.runway_b, 4) + " " + misc_utils.ftos(self.runway_a, 4) + " " + os.path.relpath(file_utils.to_absolute(self.runway_marking_texture), output_folder) + "\n"
        if self.do_runway_noise:
            of += "RUNWAY_NOISE\n"

        of += "\n"

        #Write subtextures
        if len(self.subtextures) > 0:
            of += "#Subtextures\n"
        for subtexture in self.subtextures:
            if len(subtexture) != 4:
                continue

            #Write the subtexture
            of += "#subtex " + misc_utils.ftos(subtexture[0], 4) + " " + misc_utils.ftos(subtexture[1], 4) + " " + misc_utils.ftos(subtexture[2], 4) + " " + misc_utils.ftos(subtexture[3], 4) + "\n"

        #Open the output file and write the contents
        with open(output_path, 'w') as f:
            f.write(of)

    def read(self, in_file):
        log_utils.new_section(f"Reading .pol {in_file}")

        self.name = in_file.split(os.sep)[-1]

        # Read the file
        with open(in_file, 'r') as f:
            lines = f.readlines()

        # Now we need to parse the file
        for line in lines:
            # Get the line
            line = line.strip()

            tokens = line.split()
            if not tokens:
                continue

            # Defensive: check token count for each command before using tokens
            cmd = tokens[0]
            min_tokens = {
                'TEXTURE_NOWRAP': 2,
                'TEXTURE_LIT_NOWRAP': 2,
                'TEXTURE_NORMAL': 3,
                'TEXTURE_MODULATOR': 2,
                'TEXTURE': 2,
                'TEXTURE_LIT': 2,
                'WEATHER': 2,
                'SUPER_ROUGHNESS': 1,
                'NO_BLEND': 2,
                'LAYER_GROUP': 2, # can be 2 or 3, but 2 is safe
                'SCALE': 3,
                'SURFACE': 2,
                'LOAD_CENTER': 5,
                'TEXTURE_TILE': 6,
                'RUNWAY_MARKINGS': 6,
                'RUNWAY_NOISE': 1,
                '#subtex': 5,
            }
            if cmd in min_tokens and len(tokens) < min_tokens[cmd]:
                log_utils.warning(f"Not enough tokens for command '{cmd}'! Expected at least {min_tokens[cmd]}, got {len(tokens)}. Line: '{line}'")
                continue

            # Check for material data
            if cmd == "TEXTURE_NOWRAP":
                self.nowrap = True
                self.alb_texture = tokens[1]
            elif cmd == "TEXTURE_LIT_NOWRAP":
                self.nowrap = True
                self.lit_texture = tokens[1]
            elif cmd == "TEXTURE_NORMAL":
                self.nml_texture = tokens[2]
                self.normal_scale = float(tokens[1])
            elif cmd == "TEXTURE":
                self.alb_texture = tokens[1]
            elif cmd == "TEXTURE_LIT":
                self.lit_texture = tokens[1]
            elif cmd == "TEXTURE_MODULATOR":
                self.mod_texture = tokens[1]
            elif cmd == "WEATHER" and cmd != "WEATHER_TRANSPARENT":
                self.weather_texture = tokens[1]
            elif cmd == "SUPER_ROUGHNESS":
                self.super_rough = True
            elif cmd == "NO_BLEND":
                self.do_blend = False
                self.blend_cutoff = float(tokens[1])

            #Check for decals
            if cmd.startswith("DECAL") or cmd.startswith("NORMAL_DECAL"):
                self.imported_decal_commands.append(line)

            # Check for main polygon params
            elif cmd == "LAYER_GROUP":
                self.layer = tokens[1].upper()
                if len(tokens) > 2:
                    self.layer_offset = tokens[2]
            elif cmd == "SCALE":
                self.scale_x = float(tokens[1])
                self.scale_y = float(tokens[2])
            elif cmd == "SURFACE":
                self.surface = tokens[1]
                self.surface = self.surface.upper()
            elif cmd == "LOAD_CENTER":
                self.do_load_center = True
                self.load_center_lat = float(tokens[1])
                self.load_center_lon = float(tokens[2])
                self.load_center_size = float(tokens[3])
                self.load_center_res = float(tokens[4])
            elif cmd == "TEXTURE_TILE":
                self.do_tiling = True
                self.tiling_x_pages = float(tokens[1])
                self.tiling_y_pages = float(tokens[2])
                self.tiling_map_x_res = float(tokens[3])
                self.tiling_map_y_res = float(tokens[4])
                self.tiling_map_texture = tokens[5]
            elif cmd == "RUNWAY_MARKINGS":
                self.do_runway_markings = True
                self.runway_r = float(tokens[1])
                self.runway_g = float(tokens[2])
                self.runway_b = float(tokens[3])
                self.runway_a = float(tokens[4])
                self.runway_marking_texture = tokens[5]
            elif cmd == "RUNWAY_NOISE":
                self.do_runway_noise = True
            elif cmd == "#subtex":
                # Get the subtexture values
                subtexture = tokens[1:]
                if len(subtexture) != 4:
                    continue

                # Convert to float and append to the list
                subtexture = [float(i) for i in subtexture]
                self.subtextures.append(subtexture)

    def from_collection(self, in_collection):
        log_utils.new_section(f"Reading .pol collection {in_collection.name}")

        # Check if the collection is exportable
        if not in_collection.xp_pol.exportable:
            return
        
        #Make sure there are objects in the collection
        if len(in_collection.objects) == 0:
            log_utils.error(f"Collection {in_collection.name} has no objects to export as a polygon.")
            return

        # Set nowrap property
        self.nowrap = in_collection.xp_pol.texture_is_nowrap

        # Set load center properties
        self.do_load_center = in_collection.xp_pol.is_load_centered
        self.load_center_lat = in_collection.xp_pol.load_center_lat
        self.load_center_lon = in_collection.xp_pol.load_center_lon
        self.load_center_size = in_collection.xp_pol.load_center_size
        self.load_center_res = in_collection.xp_pol.load_center_resolution

        # Set texture tiling properties
        self.do_tiling = in_collection.xp_pol.is_texture_tiling
        self.tiling_x_pages = in_collection.xp_pol.texture_tiling_x_pages
        self.tiling_y_pages = in_collection.xp_pol.texture_tiling_y_pages
        self.tiling_map_x_res = in_collection.xp_pol.texture_tiling_map_x_res
        self.tiling_map_y_res = in_collection.xp_pol.texture_tiling_map_y_res
        self.tiling_map_texture = in_collection.xp_pol.texture_tiling_map_texture

        # Set runway markings properties
        self.do_runway_markings = in_collection.xp_pol.is_runway_markings
        self.do_runway_noise = in_collection.xp_pol.is_runway_markings  #This is automatic if you need runway markings. I believe XP requires this. We just use the same values as default to keep the sim happy. Idk if it actually does antyhing in sim
        self.runway_r = in_collection.xp_pol.runway_markings_r
        self.runway_g = in_collection.xp_pol.runway_markings_g
        self.runway_b = in_collection.xp_pol.runway_markings_b
        self.runway_a = in_collection.xp_pol.runway_markings_a
        self.runway_marking_texture = in_collection.xp_pol.runway_markings_texture

        #Get the material from the first mesh object in the collection
        mat = None
        for obj in in_collection.objects:
            if obj.type == 'MESH':
                #Check if it has a material
                if len(obj.data.materials) > 0:
                    #Get the first material
                    mat = obj.data.materials[0]
                    break

        if mat is None:
            log_utils.error(f"Collection {in_collection.name} has no mesh objects with materials to export as a polygon.")
            return

        # Extract material data
        mat = mat.xp_materials

        if mat.do_separate_material_texture:
            log_utils.error(f"Collection {in_collection.name} has a material with separate textures. This is not supported for polygons.")
            return

        self.alb_texture = mat.alb_texture
        self.lit_texture = mat.lit_texture
        self.nml_texture = mat.normal_texture
        self.weather_texture = mat.weather_texture
        self.mod_texture = mat.decal_modulator
        self.do_blend = mat.blend_mode == 'BLEND'
        self.blend_cutoff = mat.blend_cutoff
        for decal in mat.decals:
            self.decals.append(decal)
        self.surface = mat.surface_type
        self.layer = mat.layer_group
        self.layer_offset = mat.layer_group_offset

        #Iterate over the objects in this collection. We will use the dimensions of the biggest to set the scale
        max_x = 0
        max_y = 0

        for obj in in_collection.objects:
            if obj.type == 'MESH':
                #Get the dimensions of the object
                x = obj.dimensions.x
                y = obj.dimensions.y

                #Check if this is the biggest object so far
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

        #Set the scale based on the biggest object
        self.scale_x = max_x
        self.scale_y = max_y

        #Now we need to extract subtextures
        for obj in in_collection.objects:
            if obj.type == 'MESH':
                #Make sure it's smaller than the largest
                if obj.dimensions.x < max_x and obj.dimensions.y < max_y:
                    #Get the UVs (left right bottom top)
                    uvs = pol_utils.get_uv_bounds(obj)

                    #Convert this to the subtexture format (left bottom right top), and save
                    subtexture = [uvs[0], uvs[2], uvs[1], uvs[3]]
                    self.subtextures.append(subtexture)

    def to_scene(self):
        log_utils.new_section(f"Creating .pol collection {self.name}")

        in_name = self.name

        # Define a new collection with the same name as the file
        new_collection = bpy.data.collections.new(name=in_name)
        bpy.context.scene.collection.children.link(new_collection)

        # Create a new material for the polygon
        mat = bpy.data.materials.new(name=in_name)
        material_config.update_settings(mat)
        mat.xp_materials.alb_texture = self.alb_texture
        mat.xp_materials.lit_texture = self.lit_texture
        mat.xp_materials.normal_texture = self.nml_texture
        mat.xp_materials.weather_texture = self.weather_texture
        mat.xp_materials.decal_modulator = self.mod_texture
        mat.xp_materials.blend_mode = 'BlEND' if self.do_blend else 'CLIP'
        mat.xp_materials.blend_cutoff = self.blend_cutoff
        mat.xp_materials.surface_type = self.surface
        mat.xp_materials.layer_group = self.layer.upper()
        mat.xp_materials.layer_group_offset = int(self.layer_offset)

        decal_alb_index = 0
        decal_nml_index = 2

        for decal in self.imported_decal_commands:
            if decal.startswith("NORMAL"):
                if decal_nml_index > 3:
                    log_utils.warning("Error: Too many normal decals! X-Plane only supports 3 decals per material.")
                    break
                decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_nml_index])
                decal_nml_index += 1
            else:
                if decal_alb_index > 2:
                    log_utils.warning("Error: Too many decals! X-Plane only supports 3 decals per material.")
                    break
                decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_alb_index])
                decal_alb_index += 1

        # Set collection properties
        new_collection.xp_pol.exportable = True
        new_collection.xp_pol.texture_is_nowrap = self.nowrap
        new_collection.xp_pol.is_load_centered = self.do_load_center
        new_collection.xp_pol.load_center_lat = self.load_center_lat
        new_collection.xp_pol.load_center_lon = self.load_center_lon
        new_collection.xp_pol.load_center_size = self.load_center_size
        new_collection.xp_pol.load_center_resolution = int(self.load_center_res)
        new_collection.xp_pol.is_texture_tiling = self.do_tiling
        new_collection.xp_pol.texture_tiling_x_pages = int(self.tiling_x_pages)
        new_collection.xp_pol.texture_tiling_y_pages = int(self.tiling_y_pages)
        new_collection.xp_pol.texture_tiling_map_x_res = int(self.tiling_map_x_res)
        new_collection.xp_pol.texture_tiling_map_y_res = int(self.tiling_map_y_res)
        new_collection.xp_pol.texture_tiling_map_texture = self.tiling_map_texture
        new_collection.xp_pol.is_runway_markings = self.do_runway_markings
        new_collection.xp_pol.runway_markings_r = self.runway_r
        new_collection.xp_pol.runway_markings_g = self.runway_g
        new_collection.xp_pol.runway_markings_b = self.runway_b
        new_collection.xp_pol.runway_markings_a = self.runway_a
        new_collection.xp_pol.runway_markings_texture = self.runway_marking_texture

        #Get rid of any subtextures that don't have 4 values. This is a safety check.
        self.subtextures = [subtexture for subtexture in self.subtextures if len(subtexture) == 4]

        #Sort the subtextures by area (largest to smallest). This lets us layer them nicer so they're all visible.
        self.subtextures.sort(key=lambda x: (x[2] - x[0]) * (x[3] - x[1]), reverse=True)

        #Generate the base object
        if True:    #So we can collapse this code
            v1 = geometery_utils.xp_vertex(
                loc_x=0,
                loc_y=0,
                loc_z=0,
                normal_x=0,
                normal_y=0,
                normal_z=1,
                uv_x=0,
                uv_y=0
            )

            v2 = geometery_utils.xp_vertex(
                loc_x=0,
                loc_y=self.scale_y,
                loc_z=0,
                normal_x=0,
                normal_y=0,
                normal_z=1,
                uv_x=0, 
                uv_y=1
            )

            v3 = geometery_utils.xp_vertex(
                loc_x=self.scale_x,
                loc_y=self.scale_y,
                loc_z=0,
                normal_x=0,
                normal_y=0,
                normal_z=1,
                uv_x=1,
                uv_y=1
            )

            v4 = geometery_utils.xp_vertex(
                loc_x=self.scale_x,
                loc_y=0,
                loc_z=0,
                normal_x=0,
                normal_y=0,
                normal_z=1,
                uv_x=1,
                uv_y=0
            )

            indicies = [2, 1, 0, 3, 2, 0]
            new_obj = geometery_utils.create_obj_from_draw_call([v1, v2, v3, v4], indicies, new_collection.name)
            new_obj.data.materials.append(mat)

            #Link the new object to the collection
            new_collection.objects.link(new_obj)

        # Generate objects for subtextures
        for i, subtexture in enumerate(self.subtextures):

            v1 = geometery_utils.xp_vertex(
                loc_x=subtexture[0] * self.scale_x,
                loc_y=subtexture[1] * self.scale_y,
                loc_z=1 + (float(i) * 0.01),
                normal_x=0,
                normal_y=0,
                normal_z=1,
                uv_x=subtexture[0],
                uv_y=subtexture[1]
            )

            v2 = geometery_utils.xp_vertex(
                loc_x=subtexture[0] * self.scale_x,
                loc_y=subtexture[3] * self.scale_y,
                loc_z=1 + (float(i) * 0.01),
                normal_x=0,
                normal_y=0,
                normal_z=1,
                uv_x=subtexture[0],
                uv_y=subtexture[3]
            )

            v3 = geometery_utils.xp_vertex(
                loc_x=subtexture[2] * self.scale_x,
                loc_y=subtexture[3] * self.scale_y,
                loc_z=1 + (float(i) * 0.01),
                normal_x=0,
                normal_y=0,
                normal_z=1,
                uv_x=subtexture[2],
                uv_y=subtexture[3]
            )

            v4 = geometery_utils.xp_vertex(
                loc_x=subtexture[2] * self.scale_x,
                loc_y=subtexture[1] * self.scale_y,
                loc_z=1 + (float(i) * 0.01),
                normal_x=0,
                normal_y=0,
                normal_z=1,
                uv_x=subtexture[2],
                uv_y=subtexture[1]
            )

            indicies = [2, 1, 0, 3, 2, 0]

            new_obj = geometery_utils.create_obj_from_draw_call([v1, v2, v3, v4], indicies, new_collection.name + "_subtexture")
            new_obj.data.materials.append(mat)
            new_collection.objects.link(new_obj)
