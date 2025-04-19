#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      4/18/2025
#Module:    Export
#Purpose:   Provide classes that abstracts the X-Plane facade format

from ..Helpers import facade_utils # type: ignore
from ..Helpers import geometery_utils # type: ignore

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

class floor:
    def __init__(self):
        self.name = ""  #Name of the floor, debug purposes only
        self.all_segments = []  #Object containing all segments in this floor. They are referenced by name.
        self.roof_objs = [] #List of all roof objects. These are xp_attached_obj objects.
        self.floor_height = 0
        self.segment_names = []  #List of all segment names in this floor
        #TODO: Define the spelling system for the floor. This will be used for choosing segments.

    def from_collection(self, collection):

        #Get the name of the collection
        self.name = collection.name

        #Iterate over all objects in the collection. If it starts with "Roof" we will process it as a roof. Otherwise we will process it as a segment.

class facade:
    def __init__(self):
        self.name = "" #Name of the facade, relative to the blender file
        self.floors = []        #List of all floors in this facade. These are xp_floor objects.
        self.roof_scale_x = 0   #Meters
        self.roof_scale_y = 0   #Meters
        self.do_wall_mesh = True    #If true, the wall mesh will be generated. If false, the wall mesh will not be generated.
        self.do_roof_mesh = True    #If true, the roof mesh will be generated. If false, the roof mesh will not be generated.
        self.wall_material = None   #This is a PROP_mats (bpy.types.Material.xp_materials)
        self.roof_material = None   #This is a PROP_mats (bpy.types.Material.xp_materials)

    def read(self, in_path):
        #Todo
        pass

    def write(self, out_path):
        #Todo
        pass

    def from_scene(self):
        #Todo
        pass

    def to_scene(self):
        #Todo
        pass
        