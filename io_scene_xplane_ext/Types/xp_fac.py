#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      4/18/2025
#Module:    Export
#Purpose:   Provide classes that abstracts the X-Plane facade format

from ..Helpers import facade_utils # type: ignore
from ..Helpers import geometery_utils # type: ignore

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
        self.far_lod = obj.xp_attached_obj.far_lod
        self.group = obj.xp_attached_obj.group
        self.cuts = obj.xp_attached_obj.cuts

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
            for spelling in wall_rule.spellings:
                cur_spelling = spelling()
                for entry in spelling.entries:
                    all_segments_names.append(entry.collection)
                    cur_spelling.segment_names.append(entry.collection)

                cur_wall.spellings.append(cur_spelling)
            
            self.walls.append(cur_wall)

        #Dedup the list of segments
        all_segments_names = list(set(all_segments_names))

        #Iterate over all the segments and get their geometry
        for segment in all_segments_names:
            #Find this collection in the scene
            col = None
            for c in bpy.data.collections:
                if c.name == segment:
                    col = c
                    break

            if col is None:
                print("Could not find collection: " + segment)
                raise Exception("Could not find collection: " + segment + " Maybe it was deleted?")

            cur_segment = segment()
            cur_segment.from_collection(segment)
            self.all_segments.append(cur_segment)

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
        self.roof_scale_x, self.roof_scale_y, self.roof_objs, self.roof_heights = facade_utils.get_roof_scale_and_objects(roof_col)

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
        self.solid = False
        self.graded = False
        self.ring = False

    def read(self, in_path):
        #Todo
        pass

    def write(self, out_path):
        #Todo
        pass

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
        self.solid = fac.solid
        self.graded = fac.graded
        self.ring = fac.ring

        #Get the floors
        for f in in_collection.floors:
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
        