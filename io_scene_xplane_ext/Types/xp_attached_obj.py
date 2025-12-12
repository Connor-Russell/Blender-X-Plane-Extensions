#Project: Blender-X-Plane-Extensions
#Author: Connor Russell
#Date: 11/9/2024
#Module: xp_attached_obj.py
#Purpose: Provide a class to hold data for X-Plane Facade attached objects.
#TODO: This is a little messy and probably unnecessary, we may be able to get rid of this entirely and embed it directly in the .fac code

#Blender modules
import collections
import math
import mathutils #type: ignore
import bpy #type: ignore
import bmesh #type: ignore

from mathutils import Matrix
from mathutils import Vector
from mathutils import Euler


#Our modules
from ..Helpers import geometery_utils
from ..Helpers import misc_utils
from ..Helpers import file_utils

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

        self.preview_path = ""

    def read_from_obj(self, obj):
        #Make sure this is an empty object, is exportable, and has a resource defined.
        if obj.type != "EMPTY":
            return
        if not obj.xp_attached_obj.exportable or obj.xp_attached_obj.resource == "":
            return

        self.resource = obj.xp_attached_obj.resource
        self.draped = obj.xp_attached_obj.draped
        self.preview_path = obj.xp_attached_obj.attached_obj_preview_resource

        # Get local transform matrix
        local_matrix = obj.matrix_local.copy()

        # Apply parent transform if exists
        if obj.parent:
            local_matrix = obj.parent.matrix_world @ local_matrix

        # Apply reflection across Y axis
        S = Matrix.Scale(-1, 4, Vector((0, 1, 0)))
        reflected_matrix = S @ local_matrix @ S

        # Extract location
        loc = reflected_matrix.to_translation()
        self.loc_x = loc.x
        self.loc_y = loc.y  # Invert Y for X-Plane
        self.loc_z = loc.z

        # Extract rotation
        rot_euler = reflected_matrix.to_euler('XYZ')
        self.rot_x = math.degrees(rot_euler.x)
        self.rot_y = math.degrees(rot_euler.y)
        self.rot_z = math.degrees(rot_euler.z) + 180  # Invert Y axis rotation for X-Plane

        self.valid = True

    def to_obj(self, name):
        obj = bpy.data.objects.new(name, None)

        # Invert Y axis back
        obj.location = (self.loc_x, -self.loc_y, self.loc_z)

        # Step 1: Subtract the 180° correction
        corrected_euler = Euler((
            math.radians(self.rot_x),
            math.radians(self.rot_y),
            math.radians(self.rot_z - 180)  # Assuming Z was the axis corrected
        ), 'XYZ')

        # Step 2: Apply reflection matrix again to undo the conjugation
        R = corrected_euler.to_matrix().to_3x3()
        S = Matrix.Scale(-1, 3, Vector((0, 1, 0)))
        R_unflipped = S @ R @ S

        # Step 3: Convert back to Euler
        final_euler = R_unflipped.to_euler('XYZ')
        obj.rotation_euler = final_euler

        # Final setup
        obj.empty_display_type = 'ARROWS'
        obj.xp_attached_obj.exportable = True
        obj.xp_attached_obj.resource = self.resource
        obj.xp_attached_obj.draped = self.draped

        if self.preview_path != "":
            obj.xp_attached_obj.attached_obj_preview_resource = file_utils.to_relative(self.preview_path)

        return obj

