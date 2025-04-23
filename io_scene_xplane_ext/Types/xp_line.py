#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Export
#Purpose:   Provide a class that defines the X-Plane line type

#Include decal params from our material plugin
from ..Helpers import line_utils #type: ignore
from ..Helpers import decal_utils #type: ignore
from ..Helpers import file_utils #type: ignore
import os

class XPSegment():
    def __init__(self):
        self.layer = 0
        self.l = 0
        self.c = 0
        self.r = 0

class XPCap():
    def __init__(self):
        self.layer = 0
        self.l = 0
        self.c = 0
        self.r = 0
        self.top = 0
        self.bottom = 0
        self.type = "START"

class XPLin():
    def __init__(self):
        self.segments = []
        self.caps = []
        self.alb_texture = ""
        self.nml_texture = ""
        self.layer = "MARKINGS"
        self.layer_offset = 0
        self.scale_x = 0
        self.scale_y = 0
        self.normal_scale = 1
        self.blend_cutoff = 0
        self.do_blend = False
        self.mirror = True
        self.segment_count = 1
        self.super_rough = False
        self.decal_1 = None
        self.decal_2 = None

    def write(self, output_path):
        output_folder = os.path.dirname(output_path)

        #Define a string to hold the file contents
        of = ""

        of += "A\n850\nLINE_PAINT\n\n"

        #Write the material data
        of += "#Materials\n"

        if self.alb_texture != "":
            of += "TEXTURE " + os.path.relpath(file_utils.rel_to_abs(self.alb_texture), output_folder) + "\n"
        if self.nml_texture != "":
            of += "TEXTURE_NORMAL " + str(self.normal_scale) + "\t" + os.path.relpath(file_utils.rel_to_abs(self.nml_texture), output_folder) + "\n"
        if self.super_rough:
            of += "SUPER_ROUGHness "

        if not self.do_blend:
            of += "NO_BLEND " + str(self.blend_cutoff) + "\n"
        
        of += "\n"

        #Write the decals
        of += "#Decals\n"
        if (self.decal_1 != None):
            of += decal_utils.get_decal_command(self.decal_1, output_folder)
        if (self.decal_2 != None):
            of += decal_utils.get_decal_command(self.decal_2, output_folder)

        of += "\n"

        of += "#Position Params\n"

        #Write the layer
        of += "LAYER_GROUP " + self.layer.lower() + " " + str(self.layer_offset) + "\n"
        if self.mirror:
            of += "MIRROR\n"
        if self.segment_count != 0:
            of += "ALIGN " + str(self.segment_count) + "\n"
        of += "SCALE " + str(int(self.scale_x)) + " " + str(int(self.scale_y)) + "\n"
        of += "TEX_WIDTH " + str(4096) + "\n"
        of += "TEX_HEIGHT " + str(4096) + "\n"

        of += "\n"

        #Write all the segments
        of += "#Segments\n"

        for seg in self.segments:
            #Format: S_OFFSET layer left center right
            of += "S_OFFSET " + str(int(seg.layer)) + " " + str(int(seg.l)) + " " + str(int(seg.c)) + " " + str(int(seg.r)) + "\n"

        of += "\n"

        #Write all the caps
        for cap in self.caps:
            #Format: START_CAP/END_CAP layer left center right top bottom type
            if cap.type == "START":
                of += "START_CAP "
            else:
                of += "END_CAP "

            of += str(int(cap.layer)) + " " + str(int(cap.l)) + " " + str(int(cap.c)) + " " + str(int(cap.r)) + " " + str(int(cap.top)) + " " + str(int(cap.bottom)) + "\n"

        #Open the output file and write the contents
        with open(output_path, 'w') as f:
            f.write(of)
    
    def read(self, in_file):
        #Read the file
        with open(in_file, 'r') as f:
            lines = f.readlines()

        uv_scalar_x = 4096
        uv_scalar_y = 4096

        #Now we need to parse the file
        for line in lines:
            #Get the line
            line = line.strip()

            #Check for comments
            if line.startswith("#"):
                continue

            #Check for material data
            if line.startswith("TEXTURE_NORMAL"):
                self.nml_texture = line.split()[2]
            elif line.startswith("TEXTURE"):
                self.alb_texture = line.split()[1]
            elif line.startswith("SUPER_ROUGHness"):
                self.super_rough = True
            elif line.startswith("NO_BLEND"):
                self.do_blend = False
                self.blend_cutoff = float(line.split()[1])

            #Check for a texture resolution specifier
            if line.startswith("TEX_WIDTH"):
                uv_scalar_x = int(line.split()[1])
            if line.startswith("TEX_HEIGHT"):
                uv_scalar_y = int(line.split()[1])

            #Check for decals (disabled)
            #if False #line.startswith("DECAL"):
            #    if self.decal_1 == None:
            #        self.decal_1 = line_utils.get_decal_from_command(line)
            #    else:
            #        self.decal_2 = line_utils.get_decal_from_command(line)

            #Check for position params
            if line.startswith("LAYER_GROUP"):
                self.layer = line.split()[1]
                self.layer_offset = float(line.split()[2])
            if line.startswith("MIRROR"):
                self.mirror = True
            if line.startswith("ALIGN"):
                self.segment_count = int(line.split()[1])
            if line.startswith("SCALE"):
                self.scale_x = float(line.split()[1])
                self.scale_y = float(line.split()[2])

            #Check for segments
            if line.startswith("S_OFFSET"):
                seg = XPSegment()
                seg.layer = int(line.split()[1])
                seg.l = float(line.split()[2]) / uv_scalar_x
                seg.c = float(line.split()[3]) / uv_scalar_x
                seg.r = float(line.split()[4]) / uv_scalar_x
                self.segments.append(seg)

            #Check for caps
            if line.startswith("START_CAP") or line.startswith("END_CAP"):
                cap = XPCap()
                if line.startswith("START_CAP"):
                    cap.type = "START"
                else:
                    cap.type = "END"
                cap.layer = int(line.split()[1])
                cap.l = float(line.split()[2]) / uv_scalar_x
                cap.c = float(line.split()[3]) / uv_scalar_x
                cap.r = float(line.split()[4]) / uv_scalar_x
                cap.top = float(line.split()[5]) / uv_scalar_y
                cap.bottom = float(line.split()[6]) / uv_scalar_y
                self.caps.append(cap)
