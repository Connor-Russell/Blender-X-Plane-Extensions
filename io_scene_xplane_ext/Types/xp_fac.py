#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      4/18/2025
#Module:    xp_fac.py
#Purpose:   Provide classes that abstracts the X-Plane facade format

from ..Helpers import facade_utils # type: ignore
from ..Helpers import geometery_utils # type: ignore
from ..Helpers import decal_utils # type: ignore
from ..Helpers import file_utils # type: ignore
from ..Helpers import misc_utils # type: ignore
from ..Helpers import log_utils
from .. import material_config
from . import xp_attached_obj # type: ignore
import os

import bpy

class mesh:
    def __init__(self):
        self.name = ""
        self.vertices = []
        self.indices = []
        self.far_lod = 0
        self.group = 0
        self.cuts = 0
        self.attached_objects = []

    def from_obj(self, obj):
        dc = geometery_utils.get_draw_call_from_obj(obj)
        self.vertices = dc[0]
        self.indices = dc[1]
        self.name = obj.name
        self.far_lod = obj.xp_fac_mesh.far_lod
        self.group = obj.xp_fac_mesh.group
        self.cuts = obj.xp_fac_mesh.cuts

    def to_obj(self, name):
        #Since we scaled by -1 on the y to compensate for XP, we need to reverse the indicies
        temp_indices = [i for i in reversed(self.indices)]  # Reverse the indices to fix face direction

        # Use the vertices and indices to generate the Blender object
        obj = geometery_utils.create_obj_from_draw_call(self.vertices, temp_indices, name)

        #Set the params of the object
        obj.xp_fac_mesh.far_lod = int(float(self.far_lod))
        obj.xp_fac_mesh.group = int(float(self.group))
        obj.xp_fac_mesh.cuts = int(float(self.cuts))
        obj.name = name

        # Return the created object
        return obj
    
class segment:
    def __init__(self):
        self.meshes = []
        self.attached_objects = [] #List of all attached objects. These are xp_attached_obj objects.
        self.name = ""
        self.is_curved = False

    def from_collection(self, collection):
        #Get the name of the collection
        self.name = collection.name

        #Iterate over all objects in the collection
        for obj in collection.objects:
            #If the object is a segment, get its geometry
            if obj.type == "MESH":
                cur_mesh = mesh()
                cur_mesh.from_obj(obj)
                self.meshes.append(cur_mesh)
            
            #If this is an empty, these typically are an attached object. We will check and handle that here.
            elif obj.type == "EMPTY":
                new_attached_obj = xp_attached_obj.xp_attached_obj()
                new_attached_obj.read_from_obj(obj)

                if new_attached_obj.valid:
                    self.attached_objects.append(new_attached_obj)

    def to_collection(self, name, in_material):
        """
        Converts the segment to a Blender collection, including its meshes and attached objects.

        :param name: The name of the Blender collection to create.
        :return: The created Blender collection.
        """
        # Create a new collection
        collection = bpy.data.collections.new(name)

        # Add meshes to the collection
        for mesh in self.meshes:
            obj = mesh.to_obj(mesh.name)
            obj.data.materials.append(in_material)
            collection.objects.link(obj)

        # Add attached objects to the collection
        for cur_obj in self.attached_objects:
            obj = cur_obj.to_obj(os.path.basename(cur_obj.resource))
            collection.objects.link(obj)

        # Return the created collection
        return collection

    def append_obj_resources(self, target_list):
        for obj in self.attached_objects:
            target_list.append(obj.resource)
                    
class spelling:
    def __init__(self):
        self.segment_names = []  #List of all segment names in this spelling

class wall:
    def __init__(self):
        self.spellings = []  #List of all spellings in this wall rule
        self.name = ""
        self.min_length = 0
        self.max_length = 0
        self.min_heading = 0
        self.max_heading = 359

