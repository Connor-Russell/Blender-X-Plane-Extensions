#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide utility functions to help in extracting the geometry and attached objects from the individual objects in a layer.

#Blender modules
import collections
import math
import mathutils #type: ignore
import bpy #type: ignore
import bmesh #type: ignore

#Our modules
from ..Helpers import geometery_utils
from ..Helpers import misc_utils

#Simple container to hold attached object data  
class xp_attached_obj:
    #Class variables
    all_objects = []    #List of all objects in the scene. This is used to get the index of the object in the list.

    #Define instance varialbes
    def __init__(self):
        self.loc_x = 0
        self.loc_y = 0
        self.loc_z = 0

        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 0

        self.draped = False  #This defaults to graded. If true, the object is draped.

        self.resource = ""  #The path to the object

        self.min_draw = 0
        self.max_draw = 0

        self.valid = False

    #Reads the data from an object
    def read_from_obj(self, obj):
        #Check to make sure this is an empty
        if obj.type != "EMPTY":
            return

        #Check if this object is exportable
        if not obj.xp_attached_obj.exportable:
            return
            
        #If the object has the 'FacadeObj' Property, get the value, otherwise return None
        if obj.xp_attached_obj.resource == "":
            return
        self.resource = obj.xp_attached_obj.resource

        #Get the draped
        self.draped = obj.xp_attached_obj.draped

        # Get the object's location and rotation
        self.loc_x = obj.location.x
        self.loc_y = obj.location.y
        self.loc_z = obj.location.z

        self.rot_x = obj.rotation_euler.x
        self.rot_y = obj.rotation_euler.y
        self.rot_z = obj.rotation_euler.z

        #Check if there is a parent. If so, we'll get it's transforms and apply that to the loc/rot
        if obj.parent != None:
            parent_transform = obj.parent.matrix_world

            # Get the local position as a vector
            local_position = mathutils.Vector((self.loc_x, self.loc_y, self.loc_z))

            # Apply the full transformation
            transformed_position = parent_transform @ local_position

            # Extract the rotation as Euler angles
            rotation = parent_transform.to_euler()

            # Set the new position and rotation
            self.loc_x = transformed_position.x
            self.loc_y = transformed_position.y
            self.loc_z = transformed_position.z

            self.rot_x = rotation.x
            self.rot_y = rotation.y
            self.rot_z = rotation.z

        #Convert the rotation to degrees
        self.rot_x = math.degrees(self.rot_x)
        self.rot_y = math.degrees(self.rot_y)
        self.rot_z = math.degrees(self.rot_z)

        self.valid = True
    
    def to_obj(self, name):
        # Create a new empty object
        obj = bpy.data.objects.new(name, None)
        #obj.type = 'EMPTY'

        # Set the object's location and rotation
        obj.location = (self.loc_x, self.loc_y, self.loc_z)
        obj.rotation_euler = (
            math.radians(self.rot_x),
            math.radians(self.rot_y),
            math.radians(self.rot_z)
        )

        # Set the object's display type to plain axes
        obj.empty_display_type = 'PLAIN_AXES'

        # Set custom properties for exportable and resource
        obj.xp_attached_obj.exportable = True
        obj.xp_attached_obj.resource = self.resource
        obj.xp_attached_obj.draped = self.draped

        # Return the created object
        return obj
