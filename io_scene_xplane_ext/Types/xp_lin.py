#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Export
#Purpose:   Provide a class that defines the X-Plane line type

#Include decal params from our material plugin
from ..Helpers import line_utils #type: ignore
from ..Helpers import decal_utils #type: ignore
from ..Helpers import file_utils #type: ignore
from ..Helpers import misc_utils #type: ignore
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
        self.decal_1 = None
        self.decal_2 = None
        self.surface = "NONE"

    def write(self, output_path):
        output_folder = os.path.dirname(output_path)

        #Define a string to hold the file contents
        of = ""

        of += "A\n850\nLINE_PAINT\n\n"

        #Write the material data
        of += "#Materials\n"

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
            elif line.startswith("TEXTURE_LIT"):
                self.lit_texture = line.split()[1]
            elif line.startswith("TEXTURE"):
                self.alb_texture = line.split()[1]
            elif line.startswith("WEATHER") and not line.startswith("WEATHER_TRANSPARENT"):
                self.weather_texture = line.split()[1]
            elif line.startswith("SUPER_ROUGHNESS"):
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
            if line.startswith("SURFACE"):
                self.surface = line.split()[1]

            #Check for segments
            if line.startswith("S_OFFSET"):
                cur_seg = segment()
                cur_seg.layer = int(line.split()[1])
                cur_seg.l = float(line.split()[2]) / uv_scalar_x
                cur_seg.c = float(line.split()[3]) / uv_scalar_x
                cur_seg.r = float(line.split()[4]) / uv_scalar_x
                self.segments.append(cur_seg)

            #Check for caps
            if line.startswith("START_CAP") or line.startswith("END_CAP"):
                cur_cap = cap()
                if line.startswith("START_CAP"):
                    cur_cap.type = "START"
                else:
                    cur_cap.type = "END"
                cur_cap.layer = int(line.split()[1])
                cur_cap.l = float(line.split()[2]) / uv_scalar_x
                cur_cap.c = float(line.split()[3]) / uv_scalar_x
                cur_cap.r = float(line.split()[4]) / uv_scalar_x
                cur_cap.bottom = float(line.split()[5]) / uv_scalar_y
                cur_cap.top = float(line.split()[6]) / uv_scalar_y
                self.caps.append(cur_cap)

    def from_collection(self, in_collection):
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
            raise Exception("Error: No segment objects found in collection" + in_collection.name)
        
        #Now we want to sort them based on their Z position. While not *necessary*, it makes the output nicer
        exportable_objects.sort(key=lambda x: x.location.z)

        #Now we need to get the scale. We will get this from the bottom object. It is expected that all objects share the same scale
        scale_x, scale_y = 0, 0
        
        scale_x, scale_y = line_utils.get_scale_from_layer(exportable_objects[0])

        #Now that we do have a scale, we will iterate over every object again and check if it's scale is within a reasonable range. If not, we will throw an error.
        max_scale_diff_x = scale_x * 0.1
        max_scale_diff_y = scale_y * 0.1
        for obj in exportable_objects:
            local_scale_x, local_scale_y = line_utils.get_scale_from_layer(obj)
            if abs(local_scale_x - scale_x) > max_scale_diff_x or abs(local_scale_y - scale_y) > max_scale_diff_y:
                raise Exception("Error: Object " + obj.name + " has a different scale than the rest of the collection. Please make sure all objects share the same UV scale.")
            break

        self.scale_x = scale_x
        self.scale_y = scale_y
        self.segment_count = in_collection.xp_lin.segment_count
        self.mirror = in_collection.xp_lin.mirror

        #Ensure we have a material. Then we will extract material data from it
        if len(exportable_objects[0].data.materials) == 0:
            raise Exception(f"Error: No material found on object! { exportable_objects[0].name } Please configure material with my X-Plane Material Plugin!")
        
        mat = in_collection.objects[0].data.materials[0].xp_materials

        if mat.do_separate_material_texture:
            raise Exception("Error: X-Plane does not support separate material textures on lines/polygons/facades. Please use a normal map with the metalness and glossyness in the blue and alpha channels respectively.")

        self.layer = mat.layer_group
        self.layer_offset = mat.layer_group_offset
        self.alb_texture = mat.alb_texture
        self.lit_texture = mat.lit_texture
        self.nml_texture = mat.normal_texture
        self.weather_texture = mat.weather_texture
        self.do_blend = mat.blend_alpha
        self.blend_cutoff = mat.blend_cutoff
        self.decal_1 = mat.decal_one
        self.decal_2 = mat.decal_two
        self.surface = mat.surface_type

        # Next we need to get segment commands. We treat the Z position as layer, so things are layered intuitively. But Z position can be *anything*.
        # So we need to sort the Z positions, then get the *index* of that Z position, so we have a 0-top continuous range of layers.
        all_layers = []
        for obj in exportable_objects:
            if obj.xp_lin.type == "SEGMENT":
                all_layers.append(line_utils.get_layer_z(obj))
        all_layers.sort()

        for obj in exportable_objects:
            #Get it's type
            type = obj.xp_lin.type

            #Get the closest layer. Why? Because caps are children of segments, so they need to connect to be in whatever layer their *closest* segment is in, rather than getting stuck in their own individual layer
            closest_idx = 0
            closest_dist = 9999
            for i, layer in enumerate(all_layers):
                dist = abs(line_utils.get_layer_z(obj) - layer)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_idx = i

            #Get the segment
            if type == "SEGMENT":
                seg = line_utils.get_layer_from_segment_object(obj, closest_idx, type)
                self.segments.append(seg)
            else:
                cap = line_utils.get_layer_from_segment_object(obj, closest_idx, type)
                self.caps.append(cap)
        
        #That is it! We got the material data, scale, and layer commands. Now the caller just needs to call write() to write the file.

    def to_collection(self, in_name):
        #Define a new collection with the same name as the file
        new_collection = bpy.data.collections.new(name=in_name)
        bpy.context.scene.collection.children.link(new_collection)

        #First create a new material for the line
        mat = bpy.data.materials.new(name=in_name)
        mat.xp_materials.alb_texture = self.alb_texture
        mat.xp_materials.lit_texture = self.lit_texture
        mat.xp_materials.normal_texture = self.nml_texture
        mat.xp_materials.weather_texture = self.weather_texture
        mat.xp_materials.blend_alpha = self.do_blend
        mat.xp_materials.blend_cutoff = self.blend_cutoff
        mat.xp_materials.layer_group = self.layer.upper()
        mat.xp_materials.layer_group_offset = int(self.layer_offset)
        mat.xp_materials.surface_type = self.surface

        #Call operator xp_mats.update_material_nodes
        #bpy.ops.xp_ext.update_material_nodes(override_material=mat)

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
