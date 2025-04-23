#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      4/18/2025
#Module:    Export
#Purpose:   Provide classes that abstracts the X-Plane facade format

from ..Helpers import facade_utils # type: ignore
from ..Helpers import geometery_utils # type: ignore
from ..Helpers import decal_utils # type: ignore
from ..Helpers import file_utils # type: ignore
from ..Helpers import misc_utils # type: ignore
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
                attached_obj = attached_obj.xp_attached_obj()
                attached_obj.read_from_obj(obj)

                if attached_obj.valid:
                    self.attached_objects.append(attached_obj)

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

        #Iterate over all the segments and get their geometry
        for cur_segment in all_segments_names:
            #Find this collection in the scene
            col = None
            for c in bpy.data.collections:
                if c.name == cur_segment:
                    col = c
                    break

            if col is None:
                print("Could not find collection: " + cur_segment)
                raise Exception("Could not find collection: " + cur_segment + " Maybe it was deleted?")
            
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
            print("Could not find roof collection: " + self.name + "_roof")
            raise Exception("Could not find roof collection: " + self.name + "_roof")
        
        #Get the roof params
        self.roof_scale_x, self.roof_scale_y, self.roof_objs, self.roof_heights = facade_utils.get_roof_data(roof_col)

    def append_obj_resources(self, target_list):
        for seg in self.all_segments:
            seg.append_obj_resources(target_list)
        for obj in self.roof_objs:
            target_list.append(obj.resource)
            
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
        self.graded = False
        self.ring = False

    def read(self, in_path):
        #Todo
        pass

    def write(self, out_path):

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

        #Wall shader
        if self.wall_material is not None and self.do_wall_mesh:
            output += "SHADER_WALL\n"

            mat = self.wall_material.xp_materials

            #Textures
            if mat.alb_texture != "":
                output += "TEXTURE " + os.path.relpath(file_utils.rel_to_abs(mat.alb_texture), output_folder) + "\n"
            if mat.lit_texture != "":
                output += "TEXTURE_LIT " + os.path.relpath(file_utils.rel_to_abs(mat.lit_texture), output_folder) + "\n"
            if mat.normal_texture != "":
                output += "TEXTURE_NORMAL " + os.path.relpath(file_utils.rel_to_abs(mat.normal_texture), output_folder)+ "\n"
            if mat.decal_modulator != "":
                output += "TEXTURE_MODULATOR " + os.path.relpath(file_utils.rel_to_abs(mat.decal_modulator), output_folder) + "\n"

            #Blend mode
            if not mat.blend_alpha:
                output += "NO_BLEND " + str(mat.blend_cutoff) + "\n"

            #Shadows
            if not mat.cast_shadow:
                output += "NO_SHADOW\n"

            #Layer group
            output += "LAYER_GROUP " + str(mat.layer_group) + " " + str(mat.layer_group_offset) + "\n"

            #Decal settings
            if mat.decal_one.enabled:
                output += decal_utils.get_decal_command(mat.decal_one, output_folder) + "\n"
            if mat.decal_two.enabled:
                output += decal_utils.get_decal_command(mat.decal_two, output_folder) + "\n"
            
            output += "\n"
        
        #Roof shader
        if self.roof_material is not None and self.do_roof_mesh:
            output += "SHADER_ROOF\n"

            mat = self.roof_material.xp_materials

            #Textures
            if mat.alb_texture != "":
                output += "TEXTURE " + os.path.relpath(file_utils.rel_to_abs(mat.alb_texture), output_folder) + "\n"
            if mat.lit_texture != "":
                output += "TEXTURE_LIT " + os.path.relpath(file_utils.rel_to_abs(mat.lit_texture), output_folder) + "\n"
            if mat.normal_texture != "":
                output += "TEXTURE_NORMAL " + os.path.relpath(file_utils.rel_to_abs(mat.normal_texture), output_folder)+ "\n"
            if mat.decal_modulator != "":
                output += "TEXTURE_MODULATOR " + os.path.relpath(file_utils.rel_to_abs(mat.decal_modulator), output_folder) + "\n"

            #Blend mode
            if not mat.blend_alpha:
                output += "NO_BLEND " + str(mat.blend_cutoff) + "\n"

            #Shadows
            if not mat.cast_shadow:
                output += "NO_SHADOW\n"

            #Layer group
            output += "LAYER_GROUP " + str(mat.layer_group) + " " + str(mat.layer_group_offset) + "\n"
            
            #Draped layer group. We only do this if draped
            if not self.graded:
                output += "LAYER_GROUP_DRAPED " + str(mat.layer_group) + " " + str(mat.layer_group_offset) + "\n"

            #Decal settings
            if mat.decal_one.enabled:
                output += decal_utils.get_decal_command(mat.decal_one, output_folder) + "\n"
            if mat.decal_two.enabled:
                output += decal_utils.get_decal_command(mat.decal_two, output_folder) + "\n"

            #Hard
            if mat.hard:
                output += "ROOF_HARD concrete\n"

        #Roof scale
        output += "ROOF_SCALE " + str(self.roof_scale_x) + " " + str(self.roof_scale_y) + "\n\n"

        #All objects
        all_objects = []
        for cur_floor in self.floors:
            cur_floor.append_obj_resources(all_objects)
        
        all_objects = list(set(all_objects)) #Dedup the list of objects

        for obj in all_objects:
            output += "OBJ " + obj + "\n"

        #Floors
        for cur_floor in self.floors:
            output += "FLOOR " + cur_floor.name + "\n"
            
            #First step is to add all the roof data
            if cur_floor.roof_two_sided:
                output += "ROOF_TWO_SIDED\n"
            
            for level in cur_floor.roof_heights:
                output += "ROOF_HEIGHT " + str(level) + "\n"

            for obj in cur_floor.roof_objs:
                obj_index = all_objects.index(obj.resource)
                output += "ROOF_OBJ_HEADING " + str(obj_index) + " " + misc_utils.ftos(obj.heading, 4) + " " + misc_utils.ftos(obj.loc_x, 8) + " " + misc_utils.ftos(obj.loc_z, 8) + " " + str(obj.min_draw) + " " + str(obj.max_draw) + "\n"
            
            #Now we need to add all the segment definitions
            def write_mesh(target_mesh):
                output = ""
                output += "MESH " + str(target_mesh.group) + " " + str(target_mesh.far_lod) + " " + str(len(target_mesh.vertices)) + " " + str(len(target_mesh.indices)) + "\n"
                for v in target_mesh.vertices:
                    output += "VERTEX " + misc_utils.ftos(v.loc_x, 8) + " " + misc_utils.ftos(v.loc_z, 8) + " " + misc_utils.ftos(v.loc_y, 8) + " " + misc_utils.ftos(v.normal_x, 8) + " " + misc_utils.ftos(v.normal_z, 8) + " " + misc_utils.ftos(v.normal_y, 8) + " " + misc_utils.ftos(v.uv_x, 8) + " " + misc_utils.ftos(v.uv_y, 8) + "\n"
                cur_idx = 0
                while cur_idx < len(target_mesh.indices):
                    if cur_idx % 10 == 0:
                        output += "IDX "
                    
                    output += str(target_mesh.indices[cur_idx])

                    if cur_idx % 10 == 9:
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
                        output += "ATTACH_DRAPED " + str(idx) + " " + misc_utils.ftos(obj.loc_x, 8) + " " + misc_utils.ftos(obj.loc_z, 8) + " " + misc_utils.ftos(obj.loc_y, 8) + " " + misc_utils.ftos(obj.heading, 4) + " " + str(obj.min_draw) + " " + str(obj.max_draw) + "\n"
                    else:
                        output += "ATTACH_GRADED " + str(idx) + " " + misc_utils.ftos(obj.loc_x, 8) + " " + misc_utils.ftos(obj.loc_z, 8) + " " + misc_utils.ftos(obj.loc_y, 8) + " " + misc_utils.ftos(obj.heading, 4) + " " + str(obj.min_draw) + " " + str(obj.max_draw) + "\n"
                return output + "\n"

            cur_seg_idx = 0
            for cur_seg in cur_floor.all_segments:
                output += write_segment(cur_seg, cur_seg_idx, False)
                cur_seg_idx += 1

            output += "\n"

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
                            print("Could not find wall: " + seg_name + " in spelling for wall: " + cur_wall.name + ". Maybe it was deleted?")
                            raise Exception("Could not find wall: " + seg_name + " in spelling for wall: " + cur_wall.name + ". Maybe it was deleted?")

                        output += str(idx_cur_wall) + " "
                    output += "\n"

                output += "\n"

        #Now output contains the contents of the full facade file, soo, now we just need to write it to the file
        with open(out_path, "w") as f:
            f.write(output)
            f.close()

    def from_collection(self, in_collection):
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

        #Get the floors
        for f in in_collection.xp_fac.floors:
            cur_floor = floor()
            cur_floor.from_floor_props(f)
            self.floors.append(cur_floor)

        #Make sure we have at least one floor
        if len(self.floors) == 0:
            print("No floors found in facade: " + self.name)
            raise Exception("No floors found in facade: " + self.name)

        #Get the roof scale from the first floor.
        self.roof_scale_x = self.floors[0].roof_scale_x
        self.roof_scale_y = self.floors[0].roof_scale_y


    def to_scene(self):
        #Todo
        pass
        