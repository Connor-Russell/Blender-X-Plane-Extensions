#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Export
#Purpose:   Provide a class that defines the X-Plane line type

#Include decal params from our material plugin
from ..Helpers import pol_utils #type: ignore
from ..Helpers import decal_utils #type: ignore
from ..Helpers import file_utils #type: ignore
from ..Helpers import misc_utils #type: ignore
import bpy #type: ignore
import os

class polygon():
    def __init__(self):
        self.nowrap = False
        self.alb_texture = ""
        self.lit_texture = ""
        self.nml_texture = ""
        self.weather_texture = ""
        self.layer = "MARKINGS"
        self.layer_offset = 0
        self.scale_x = 0
        self.scale_y = 0
        self.normal_scale = 1
        self.blend_cutoff = 0
        self.do_blend = False
        self.super_rough = False
        self.decal_1 = None
        self.decal_2 = None
        self.surface = None

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
        output_folder = os.path.dirname(output_path)

        #Define a string to hold the file contents
        of = ""

        of += "A\n850\DRAPED_POLYGON\n\n"

        #Write the material data
        of += "#Materials\n"

        if self.nowrap:
            if self.alb_texture != "":
                of += "TEXTURE_NOWRAP " + os.path.relpath(file_utils.rel_to_abs(self.alb_texture), output_folder) + "\n"
            if self.lit_texture != "":
                of += "TEXTURE_LIT_NOWRAP " + os.path.relpath(file_utils.rel_to_abs(self.lit_texture), output_folder) + "\n"
            if self.nml_texture != "":
                of += "TEXTURE_NORMAL " + str(self.normal_scale) + "\t" + os.path.relpath(file_utils.rel_to_abs(self.nml_texture), output_folder) + "\n"
        else:
            if self.alb_texture != "":
                of += "TEXTURE " + os.path.relpath(file_utils.rel_to_abs(self.alb_texture), output_folder) + "\n"
            if self.lit_texture != "":
                of += "TEXTURE_LIT " + os.path.relpath(file_utils.rel_to_abs(self.lit_texture), output_folder) + "\n"
            if self.nml_texture != "":
                of += "TEXTURE_NORMAL " + str(self.normal_scale) + "\t" + os.path.relpath(file_utils.rel_to_abs(self.nml_texture), output_folder) + "\n"
            if self.weather_texture != "":
                of += "WEATHER " + os.path.relpath(file_utils.rel_to_abs(self.weather_texture), output_folder) + "\n"
            else:
                of += "WEATHER_TRANSPARENT\n"
        
        if self.super_rough:
            of += "SUPER_ROUGHNESS\n"

        if not self.do_blend:
            of += "NO_BLEND " + misc_utils.ftos(self.blend_cutoff, 2) + "\n"
        
        of += "\n"

        #Write the decals
        if self.decal_1.enabled or self.decal_2.enabled:
            of += "#Decals\n"
            if self.decal_1.enabled:
                of += decal_utils.get_decal_command(self.decal_1, output_folder)
                of += "\n"
            if self.decal_2.enabled:
                of += decal_utils.get_decal_command(self.decal_2, output_folder)
                of += "\n"
            of += "\n"

        #Write the main polygon params
        of += "LAYER_GROUP " + self.layer.lower() + " " + str(self.layer_offset) + "\n"
        of += "SCALE " + str(int(self.scale_x)) + " " + str(int(self.scale_y)) + "\n"
        if self.surface != None:
            of += "SURFACE " + self.surface + "\n"
        if self.do_load_center:
            of += "LOAD_CENTER " + str(self.load_center_lat) + " " + str(self.load_center_lon) + " " + str(self.load_center_size) + " " + str(self.load_center_res) + "\n"
        if self.do_tiling:
            of += "TEXTURE_TILE " + str(self.tiling_x_pages) + " " + str(self.tiling_y_pages) + " " + str(self.tiling_map_x_res) + " " + str(self.tiling_map_y_res) + " " + os.path.relpath(file_utils.rel_to_abs(self.tiling_map_texture), output_folder) + "\n"
        if self.do_runway_markings:
            of += "RUNWAY_MARKINGS " + str(self.runway_r) + " " + str(self.runway_g) + " " + str(self.runway_b) + " " + str(self.runway_a) + " " + os.path.relpath(file_utils.rel_to_abs(self.runway_marking_texture), output_folder) + "\n"
        if self.do_runway_noise:
            of += "RUNWAY_NOISE\n"

        of += "\n"

        #Write subtextures
        of += "\n#Subtextures\n"
        for subtexture in self.subtextures:
            if len(subtexture) != 4:
                continue

            #Write the subtexture
            of += "SUBTEXTURE " + misc_utils.ftos(subtexture[0], 4) + " " + misc_utils.ftos(subtexture[1], 4) + " " + misc_utils.ftos(subtexture[2], 4) + " " + misc_utils.ftos(subtexture[3], 4) + "\n"

        of += "\n"

        #Open the output file and write the contents
        with open(output_path, 'w') as f:
            f.write(of)

    def read(self, in_file):
        # Read the file
        with open(in_file, 'r') as f:
            lines = f.readlines()

        # Now we need to parse the file
        for line in lines:
            # Get the line
            line = line.strip()

            # Check for comments
            if line.startswith("#"):
                continue

            # Check for material data
            if line.startswith("TEXTURE_NOWRAP"):
                self.nowrap = True
                self.alb_texture = line.split()[1]
            elif line.startswith("TEXTURE_LIT_NOWRAP"):
                self.nowrap = True
                self.lit_texture = line.split()[1]
            elif line.startswith("TEXTURE_NORMAL"):
                self.nml_texture = line.split()[2]
                self.normal_scale = float(line.split()[1])
            elif line.startswith("TEXTURE"):
                self.alb_texture = line.split()[1]
            elif line.startswith("TEXTURE_LIT"):
                self.lit_texture = line.split()[1]
            elif line.startswith("WEATHER"):
                self.weather_texture = line.split()[1]
            elif line.startswith("WEATHER_TRANSPARENT"):
                self.weather_texture = ""
            elif line.startswith("SUPER_ROUGHNESS"):
                self.super_rough = True
            elif line.startswith("NO_BLEND"):
                self.do_blend = False
                self.blend_cutoff = float(line.split()[1])

            # Check for decals (disabled for now)
            # if line.startswith("DECAL"):
            #     if self.decal_1 is None:
            #         self.decal_1 = decal_utils.get_decal_from_command(line)
            #     else:
            #         self.decal_2 = decal_utils.get_decal_from_command(line)

            # Check for main polygon params
            if line.startswith("LAYER_GROUP"):
                self.layer = line.split()[1].upper()
                self.layer_offset = int(line.split()[2])
            elif line.startswith("SCALE"):
                self.scale_x = int(line.split()[1])
                self.scale_y = int(line.split()[2])
            elif line.startswith("SURFACE"):
                self.surface = line.split()[1]
            elif line.startswith("LOAD_CENTER"):
                self.do_load_center = True
                self.load_center_lat = float(line.split()[1])
                self.load_center_lon = float(line.split()[2])
                self.load_center_size = float(line.split()[3])
                self.load_center_res = float(line.split()[4])
            elif line.startswith("TEXTURE_TILE"):
                self.do_tiling = True
                self.tiling_x_pages = int(line.split()[1])
                self.tiling_y_pages = int(line.split()[2])
                self.tiling_map_x_res = int(line.split()[3])
                self.tiling_map_y_res = int(line.split()[4])
                self.tiling_map_texture = line.split()[5]
            elif line.startswith("RUNWAY_MARKINGS"):
                self.do_runway_markings = True
                self.runway_r = int(line.split()[1])
                self.runway_g = int(line.split()[2])
                self.runway_b = int(line.split()[3])
                self.runway_a = int(line.split()[4])
                self.runway_marking_texture = line.split()[5]
            elif line.startswith("RUNWAY_NOISE"):
                self.do_runway_noise = True

    def from_collection(self, in_collection):
        # Check if the collection is exportable
        if not in_collection.xp_pol.exportable:
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
        self.runway_r = in_collection.xp_pol.runway_markings_r
        self.runway_g = in_collection.xp_pol.runway_markings_g
        self.runway_b = in_collection.xp_pol.runway_markings_b
        self.runway_a = in_collection.xp_pol.runway_markings_a
        self.runway_marking_texture = in_collection.xp_pol.runway_markings_texture

        # Ensure the collection has a material
        if not in_collection.xp_pol.material:
            raise Exception(f"Error: No material found in collection {in_collection.name}. Please configure material with the X-Plane Material Plugin!")

        # Extract material data
        mat = in_collection.xp_pol.material.xp_materials
        self.layer = mat.layer_group
        self.layer_offset = mat.layer_group_offset
        self.alb_texture = mat.alb_texture
        self.lit_texture = mat.lit_texture
        self.nml_texture = mat.nml_texture
        self.weather_texture = mat.weather_texture
        self.do_blend = mat.blend_alpha
        self.blend_cutoff = mat.blend_cutoff
        self.decal_1 = mat.decal_one
        self.decal_2 = mat.decal_two
        self.surface = mat.surface_type

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