class floor:
    def __init__(self):
        self.name = ""  #Name of the floor, debug purposes only
        self.all_segments = []  #Object containing all segments in this floor. They are referenced by name.
        self.all_curved_segments = [] #Object containing all the curved segments in this floor. They are referenced by name. These will be duplicates of the straight segments, or an _Curved variant. In the future this may be specifiable via the UI
        self.roof_scale_x = 0  #Meters
        self.roof_scale_y = 0  #Meters
        self.roof_objs = [] #List of all roof objects. These are xp_attached_obj objects.
        self.roof_heights = [] #List of all roof heights. These are floats.
        self.roof_two_sided = False #If true, the roof is two sided. If false, the roof is one sided.
        self.roof_collision = 'NONE' #Roof collision type. This is a string.
        self.walls = []

    def from_floor_props(self, in_floor):

        #Get the name of the collection
        self.name = in_floor.name

        #Iterate over all the wall rules, and all the spellings. We need to get a deduped list of all the segments
        all_segments_names = [] #These are the segment names

        for wall_rule in in_floor.walls:

            cur_wall = wall()
            cur_wall.name = wall_rule.name
            cur_wall.min_length = wall_rule.min_length
            cur_wall.max_length = wall_rule.max_length
            cur_wall.min_heading = wall_rule.min_heading
            cur_wall.max_heading = wall_rule.max_heading

            #Load all the spelling params into this wall, and load all the names of the segments the spellings map to into our list of all segment names
            for cur_spelling in wall_rule.spellings:
                new_spelling = spelling()
                for entry in cur_spelling.entries:
                    all_segments_names.append(entry.collection)
                    new_spelling.segment_names.append(entry.collection)

                cur_wall.spellings.append(new_spelling)
            
            self.walls.append(cur_wall)

        #Dedup the list of segments
        all_segments_names = list(set(all_segments_names))
        all_segments_names.sort() #Sort the list of segments. Again so the order is deterministic

        #Iterate over all the segments and get their geometry
        for cur_segment in all_segments_names:
            #Find this collection in the scene
            col = None
            for c in bpy.data.collections:
                if c.name == cur_segment:
                    col = c
                    break

            if col is None:
                log_utils.error("Could not find collection: " + cur_segment + " Maybe it was deleted?")
                return
            
            #Check if there is an _Curved variant of this segment.
            segment_curved = cur_segment + "_Curved"
            col_curved = None
            for c in bpy.data.collections:
                if c.name == segment_curved:
                    col_curved = c
                    break
            
            if col_curved is not None:
                #If there is a curved variant, we need to add it to the list of segments
                new_segment = segment()
                new_segment.from_collection(col_curved)
                self.all_curved_segments.append(new_segment)
            else:
                #If there is no curved variant, we need to use the straight segment
                new_segment = segment()
                new_segment.from_collection(col)
                self.all_curved_segments.append(new_segment)

            new_segment = segment()
            new_segment.from_collection(col)
            self.all_segments.append(new_segment)

        #Get the roof collection, so we can get it's parameters
        roof_col = None
        for c in bpy.data.collections:
            if c.name == in_floor.roof_collection:
                roof_col = c
                break
        
        if roof_col is None:
            log_utils.warning("Could not find roof collection: " + self.name + "_roof")
            self.roof_scale_x = 1
            self.roof_scale_y = 1
            self.roof_objs = []
            self.roof_heights = [1.0]
        else:
            #Get the roof params
            self.roof_scale_x, self.roof_scale_y, self.roof_objs, self.roof_heights = facade_utils.get_roof_data(roof_col)

            #Sort the roof objects by their names
            self.roof_objs.sort(key=lambda x: x.resource)

    def append_obj_resources(self, target_list):
        for seg in self.all_segments:
            seg.append_obj_resources(target_list)
        for obj in self.roof_objs:
            target_list.append(obj.resource)

    def to_floor_props(self, in_floor):
        """
        Populates a Blender floor property group (in_floor) with the data from this floor object.

        :param in_floor: The Blender floor property group to populate.
        """
        # Set the name of the floor
        in_floor.name = self.name

        # Populate wall rules and their spellings
        for cur_wall in self.walls:
            wall_rule = in_floor.walls.add()
            wall_rule.name = cur_wall.name
            wall_rule.min_length = cur_wall.min_length
            wall_rule.max_length = cur_wall.max_length
            wall_rule.min_heading = cur_wall.min_heading
            wall_rule.max_heading = cur_wall.max_heading

            for cur_spelling in cur_wall.spellings:
                spelling = wall_rule.spellings.add()
                for segment_name in cur_spelling.segment_names:
                    entry = spelling.entries.add()
                    entry.collection = segment_name

        # Set roof scale
        in_floor.roof_scale_x = self.roof_scale_x
        in_floor.roof_scale_y = self.roof_scale_y

#This class is only used when importing a facade. It is to hold the material data until we create a material for it.
class facade_material:
    def __init__(self):
        self.alb_texture = ""
        self.nml_tile_ratio = 1.0
        self.nml_texture = ""
        self.lit_texture = ""
        self.mod_texture = ""
        self.do_blend_alpha = True
        self.alpha_cutoff = 0.5
        self.cast_shadow = True
        self.layer_group = "OBJECTS"
        self.layer_group_offset = 0
        self.decals = []  # List of decals, each decal is a facade_decal object
        self.imported_decal_commands = []

