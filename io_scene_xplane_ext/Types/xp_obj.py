#Project:   Blender X-Plane Extensions
#Author:    Connor Russell
#Date:      4-24/2025
#Module:    xp_obj.py
#Purpose:   Provide a class that abstracts the X-Plane object, and provides functions to import the object into Blender

import bpy
import os

from ..Helpers import geometery_utils

class anim_loc_keyframe:
    """
    Class to represent a keyframe for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self, time, loc):
        self.time = time  #Time of the keyframe
        self.loc = loc  #Location of the keyframe

class anim_rot_keyframe:
    """
    Class to represent a keyframe for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self, time, rot):
        self.time = time  #Time of the keyframe
        self.rot = rot  #Rotation of the keyframe

class anim_rot_table:
    """
    Class to represent a table of keyframes for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self, name):
        self.name = name  #Name of the animation
        self.keyframes = []  #List of keyframes for the animation

    def add_keyframe(self, time, rot):
        #Add a keyframe to the list of keyframes
        kf = anim_rot_keyframe(time, rot)
        self.keyframes.append(kf)

class anim_loc_table:
    """
    Class to represent a table of keyframes for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self, name):
        self.name = name  #Name of the animation
        self.keyframes = []  #List of keyframes for the animation

    def add_keyframe(self, time, loc):
        #Add a keyframe to the list of keyframes
        kf = anim_loc_keyframe(time, loc)
        self.keyframes.append(kf)

class anim_level:
    """
    Class to represent a level of animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self, name):
        self.driver #This is an empty that all children are linked to. This is what is keyframed and "drives" the animation
        self.static_loc_keyframes = []  #List of static location keyframes for the animation
        self.static_rot_keyframes = []  #List of static rotation keyframes for the animation
        self.loc_tables = []  #List of location tables for the animation
        self.rot_tables = []  #List of rotation tables for the animation
        self.draw_calls = []  #List of draw calls for the animation
        self.children = []  #List of children anim_levels for the animation

class object:
    """
    Class to represent an X-Plane object. This class provides functions to import the object into Blender.
    """

    #Class variables
    all_objects = []  #List of all objects in the scene. This is used to get the index of the object in the list.

    #Define instance variables
    def __init__(self):
        self.verticies = []  #List of vertices in the object. geometery_utils.xp_vertex
        self.indicies = []  #List of indices in the object
        self.draw_calls = [] #List of "draw calls". These are pairs of start indicies and lengths
        self.alb_texture = ""
        self.nml_texture = ""
        self.lit_texture = ""
        self.do_blend_alpha = False
        self.alpha_cutoff = 0.5
        self.cast_shadows = True
        self.name = ""

    def read(self, in_obj_path):
        self.name = os.path.basename(in_obj_path)

        with open(in_obj_path, "r") as f:
            lines = f.readlines()
        
        for line in lines:

            line = line.strip()
            tokens = line.split()

            if len(tokens) == 0:
                continue

            if tokens[0] == "VT":
                #We flip Y and Z because of the way Blender and X-Plane handle coordinates
                vert = geometery_utils.xp_vertex(
                    float(tokens[1]), float(tokens[3]), float(tokens[2]), 
                    float(tokens[4]), float(tokens[6]), float(tokens[5]), 
                    float(tokens[7]), float(tokens[8])
                )
                self.verticies.append(vert)

            elif tokens[0] == "IDX10":
                #List of 10 indices
                for i in range(10):
                    self.indicies.append(int(tokens[i+1]))

            elif tokens[0] == "IDX":
                #Single index
                self.indicies.append(int(tokens[1]))
            
            elif tokens[0] == "TRIS":
                #Draw call. Start index and length
                start_index = int(tokens[1])
                length = int(tokens[2])
                self.draw_calls.append((start_index, length))

            elif tokens[0] == "TEXTURE":
                self.alb_texture = tokens[1]
            
            elif tokens[0] == "TEXTURE_NORMAL":
                self.nml_texture = tokens[1]

            elif tokens[0] == "TEXTURE_LIT":
                self.lit_texture = tokens[1]

            elif tokens[0] == "GLOBAL_no_blend":
                self.do_blend_alpha = False
                self.alpha_cutoff = float(tokens[1])

            elif tokens[0] == "GLOBAL_no_shadow":
                self.cast_shadows = False

    def to_scene(self):
        #Create a new collection for this object
        collection = bpy.data.collections.new(self.name)
        collection.name = self.name
        bpy.context.scene.collection.children.link(collection)

        #Create a new material
        mat = bpy.data.materials.new(name=self.name)
        mat.use_nodes = True
        xp_mat = mat.xp_materials
        xp_mat.alb_texture = self.alb_texture
        xp_mat.nml_texture = self.nml_texture
        xp_mat.lit_texture = self.lit_texture
        xp_mat.do_blend_alpha = self.do_blend_alpha
        xp_mat.alpha_cutoff = self.alpha_cutoff
        xp_mat.cast_shadows = self.cast_shadows
        mat.name = self.name

        for dc in self.draw_calls:
            start_index = dc[0]
            length = dc[1]

            #Get the indicies for this draw call
            dc_indicies = self.indicies[start_index:start_index+length]

            #Get the verticies for this draw call, and adjust the indicies references
            dc_verticies = []
            for i in range(len(dc_indicies)):
                dc_verticies.append(self.verticies[dc_indicies[i]])
                dc_indicies[i] = i

            #Create the object for this draw call
            dc_obj = geometery_utils.create_obj_from_draw_call(dc_verticies, dc_indicies, f"TRIS {start_index} {length}")
            dc_obj.data.materials.append(mat)
            collection.objects.link(dc_obj)
            bpy.context.view_layer.objects.active = dc_obj
