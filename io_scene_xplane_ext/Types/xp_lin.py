#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    xp_lin.py
#Purpose:   Provide a class that defines the X-Plane line type

#Include decal params from our material plugin
from ..Helpers import line_utils #type: ignore
from ..Helpers import decal_utils #type: ignore
from ..Helpers import file_utils #type: ignore
from ..Helpers import misc_utils #type: ignore
from ..Helpers import log_utils #type: ignore
from .. import material_config #type: ignore
import bpy #type: ignore
import os

class segment():
    def __init__(self):
        self.layer = 0
        self.l = 0
        self.c = 0
        self.r = 0

class cap():
    def __init__(self):
        self.layer = 0
        self.l = 0
        self.c = 0
        self.r = 0
        self.top = 0
        self.bottom = 0
        self.type = "START"

class line():
    def __init__(self):
        self.segments = []
        self.caps = []
        self.alb_texture = ""
        self.nml_texture = ""
        self.lit_texture = ""
        self.mod_texture = ""
        self.weather_texture = ""
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
        self.decals = []
        self.imported_decal_commands = []
        self.surface = "NONE"

    def write(self, output_path):
        log_utils.new_section(f"Writing .lin {output_path}")

        output_folder = os.path.dirname(output_path)

        #Define a string to hold the file contents
        of = ""

        of += "A\n850\nLINE_PAINT\n\n"

        #Write the material data
        of += "#Materials\n"

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
        if self.super_rough:
            of += "SUPER_ROUGHNESS\n"

        if not self.do_blend:
            of += "NO_BLEND " + misc_utils.ftos(self.blend_cutoff, 2) + "\n"
        
        of += "\n"
        
        #Write the decals
        if len(self.decals) > 0:
            of += "#Decals\n"
            #Write the modulator texture
            if self.mod_texture != "":
                of += "TEXTURE_MODULATOR " + os.path.relpath(file_utils.to_absolute(self.mod_texture), output_folder) + "\n"
            for decal in self.decals:
                #Get the decal command
                decal_command = decal_utils.get_decal_command(decal, output_folder)
                if decal_command:
                    of += decal_command

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

            of += str(int(cap.layer)) + " " + str(int(cap.l)) + " " + str(int(cap.c)) + " " + str(int(cap.r)) + " " + str(int(cap.bottom)) + " " + str(int(cap.top)) + "\n"

        #Open the output file and write the contents
        with open(output_path, 'w') as f:
            f.write(of)
    
    def read(self, in_file):
        log_utils.new_section(f"Reading .lin {in_file}")

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

            tokens = line.split()
            if not tokens:
                continue

            # Defensive: check token count for each command before using tokens
            cmd = tokens[0]
            min_tokens = {
                'TEXTURE_NORMAL': 3,
                'TEXTURE_LIT': 2,
                'TEXTURE': 2,
                'TEXTURE_MODULATOR': 2,
                'WEATHER': 2,
                'NO_BLEND': 2,
                'TEX_WIDTH': 2,
                'TEX_HEIGHT': 2,
                'DECAL': 1,
                'NORMAL_DECAL': 1,
                'LAYER_GROUP': 2, # can be 2 or 3, but 2 is safe
                'MIRROR': 1,
                'ALIGN': 2,
                'SCALE': 2, # can be 2 or 3
                'SURFACE': 2,
                'S_OFFSET': 5,
                'START_CAP': 7,
                'END_CAP': 7,
            }
            # Only check if command is in our map
            if cmd in min_tokens and len(tokens) < min_tokens[cmd]:
                log_utils.warning(f"Not enough tokens for command '{cmd}'! Expected at least {min_tokens[cmd]}, got {len(tokens)}. Line: '{line}'")
                continue

            #Check for material data
            if cmd == "TEXTURE_NORMAL":
                self.nml_texture = tokens[2]
            elif cmd == "TEXTURE_LIT":
                self.lit_texture = tokens[1]
            elif cmd == "TEXTURE":
                self.alb_texture = tokens[1]
            elif cmd == "TEXTURE_MODULATOR":
                self.mod_texture = tokens[1]
            elif cmd == "WEATHER" and cmd != "WEATHER_TRANSPARENT":
                self.weather_texture = tokens[1]
            elif cmd == "SUPER_ROUGHNESS":
                self.super_rough = True
            elif cmd == "NO_BLEND":
                self.do_blend = False
                self.blend_cutoff = float(tokens[1])

            #Check for a texture resolution specifier
            if cmd == "TEX_WIDTH":
                uv_scalar_x = int(tokens[1])
            if cmd == "TEX_HEIGHT":
                uv_scalar_y = int(tokens[1])

            #Check for decals
            if cmd.startswith("DECAL") or cmd.startswith("NORMAL_DECAL"):
                self.imported_decal_commands.append(line)

            #Check for position params
            if cmd == "LAYER_GROUP":
                self.layer = tokens[1]
                if len(tokens) > 2:
                    self.layer_offset = float(tokens[2])
            if cmd == "MIRROR":
                self.mirror = True
            if cmd == "ALIGN":
                self.segment_count = int(tokens[1])
            if cmd == "SCALE":
                self.scale_x = float(tokens[1])
                if len(tokens) > 2:
                    self.scale_y = float(tokens[2])
            if cmd == "SURFACE":
                self.surface = tokens[1]

            #Check for segments
            if cmd == "S_OFFSET":
                cur_seg = segment()
                cur_seg.layer = int(tokens[1])
                cur_seg.l = float(tokens[2]) / uv_scalar_x
                cur_seg.c = float(tokens[3]) / uv_scalar_x
                cur_seg.r = float(tokens[4]) / uv_scalar_x
                self.segments.append(cur_seg)

            #Check for caps
            if cmd == "START_CAP" or cmd == "END_CAP":
                cur_cap = cap()
                if cmd == "START_CAP":
                    cur_cap.type = "START"
                else:
                    cur_cap.type = "END"
                cur_cap.layer = int(tokens[1])
                cur_cap.l = float(tokens[2]) / uv_scalar_x
                cur_cap.c = float(tokens[3]) / uv_scalar_x
                cur_cap.r = float(tokens[4]) / uv_scalar_x
                cur_cap.bottom = float(tokens[5]) / uv_scalar_y
                cur_cap.top = float(tokens[6]) / uv_scalar_y
                self.caps.append(cur_cap)

    def from_collection(self, in_collection):
        log_utils.new_section(f"Reading .lin collection {in_collection.name}")

        #First iterate through all the objects in this collection. Here we will determine a list of objects eligable for export
        exportable_objects = []

        for obj in in_collection.objects:
            if obj.type == 'MESH':
                #Check if this object is exportable
                if obj.xp_lin.exportable:
                    exportable_objects.append(obj)

        #Make sure 1. We have exporable objects, and 2. At least one is a segment. In the XP format, caps are "children" of segments, so having caps without segments is a problem
        if len(exportable_objects) == 0:
            return
        if len([obj for obj in exportable_objects if obj.xp_lin.type == "SEGMENT"]) == 0:
            log_utils.error("Error: No segment objects found in collection" + in_collection.name)
            return
        
        #Now we want to sort them based on their Z position. While not *necessary*, it makes the output nicer
        exportable_objects.sort(key=lambda x: line_utils.get_layer_z(x))

        #Now we need to get the scale. We will get this from the bottom object. It is expected that all objects share the same scale
        scale_x, scale_y = 0, 0
        
        scale_x, scale_y = line_utils.get_scale_from_layer(exportable_objects[0])

        #Now that we do have a scale, we will iterate over every object again and check if it's scale is within a reasonable range. If not, we will throw an error.
        max_scale_diff_x = scale_x * 0.1
        max_scale_diff_y = scale_y * 0.1
        for obj in exportable_objects:
            local_scale_x, local_scale_y = line_utils.get_scale_from_layer(obj)
            if abs(local_scale_x - scale_x) > max_scale_diff_x or abs(local_scale_y - scale_y) > max_scale_diff_y:
                log_utils.error("Error: Object " + obj.name + " has a different scale than the rest of the collection. Please make sure all objects share the same UV scale.")
                return
            break

        self.scale_x = scale_x
        self.scale_y = scale_y
        self.segment_count = in_collection.xp_lin.segment_count
        self.mirror = in_collection.xp_lin.mirror

        if self.mirror and self.segment_count > 0:
            log_utils.warning("Warning: Mirror is enabled on a line with a set segment count. Segment count will be ignored as these are mutually exclusive settings.")
            self.segment_count = 0

        #Ensure we have a material. Then we will extract material data from it
        if len(exportable_objects[0].data.materials) == 0:
            log_utils.error(f"Error: No material found on object! { exportable_objects[0].name } Please configure material with my X-Plane Material Plugin!")
            return
        
        mat = in_collection.objects[0].data.materials[0].xp_materials

        if mat.do_separate_material_texture:
            log_utils.error("Error: X-Plane does not support separate material textures on lines/polygons/facades. Please use a normal map with the metalness and glossyness in the blue and alpha channels respectively.")
            return

        self.alb_texture = mat.alb_texture
        self.lit_texture = mat.lit_texture
        self.nml_texture = mat.normal_texture
        self.mod_texture = mat.decal_modulator
        self.weather_texture = mat.weather_texture
        self.do_blend = True if mat.blend_mode == 'BLEND' else False
        self.blend_cutoff = mat.blend_cutoff
        self.surface = mat.surface_type
        self.layer = mat.layer_group
        self.layer_offset = mat.layer_group_offset

        for decal in mat.decals:
            self.decals.append(decal)

        # Line layers are a bit weird. All segments need to be consecutive layers from 0+. However, layers *cannot* be duplicated (i.e. 2 segments on layer 0).
        # Additionally, caps are *children* of segments, a start and end cap need to be on the same layer as their closest segment. Yet, you cannot have two caps of the same type on the same layer!
        # So, the way we will do this is:
        # 1. All segments are sorted by their Z, so just add them and define their groups by incrementing a counter. Store these as a tuple of (Z position, layer index, used start cap flag, used end cap flag)
        # 2. For caps, from a list of tuples we defined during segments, find the nearest segment, and if it is not used for this given type, use it. If it is used, log the warning and skip it.
        segment_layers = []
        current_segment_layer = 0

        # Segments first
        for obj in exportable_objects:
            if obj.xp_lin.type == "SEGMENT":
                seg = line_utils.get_layer_from_segment_object(obj, current_segment_layer, "SEGMENT")
                self.segments.append(seg)
                segment_layers.append( (line_utils.get_layer_z(obj), current_segment_layer, False, False) ) #False, False for start and end cap used flags
                current_segment_layer += 1
        
        # Now handle caps
        for obj in exportable_objects:
            if obj.xp_lin.type != "SEGMENT":
                #Find the closest segment layer
                obj_layer_z = line_utils.get_layer_z(obj)
                closest_idx = -1
                closest_dist = 9999
                for i, (layer_z, layer_idx, start_used, end_used) in enumerate(segment_layers):
                    dist = abs(obj_layer_z - layer_z)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_idx = i
                
                if closest_idx == -1:
                    log_utils.warning(f"Error: Could not find a parent segment for cap object {obj.name}! Perhaps you have no segments? Skipping this cap.")
                    continue
                
                seg_layer_z, seg_layer_idx, start_used, end_used = segment_layers[closest_idx]

                if obj.xp_lin.type == "START":
                    if start_used:
                        log_utils.warning(f"Warning: Multiple start caps found for segment layer at Z {seg_layer_z}. Skipping cap object {obj.name}!")
                        continue
                    cap = line_utils.get_layer_from_segment_object(obj, seg_layer_idx, obj.xp_lin.type)
                    self.caps.append(cap)
                    #Mark start cap as used
                    segment_layers[closest_idx] = (seg_layer_z, seg_layer_idx, True, end_used)
                elif obj.xp_lin.type == "END":
                    if end_used:
                        log_utils.warning(f"Warning: Multiple end caps found for segment layer at Z {seg_layer_z}. Skipping cap object {obj.name}!")
                        continue
                    cap = line_utils.get_layer_from_segment_object(obj, seg_layer_idx, obj.xp_lin.type)
                    self.caps.append(cap)
                    #Mark end cap as used
                    segment_layers[closest_idx] = (seg_layer_z, seg_layer_idx, start_used, True)

    def to_collection(self, in_name):
        log_utils.new_section(f"Creating .lin collection {in_name}")

        #Define a new collection with the same name as the file
        new_collection = bpy.data.collections.new(name=in_name)
        bpy.context.scene.collection.children.link(new_collection)
        
        #First create a new material for the line
        mat = bpy.data.materials.new(name=in_name)
        mat.xp_materials.alb_texture = self.alb_texture
        mat.xp_materials.lit_texture = self.lit_texture
        mat.xp_materials.normal_texture = self.nml_texture
        mat.xp_materials.weather_texture = self.weather_texture
        mat.xp_materials.decal_modulator = self.mod_texture
        mat.xp_materials.blend_mode = 'BLEND' if self.do_blend else 'CLIP'
        mat.xp_materials.blend_cutoff = self.blend_cutoff
        mat.xp_materials.surface_type = self.surface
        mat.xp_materials.layer_group = self.layer.upper()
        mat.xp_materials.layer_group_offset = int(self.layer_offset)
        new_collection.xp_lin.exportable = True
        new_collection.xp_lin.mirror = self.mirror
        new_collection.xp_lin.segment_count = self.segment_count

        material_config.update_settings(mat)

        decal_alb_index = 0
        decal_nml_index = 2

        for decal in self.imported_decal_commands:
            if decal.startswith("NORMAL"):
                if decal_nml_index > 3:
                    log_utils.warning("Error: Too many normal decals! X-Plane only supports 2 normal decals per material.")
                    break
                decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_nml_index])
                decal_nml_index += 1
            else:
                if decal_alb_index > 2:
                    log_utils.warning("Error: Too many albedo decals! X-Plane only supports 2 decals per material.")
                    break
                decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_alb_index])
                decal_alb_index += 1

        material_config.update_settings(mat)

        #Now we will iterate through every segment, and generate a plane for it
        for seg in self.segments:
            #Create the vertices
            LowerLeft = line_utils.lin_vertex()
            LowerRight = line_utils.lin_vertex()
            UpperLeft = line_utils.lin_vertex()
            UpperRight = line_utils.lin_vertex()

            LowerLeft.x = (seg.l - seg.c) * self.scale_x
            LowerLeft.y = -0.5 * self.scale_y
            LowerLeft.z = seg.layer
            LowerLeft.u = seg.l
            LowerLeft.v = 0

            LowerRight.x = (seg.r - seg.c) * self.scale_x
            LowerRight.y = -0.5 * self.scale_y
            LowerRight.z = seg.layer
            LowerRight.u = seg.r
            LowerRight.v = 0

            UpperLeft.x = (seg.l - seg.c) * self.scale_x
            UpperLeft.y = 0.5 * self.scale_y
            UpperLeft.z = seg.layer
            UpperLeft.u = seg.l
            UpperLeft.v = 1

            UpperRight.x = (seg.r - seg.c) * self.scale_x
            UpperRight.y = 0.5 * self.scale_y
            UpperRight.z = seg.layer
            UpperRight.u = seg.r
            UpperRight.v = 1

            #Create the faces
            new_plane = line_utils.gen_plane_from_verts([LowerLeft, LowerRight, UpperRight, UpperLeft])
            new_plane.data.materials.append(mat)

            #Link it to the scene and new collection
            new_collection.objects.link(new_plane)

        #Now we will iterate through every cap, and generate a plane for it
        for cur_cap in self.caps:
            #Create the vertices
            LowerLeft = line_utils.lin_vertex()
            LowerRight = line_utils.lin_vertex()
            UpperLeft = line_utils.lin_vertex()
            UpperRight = line_utils.lin_vertex()

            LowerLeft.x = (cur_cap.l - cur_cap.c) * self.scale_x
            LowerLeft.y = cur_cap.bottom * self.scale_y
            LowerLeft.z = cur_cap.layer
            LowerLeft.u = cur_cap.l
            LowerLeft.v = cur_cap.bottom

            LowerRight.x = (cur_cap.r - cur_cap.c) * self.scale_x
            LowerRight.y = cur_cap.bottom * self.scale_y
            LowerRight.z = cur_cap.layer
            LowerRight.u = cur_cap.r
            LowerRight.v = cur_cap.bottom

            UpperLeft.x = (cur_cap.l - cur_cap.c) * self.scale_x
            UpperLeft.y = cur_cap.top * self.scale_y
            UpperLeft.z = cur_cap.layer
            UpperLeft.u = cur_cap.l
            UpperLeft.v = cur_cap.top

            UpperRight.x = (cur_cap.r - cur_cap.c) * self.scale_x
            UpperRight.y = cur_cap.top * self.scale_y
            UpperRight.z = cur_cap.layer
            UpperRight.u = cur_cap.r
            UpperRight.v = cur_cap.top

            #Create the faces
            new_plane = line_utils.gen_plane_from_verts([LowerLeft, LowerRight, UpperRight, UpperLeft])
            new_plane.data.materials.append(mat)
        
            if cur_cap.type == "START":
                new_plane.xp_lin.type = "START"
            elif cur_cap.type == "END":
                new_plane.xp_lin.type = "END"

            #Link it to the scene and new collection
            new_collection.objects.link(new_plane)