class facade:
    def __init__(self):
        self.name = "" #Name of the facade, relative to the blender file
        self.floors = []        #List of all floors in this facade. These are xp_floor objects.
        self.all_objects = []      #List of all objects in this facade. These are strings
        self.roof_scale_x = 0   #Meters
        self.roof_scale_y = 0   #Meters
        self.do_wall_mesh = True    #If true, the wall mesh will be generated. If false, the wall mesh will not be generated.
        self.do_roof_mesh = True    #If true, the roof mesh will be generated. If false, the roof mesh will not be generated.
        self.wall_material = None   #This is a PROP_mats (bpy.types.Material.xp_materials)
        self.roof_material = None   #This is a PROP_mats (bpy.types.Material.xp_materials)
        self.import_wall_material = None #This is a facade_material
        self.import_roof_material = None #This is a facade_material
        self.export_wall_layer_group = "OBJECTS"
        self.export_wall_layer_group_offset = 0
        self.export_roof_layer_group = "OBJECTS"
        self.export_roof_layer_group_offset = 0
        self.graded = False
        self.ring = False

    def read(self, in_path):
        """
        Reads a .fac file and populates the facade object and its members.
        """

        log_utils.new_section(f"Reading .fac {in_path}")

        self.name = os.path.basename(in_path)  # Get the name of the facade file

        with open(in_path, "r") as f:
            lines = f.readlines()

        current_floor = None
        current_wall = None
        current_spelling = None
        current_segment = None
        current_mesh = None
        current_material = None

        for line in lines:
            line = line.strip()

            if not line or line.startswith("#"):
                continue  # Ignore empty lines and comments

            tokens = line.split()
            if not tokens:
                continue

            # Defensive: check token count for each command before using tokens
            command = tokens[0]
            min_tokens = {
                'I': 1,
                'FACADE': 1,
                'GRADED': 1,
                'DRAPED': 1,
                'RING': 2,
                'SHADER_WALL': 1,
                'SHADER_ROOF': 1,
                'TEXTURE': 2,
                'TEXTURE_LIT': 2,
                'TEXTURE_NORMAL': 2,
                'TEXTURE_MODULATOR': 2,
                'NO_BLEND': 2,
                'NO_SHADOW': 1,
                'LAYER_GROUP': 3,
                'DECAL': 1,
                'NORMAL_DECAL': 1,
                'ROOF_SCALE': 3,
                'OBJ': 2,
                'FLOOR': 2,
                'ROOF_TWO_SIDED': 1,
                'ROOF_HEIGHT': 2,
                'ROOF_OBJ_HEADING': 7,
                'SEGMENT': 2,
                'SEGMENT_CURVED': 2,
                'MESH': 4,
                'VERTEX': 9,
                'IDX': 2,
                'WALL': 6,
                'SPELLING': 2,
                'ATTACH_DRAPED': 6,
                'ATTACH_GRADED': 6,
            }
            if command in min_tokens and len(tokens) < min_tokens[command]:
                
                log_utils.warning(f"Not enough tokens for command '{command}'! Expected at least {min_tokens[command]}, got {len(tokens)}. Line: '{line}'")
                continue

            if command == "I":
                # Header line, skip
                continue

            elif command == "FACADE":
                # Start of a facade definition, skip
                continue

            elif command == "GRADED":
                self.graded = True

            elif command == "DRAPED":
                self.graded = False

            elif command == "RING":
                self.ring = tokens[1] == "1"

            elif command == "SHADER_WALL":
                # Wall material data
                current_material = facade_material()
                self.import_wall_material = current_material
                current_mat_name = "WALL"

            elif command == "SHADER_ROOF":
                # Roof material data
                current_material = facade_material()
                self.import_roof_material = current_material
                current_mat_name = "ROOF"

            elif command == "TEXTURE":
                if current_material:
                    current_material.alb_texture = tokens[1]

            elif command == "TEXTURE_LIT":
                if current_material:
                    current_material.lit_texture = tokens[1]

            elif command == "TEXTURE_NORMAL":
                if current_material:
                    current_material.nml_tile_ratio = float(tokens[1])
                    current_material.nml_texture = tokens[2]

            elif command == "TEXTURE_MODULATOR":
                if current_material:
                    current_material.mod_texture = tokens[1]

            elif command == "NO_BLEND":
                if current_material:
                    current_material.do_blend_alpha = False
                    current_material.alpha_cutoff = float(tokens[1])

            elif command == "NO_SHADOW":
                if current_material:
                    current_material.cast_shadow = False

            elif command == "LAYER_GROUP":
                if current_material:
                    current_material.layer_group = tokens[1]
                    current_material.layer_group_offset = int(tokens[2])

            elif command.startswith("DECAL") or command.startswith("NORMAL_DECAL"):
                if current_material:
                    current_material.imported_decal_commands.append(line)

            elif command == "ROOF_SCALE":
                self.roof_scale_x = float(tokens[1])
                self.roof_scale_y = float(tokens[2])

            elif command == "OBJ":
                self.all_objects.append(tokens[1])

            elif command == "FLOOR":
                current_floor = floor()
                current_floor.name = tokens[1]
                self.floors.append(current_floor)

            elif command == "ROOF_TWO_SIDED":
                if current_floor:
                    current_floor.roof_two_sided = True

            elif command == "ROOF_HEIGHT":
                if current_floor:
                    current_floor.roof_heights.append(float(tokens[1]))

            elif command == "ROOF_OBJ_HEADING":
                if current_floor:
                    obj_index = int(tokens[1])
                    obj_resource = self.all_objects[obj_index]
                    attached_obj = xp_attached_obj.xp_attached_obj()
                    attached_obj.resource = obj_resource
                    attached_obj.rot_z = float(tokens[2])
                    attached_obj.loc_x = float(tokens[3])
                    attached_obj.loc_z = float(tokens[4])
                    attached_obj.min_draw = float(tokens[5])
                    attached_obj.max_draw = float(tokens[6])
                    current_floor.roof_objs.append(attached_obj)

            elif command == "SEGMENT":
                current_segment = segment()
                current_segment.name = tokens[1]
                if current_floor:
                    current_floor.all_segments.append(current_segment)

            elif command == "SEGMENT_CURVED":
                current_segment = segment()
                current_segment.name = tokens[1]
                current_segment.is_curved = True
                if current_floor:
                    current_floor.all_curved_segments.append(current_segment)

            elif command == "MESH":
                if current_segment:
                    current_mesh = mesh()
                    current_mesh.group = float(tokens[1])
                    current_mesh.far_lod = float(tokens[2])
                    current_segment.meshes.append(current_mesh)

            elif command == "VERTEX":
                if current_mesh:
                    #X-Plane facades are *very* weird. They scale the wall mesh by -1 on their z axis (our y). So we need to do the same here so XP appears the same as blender - 0y being the start of the wall
                    vertex = geometery_utils.xp_vertex(
                        loc_x=float(tokens[1]),
                        loc_y=-float(tokens[3]),
                        loc_z=float(tokens[2]),
                        normal_x=float(tokens[4]),
                        normal_y=-float(tokens[6]),
                        normal_z=float(tokens[5]),
                        uv_x=float(tokens[7]),
                        uv_y=float(tokens[8])
                    )

                    current_mesh.vertices.append(vertex)

            elif command == "IDX":
                if current_mesh:
                    current_mesh.indices.extend(map(int, tokens[1:]))

            elif command == "WALL":
                current_wall = wall()
                current_wall.min_length = float(tokens[1])
                current_wall.max_length = float(tokens[2])
                current_wall.min_heading = float(tokens[3])
                current_wall.max_heading = float(tokens[4])
                current_wall.name = tokens[5]
                if current_floor:
                    current_floor.walls.append(current_wall)

            elif command == "SPELLING":
                current_spelling = spelling()
                if current_wall:
                    current_wall.spellings.append(current_spelling)
                for seg_idx in tokens[1:]:
                    seg_idx = int(seg_idx)
                    if seg_idx < len(current_floor.all_segments):
                        segment_name = current_floor.all_segments[seg_idx].name
                        current_spelling.segment_names.append(segment_name)
            elif command == "ATTACH_DRAPED":
                if current_segment:
                    obj_index = int(tokens[1])
                    obj_resource = self.all_objects[obj_index]
                    attached_obj = xp_attached_obj.xp_attached_obj()
                    attached_obj.resource = obj_resource
                    attached_obj.loc_x = float(tokens[2])
                    attached_obj.loc_z = float(tokens[3])
                    attached_obj.loc_y = float(tokens[4])
                    attached_obj.rot_z = misc_utils.resolve_heading(float(tokens[5]) + 180)
                    if len(tokens) > 6:
                        attached_obj.min_draw = float(tokens[6])
                        attached_obj.max_draw = float(tokens[7])
                    attached_obj.draped = True
                    current_segment.attached_objects.append(attached_obj)

            elif command == "ATTACH_GRADED":
                if current_segment:
                    obj_index = int(tokens[1])
                    obj_resource = self.all_objects[obj_index]
                    attached_obj = xp_attached_obj.xp_attached_obj()
                    attached_obj.resource = obj_resource
                    attached_obj.loc_x = float(tokens[2])
                    attached_obj.loc_z = float(tokens[3])
                    attached_obj.loc_y = float(tokens[4])
                    attached_obj.rot_z = misc_utils.resolve_heading(float(tokens[5]) + 180)
                    if len(tokens) > 6:
                        attached_obj.min_draw = float(tokens[6])
                        attached_obj.max_draw = float(tokens[7])
                    attached_obj.draped = False
                    current_segment.attached_objects.append(attached_obj)

        # Sort objects and segments for consistency
        self.all_objects.sort()
        for cur_floor in self.floors:
            cur_floor.all_segments.sort(key=lambda seg: seg.name)
            cur_floor.all_curved_segments.sort(key=lambda seg: seg.name)
            cur_floor.roof_objs.sort(key=lambda obj: obj.resource)

    def write(self, out_path):
        log_utils.new_section(f"Writing .fac {out_path}")

        output_folder = os.path.dirname(out_path)
        output = ""

        #Start with the header
        output += "I\n1000\nFACADE\n\n"

        #Basic properties
        if self.graded:
            output += "GRADED\n"
        else:
            output += "DRAPED\n"

        if self.ring:
            output += "RING 1\n"
        else:
            output += "RING 0\n"

        output += "\n"

        #Define the roof surface. We save this so we can set the HARD_ROOF command later as it is on a per-floor basis not a facade wide basis
        roof_surface = ""

        #Wall shader
        if self.wall_material is not None and self.do_wall_mesh:
            output += "SHADER_WALL\nNORMAL_METALNESS\n"

            mat = self.wall_material.xp_materials

            if mat.do_separate_material_texture:
                log_utils.error("Error: X-Plane does not support separate material textures on lines/polygons/facades. Please use a normal map with the metalness and glossyness in the blue and alpha channels respectively.")
                return

            #Textures
            if mat.alb_texture != "":
                output += "TEXTURE " + os.path.relpath(file_utils.to_absolute(mat.alb_texture), output_folder) + "\n"
            if mat.lit_texture != "":
                output += "TEXTURE_LIT " + os.path.relpath(file_utils.to_absolute(mat.lit_texture), output_folder) + "\n"
            if mat.normal_texture != "":
                output += "TEXTURE_NORMAL " + str(mat.normal_tile_ratio) + " " + os.path.relpath(file_utils.to_absolute(mat.normal_texture), output_folder)+ "\n"
            if mat.decal_modulator != "":
                output += "TEXTURE_MODULATOR " + os.path.relpath(file_utils.to_absolute(mat.decal_modulator), output_folder) + "\n"

            #Write the decals
            if len(mat.decals) > 0:
                output += "#Decals\n"
                for decal in mat.decals:
                    #Get the decal command
                    decal_command = decal_utils.get_decal_command(decal, output_folder)
                    if decal_command:
                        output += decal_command

                output += "\n"

            #Blend mode
            if mat.blend_mode == "CLIP":
                output += "NO_BLEND " + str(mat.blend_cutoff) + "\n"

            #Shadows
            if not mat.cast_shadow:
                output += "NO_SHADOW\n"

            #Layer group
            output += "LAYER_GROUP " + str(self.export_wall_layer_group) + " " + str(self.export_wall_layer_group_offset) + "\n"

            output += "\n"
        elif not self.do_wall_mesh:
            output += "NO_WALL_MESH\n"
        #Roof shader
        if self.roof_material is not None and self.do_roof_mesh:
            output += "SHADER_ROOF\nNORMAL_METALNESS\n"

            mat = self.roof_material.xp_materials

            if mat.do_separate_material_texture:
                log_utils.error("Error: X-Plane does not support separate material textures on lines/polygons/facades. Please use a normal map with the metalness and glossyness in the blue and alpha channels respectively.")
                return

            #Textures
            if mat.alb_texture != "":
                output += "TEXTURE " + os.path.relpath(file_utils.to_absolute(mat.alb_texture), output_folder) + "\n"
            if mat.lit_texture != "":
                output += "TEXTURE_LIT " + os.path.relpath(file_utils.to_absolute(mat.lit_texture), output_folder) + "\n"
            if mat.normal_texture != "":
                output += "TEXTURE_NORMAL " + str(mat.normal_tile_ratio) + " " + os.path.relpath(file_utils.to_absolute(mat.normal_texture), output_folder)+ "\n"
            if mat.decal_modulator != "":
                output += "TEXTURE_MODULATOR " + os.path.relpath(file_utils.to_absolute(mat.decal_modulator), output_folder) + "\n"

            #Write the decals
            if len(mat.decals) > 0:
                output += "#Decals\n"
                for decal in mat.decals:
                    #Get the decal command
                    decal_command = decal_utils.get_decal_command(decal, output_folder)
                    if decal_command:
                        output += decal_command

                output += "\n"

            #Blend mode
            if mat.blend_mode == "CLIP":
                output += "NO_BLEND " + str(mat.blend_cutoff) + "\n"

            #Shadows
            if not mat.cast_shadow:
                output += "NO_SHADOW\n"

            #Layer group
            output += "LAYER_GROUP " + str(self.export_roof_layer_group) + " " + str(self.export_roof_layer_group_offset) + "\n"
            
            #Draped layer group. We only do this if draped
            if not self.graded:
                output += "LAYER_GROUP_DRAPED " + str(self.export_roof_layer_group) + " " + str(self.export_roof_layer_group_offset) + "\n"

            #Hard
            if mat.surface_type != "NONE":
                roof_surface = mat.surface_type
        elif not self.do_roof_mesh:
            output += "NO_ROOF_MESH\n"
        #Roof scale
        output += "ROOF_SCALE " + str(self.roof_scale_x) + " " + str(self.roof_scale_y) + "\n\n"

        #All objects
        all_objects = []
        for cur_floor in self.floors:
            cur_floor.append_obj_resources(all_objects)
        
        all_objects = list(set(all_objects)) #Dedup the list of objects
        all_objects.sort() #Sort the list of objects. We do this to avoid changes in the order of objects, which would make our output slightly non-deterministic, and therefore invalid for testing

        for obj in all_objects:
            output += "OBJ " + obj + "\n"

        #Floors
        for cur_floor in self.floors:
            output += "FLOOR " + cur_floor.name + "\n"

            #Add the hard roof command if we have a roof surface
            if roof_surface != "":
                output += "HARD_ROOF " + str(roof_surface).lower() + "\n"

            #First step is to add all the roof data
            if cur_floor.roof_two_sided:
                output += "ROOF_TWO_SIDED\n"
            
            for level in cur_floor.roof_heights:
                output += "ROOF_HEIGHT " + str(level) + "\n"

            for obj in cur_floor.roof_objs:
                obj_index = all_objects.index(obj.resource)
                output += "ROOF_OBJ_HEADING " + str(obj_index) + " " + misc_utils.ftos(obj.rot_z, 4) + " " + misc_utils.ftos(obj.loc_x, 8) + " " + misc_utils.ftos(obj.loc_z, 8) + " " + str(obj.min_draw) + " " + str(obj.max_draw) + "\n"
            
            #Now we need to add all the segment definitions
            def write_mesh(target_mesh):
                output = ""
                output += "MESH " + str(target_mesh.group) + " " + str(target_mesh.far_lod) + " " + str(len(target_mesh.vertices)) + " " + str(len(target_mesh.indices)) + "\n"

                #X-Plane facades are *very* weird. They scale the wall mesh by -1 on their z axis (our y). So we need to do the same here so XP appears the same as blender - 0y being the start of the wall

                for v in target_mesh.vertices:
                    output += "VERTEX " + misc_utils.ftos(v.loc_x, 8) + " " + misc_utils.ftos(v.loc_z, 8) + " " + misc_utils.ftos(-v.loc_y, 8) + " " + misc_utils.ftos(v.normal_x, 8) + " " + misc_utils.ftos(v.normal_z, 8) + " " + misc_utils.ftos(-v.normal_y, 8) + " " + misc_utils.ftos(v.uv_x, 8) + " " + misc_utils.ftos(v.uv_y, 8) + "\n"
                cur_idx = 0

                #Since we had to scale by -1 for Y, we need to reverse the indicies to fix the face direction
                temp_indicies = [i for i in reversed(target_mesh.indices)]  # Reverse the indices to fix face direction

                while cur_idx < len(temp_indicies):
                    if cur_idx % 10 == 0:
                        output += "IDX "

                    output += str(temp_indicies[cur_idx])

                    if cur_idx % 10 == 9 or cur_idx == len(temp_indicies) - 1:
                        output += "\n"
                    else:
                        output += " "
                    
                    cur_idx += 1
                return output
            
            def write_segment(target_segment, seg_idx, is_curved):
                output = ""
                output += "# " + target_segment.name + "\n"
                if is_curved:
                    output += "SEGMENT_CURVED " + str(seg_idx) + "\n"
                else:    
                    output += "SEGMENT " + str(seg_idx) + "\n"
                for cur_mesh in target_segment.meshes:
                    output += write_mesh(cur_mesh)
                for obj in target_segment.attached_objects:
                    idx = all_objects.index(obj.resource)
                    if obj.draped:
                        output += "ATTACH_DRAPED " + str(idx) + " " + misc_utils.ftos(obj.loc_x, 8) + " " + misc_utils.ftos(obj.loc_z, 8) + " " + misc_utils.ftos(obj.loc_y, 8) + " " + misc_utils.ftos(misc_utils.resolve_heading(obj.rot_z + 180), 4) + " " + str(obj.min_draw) + " " + str(obj.max_draw) + "\n"
                    else:
                        output += "ATTACH_GRADED " + str(idx) + " " + misc_utils.ftos(obj.loc_x, 8) + " " + misc_utils.ftos(obj.loc_z, 8) + " " + misc_utils.ftos(obj.loc_y, 8) + " " + misc_utils.ftos(misc_utils.resolve_heading(obj.rot_z + 180), 4) + " " + str(obj.min_draw) + " " + str(obj.max_draw) + "\n"
                return output + "\n"

            cur_seg_idx = 0
            for cur_seg in cur_floor.all_segments:
                output += write_segment(cur_seg, cur_seg_idx, False)
                cur_seg_idx += 1

            output += "\n"

            cur_seg_idx = 0
            for cur_seg in cur_floor.all_curved_segments:
                output += write_segment(cur_seg, cur_seg_idx, True)
                cur_seg_idx += 1

            output += "\n"

            #Now we need to add all the wall rules
            for cur_wall in cur_floor.walls:
                
                output += "WALL " + str(cur_wall.min_length) + " " + str(cur_wall.max_length) + " " + str(cur_wall.min_heading) + " " + str(cur_wall.max_heading) + " " + cur_wall.name + "\n"

                for cur_spelling in cur_wall.spellings:

                    output += "SPELLING "
                    for seg_name in cur_spelling.segment_names:

                        idx_cur_wall = -1
                        for possible_idx, possible_wall in enumerate(cur_floor.all_segments):
                            if possible_wall.name == seg_name:
                                idx_cur_wall = possible_idx
                                break

                        if idx_cur_wall == -1:
                            log_utils.error("Could not find wall: " + seg_name + " in spelling for wall: " + cur_wall.name + ". Maybe it was deleted?")
                            return

                        output += str(idx_cur_wall) + " "
                    output += "\n"

                output += "\n"

        #Now output contains the contents of the full facade file, soo, now we just need to write it to the file
        with open(out_path, "w") as f:
            f.write(output)
            f.close()

    def from_collection(self, in_collection):

        log_utils.new_section(f"Reading .fac collection {in_collection.name}")

        fac = in_collection.xp_fac

        #Set the general properties
        self.name = fac.name
        if self.name == "":
            self.name = in_collection.name
        self.do_roof_mesh = fac.render_roof
        self.do_wall_mesh = fac.render_wall
        self.wall_material = fac.wall_material
        self.roof_material = fac.roof_material
        self.graded = fac.graded
        self.ring = fac.ring
        
        #Layer groups
        if self.wall_material != None:
            self.export_wall_layer_group = self.wall_material.xp_materials.layer_group
            self.export_wall_layer_group_offset = self.wall_material.xp_materials.layer_group_offset
        if self.roof_material != None:
            self.export_roof_layer_group = self.roof_material.xp_materials.layer_group
            self.export_roof_layer_group_offset = self.roof_material.xp_materials.layer_group_offset

        #Get the floors
        for f in in_collection.xp_fac.floors:
            cur_floor = floor()
            cur_floor.from_floor_props(f)
            self.floors.append(cur_floor)

        #Make sure we have at least one floor
        if len(self.floors) == 0:
            log_utils.error("No floors found in facade: " + self.name)

        #Get the roof scale from the first floor.
        self.roof_scale_x = self.floors[0].roof_scale_x
        self.roof_scale_y = self.floors[0].roof_scale_y

    def to_scene(self):
        """
        Converts the facade object into a Blender scene.
        This method should be called after the `read` function to populate the scene with the facade's data.
        """

        log_utils.new_section(f"Creating .fac collection {self.name}")

        # Create a new collection for the facade
        facade_collection = bpy.data.collections.new(self.name)
        bpy.context.scene.collection.children.link(facade_collection)

        # Set facade properties
        facade_props = facade_collection.xp_fac
        facade_props.exportable = True
        facade_props.name = self.name
        facade_props.wall_material = self.wall_material
        facade_props.roof_material = self.roof_material
        facade_props.render_wall = self.do_wall_mesh
        facade_props.render_roof = self.do_roof_mesh
        facade_props.graded = self.graded
        facade_props.ring = self.ring

        # Set wall and roof materials
        if self.import_wall_material:
            wall_material = bpy.data.materials.new(name="WallMaterial")
            wall_material.use_nodes = True
            wall_material.xp_materials.alb_texture = self.import_wall_material.alb_texture
            wall_material.xp_materials.normal_texture = self.import_wall_material.nml_texture
            wall_material.xp_materials.lit_texture = self.import_wall_material.lit_texture
            wall_material.xp_materials.decal_modulator = self.import_wall_material.mod_texture
            wall_material.xp_materials.blend_mode = 'BLEND' if self.import_wall_material.do_blend_alpha else 'CLIP'
            wall_material.xp_materials.blend_cutoff = self.import_wall_material.alpha_cutoff
            wall_material.xp_materials.cast_shadow = self.import_wall_material.cast_shadow
            wall_material.xp_materials.layer_group = self.import_wall_material.layer_group.upper()
            wall_material.xp_materials.layer_group_offset = self.import_wall_material.layer_group_offset
            self.wall_material = wall_material

            decal_alb_index = 0
            decal_nml_index = 2

            material_config.update_settings(wall_material)

            for decal in self.import_wall_material.imported_decal_commands:
                if decal.startswith("NORMAL"):
                    if decal_nml_index > 3:
                        log_utils.warning("Error: Too many normal decals! X-Plane only supports 2 normal decals per material.")
                        break
                    decal_utils.get_decal_from_command(decal, wall_material.xp_materials.decals[decal_nml_index])
                    decal_nml_index += 1
                else:
                    if decal_alb_index > 2:
                        log_utils.warning("Error: Too many albedo decals! X-Plane only supports 2 decals per material.")
                        break
                    decal_utils.get_decal_from_command(decal, wall_material.xp_materials.decals[decal_alb_index])
                    decal_alb_index += 1

            material_config.update_settings(wall_material)

            facade_props.wall_material = wall_material
            
        if self.import_roof_material:
            roof_material = bpy.data.materials.new(name="RoofMaterial")
            roof_material.use_nodes = True
            roof_material.xp_materials.alb_texture = self.import_roof_material.alb_texture
            roof_material.xp_materials.normal_texture = self.import_roof_material.nml_texture
            roof_material.xp_materials.lit_texture = self.import_roof_material.lit_texture
            roof_material.xp_materials.decal_modulator = self.import_roof_material.mod_texture
            roof_material.xp_materials.blend_mode = 'BLEND' if self.import_roof_material.do_blend_alpha else 'CLIP'
            roof_material.xp_materials.blend_cutoff = self.import_roof_material.alpha_cutoff
            roof_material.xp_materials.cast_shadow = self.import_roof_material.cast_shadow
            roof_material.xp_materials.layer_group = self.import_roof_material.layer_group.upper()
            roof_material.xp_materials.layer_group_offset = self.import_roof_material.layer_group_offset
            self.roof_material = roof_material

            decal_alb_index = 0
            decal_nml_index = 2

            material_config.update_settings(roof_material)

            for decal in self.import_roof_material.imported_decal_commands:
                if decal.startswith("NORMAL"):
                    if decal_nml_index > 3:
                        log_utils.warning("Error: Too many normal decals! X-Plane only supports 2 normal decals per material.")
                        break
                    decal_utils.get_decal_from_command(decal, roof_material.xp_materials.decals[decal_nml_index])
                    decal_nml_index += 1
                else:
                    if decal_alb_index > 2:
                        log_utils.warning("Error: Too many albedo decals! X-Plane only supports 2 decals per material.")
                        break
                    decal_utils.get_decal_from_command(decal, roof_material.xp_materials.decals[decal_alb_index])
                    decal_alb_index += 1

            material_config.update_settings(roof_material)

            facade_props.roof_material = roof_material
        # Add floors to the collection
        for floor_obj in self.floors:
            # Create a collection for the floor
            floor_collection = bpy.data.collections.new(floor_obj.name)
            facade_collection.children.link(floor_collection)

            # Add segments
            for segment in floor_obj.all_segments:
                segment_collection = segment.to_collection(segment.name, self.wall_material)
                floor_collection.children.link(segment_collection)

            for curved_segment in floor_obj.all_curved_segments:
                curved_segment_collection = curved_segment.to_collection(curved_segment.name + "_Curved", self.wall_material)
                floor_collection.children.link(curved_segment_collection)

            # Set roof properties
            facade_props.floors.add()
            floor_props = facade_props.floors[-1]
            floor_obj.to_floor_props(floor_props)

            #Create the roof collection
            roof_collection = bpy.data.collections.new(floor_obj.name + "_roof")
            floor_collection.children.link(roof_collection)

            #Create planes that are the size of the roof, one at each floor height, and link them to the roof collection. 
            for i, height in enumerate(floor_obj.roof_heights):
                verts = [geometery_utils.xp_vertex(0, 0, 0, 0, 0, 1, 0, 0),
                        geometery_utils.xp_vertex(0, self.roof_scale_y, 0, 0, 0, 1, 0, 1),
                        geometery_utils.xp_vertex(self.roof_scale_x, 0, 0, 0, 0, 1, 1, 0),
                        geometery_utils.xp_vertex(self.roof_scale_x, self.roof_scale_y, 0, 0, 0, 1, 1, 1),]
                indicies = [0, 2, 1, 2, 3, 1]
                roof_obj = geometery_utils.create_obj_from_draw_call(verts, indicies, "Roof_" + str(i))
                roof_obj.location.z = height
                roof_obj.data.materials.append(self.roof_material)
                roof_collection.objects.link(roof_obj)

            for roof_obj in floor_obj.roof_objs:
                obj = roof_obj.to_obj(roof_obj.resource)
                roof_collection.objects.link(obj)



