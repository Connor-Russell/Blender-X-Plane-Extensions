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
from . import GeometryUtils
from . import MiscUtils

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

        self.roof_obj = False

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
    
    #Resets the all objects list
    def reset_objects():
        xp_attached_obj.all_objects = []

    #Sorts and deduplicates the all objects list
    def prep_object_list():
        xp_attached_obj.all_objects.sort()

        #Iterate through the list (except for the last item) adn remove duplicates
        i = 0
        while i < len(xp_attached_obj.all_objects) - 1:
            if xp_attached_obj.all_objects[i] == xp_attached_obj.all_objects[i + 1]:
                xp_attached_obj.all_objects.pop(i)
            else:
                i += 1

    #Adds an object to the list of all objects so we can get it's index later
    def add_object_to_list(obj):
        #Make sure this is an empty
        if obj.type != "EMPTY":
            return
        
        #Check if it is exportable
        if not obj.xp_attached_obj.exportable:
            return
        
        #Check if it has the obj resource
        if obj.xp_attached_obj.resource == "":
            return
        
        #Get and store the resource
        resource = obj.xp_attached_obj.resource
        xp_attached_obj.all_objects.append(resource)
        

    #Get the string representation of this object
    def get_string(self):
        out = ""
        if self.roof_obj:
            out += "ROOF_OBJ_HEADING "
        elif self.draped:
            out += "ATTACH_DRAPED "
        else:
            out += "ATTACH_GRADED "

        #Get the index of this object's resource in the list of all objects
        try:
            index = MiscUtils.linear_search_list(xp_attached_obj.all_objects, self.resource)
        except ValueError:
            print("Error: Resource not found in list of all objects. Number of object in list:" + str(len(xp_attached_obj.all_objects)))
            index = 0

        #Add the data index, x, y, z, rot_z, min_draw, max_draw
        if self.roof_obj:
            out += str(index) + " " + MiscUtils.ftos(self.loc_x, 8) + " " + MiscUtils.ftos(self.loc_y, 8) + " " + MiscUtils.ftos(MiscUtils.resolve_heading(self.rot_z * -1), 4) + " " + str(self.min_draw) + " " + str(self.max_draw)
        else:
            out += str(index) + " " + MiscUtils.ftos(self.loc_x, 8) + " " + MiscUtils.ftos(self.loc_z, 8) + " " + MiscUtils.ftos(self.loc_y, 8) + " " + MiscUtils.ftos(MiscUtils.resolve_heading(self.rot_z + 180), 3) + " " + str(self.min_draw) + " " + str(self.max_draw)

        return out

