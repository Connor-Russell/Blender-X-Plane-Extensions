#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      4-24/2025
#Module:    xp_obj.py
#Purpose:   Provide a class that abstracts the X-Plane object, and provides functions to import the object into Blender

import bpy
import os
import mathutils

from ..Helpers import geometery_utils
from ..Helpers import anim_utils

class anim_loc_keyframe:
    """
    Class to represent a keyframe for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        self.type = 'loc_keyframe'
        self.frame = 0
        self.time = 0  #Time of the keyframe
        self.loc = (0, 0, 0)  #Location of the keyframe
        self.empty = None  #Empty for the animation

class anim_rot_keyframe:
    """
    Class to represent a keyframe for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        self.type = 'rot_keyframe'
        self.frame = 0
        self.time = 0  #Time of the keyframe
        self.rot_vector = (0, 0, 0)  #Rotation vector of the keyframe. Only used if standalone
        self.rot = 0  #Rotation of the keyframe
        self.empty = None  #Empty for the animation

class anim_rot_table:
    """
    Class to represent a table of keyframes for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        self.type = 'rot_table'
        self.dataref = ''  #Dataref for the animation
        self.keyframes = []  #List of keyframes for the animation
        self.rot_vector = (0, 0, 0)  #Rotation vector of the keyframe. Only used if standalone
        self.empty = None  #Empty for the animation

    def add_keyframe(self, time, rot):
        #Add a keyframe to the list of keyframes
        kf = anim_rot_keyframe()
        kf.time = time
        kf.rot = rot
        self.keyframes.append(kf)

    def get_frames(self):
        #Find the highest, and lowest times in all the frames
        min_time = 9999999999
        max_time = -9999999999
        min_frame = 0
        max_frame = 250

        for kf in self.keyframes:
            if kf.time < min_time:
                min_time = kf.time
            if kf.time > max_time:
                max_time = kf.time

        #Now iterate through all the keyframes, and interpolate their frame based on where they are in the time range
        for kf in self.keyframes:
            #Get the time range
            time_range = max_time - min_time
            if time_range == 0:
                time_range = 1

            #Get the frame range
            frame_range = max_frame - min_frame

            #Get the frame for this keyframe
            kf.frame = int((kf.time - min_time) / time_range * frame_range + min_frame)

class anim_loc_table:
    """
    Class to represent a table of keyframes for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        self.type = 'loc_table'
        self.dataref = ""  #Dataref for the animation
        self.keyframes = []  #List of keyframes for the animation
        self.empty = None  #Empty for the animation

    def add_keyframe(self, time, loc):
        #Add a keyframe to the list of keyframes
        kf = anim_loc_keyframe()
        kf.time = time
        kf.loc = loc
        self.keyframes.append(kf)

    def get_frames(self):
        #Find the highest, and lowest times in all the frames
        min_time = 9999999999
        max_time = -9999999999
        min_frame = 2
        max_frame = 250

        for kf in self.keyframes:
            if kf.time < min_time:
                min_time = kf.time
            if kf.time > max_time:
                max_time = kf.time

        #Now iterate through all the keyframes, and interpolate their frame based on where they are in the time range
        for kf in self.keyframes:
            #Get the time range
            time_range = max_time - min_time
            if time_range == 0:
                time_range = 1

            #Get the frame range
            frame_range = max_frame - min_frame

            #Get the frame for this keyframe
            kf.frame = int((kf.time - min_time) / time_range * frame_range + min_frame)

class anim_level:
    """
    Class to represent a level of animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        self.first_action = None #This is the empty that drives the first action in the animation
        self.last_action = None #This is the empty that drives the last action in the animation
        self.actions = []  #List of actions for the animation
        self.draw_calls = []  #List of draw calls for the animation
        self.children = []  #List of children anim_levels for the animation

    def add_to_scene(self, parent_obj, all_verts, all_indicies, in_mat, in_collection):
        #Create a new empty for this animation level

        self.last_action = parent_obj
        cur_parent = parent_obj
        for i, action in enumerate(self.actions):
            #Create the empty for this action
            name = f"Anim + Action {i}"
            if len(self.draw_calls) > 0:
                name = f"Anim TRIS {self.draw_calls[0][0]} {self.draw_calls[0][1]} Action {i}"
            anim_empty = bpy.data.objects.new(name, None)
            anim_empty.empty_display_type = "ARROWS"
            anim_empty.empty_display_size = 0.1
            in_collection.objects.link(anim_empty)
            self.actions[i].empty = anim_empty

            if cur_parent != None:
                anim_empty.parent = cur_parent
            cur_parent = anim_empty

            #Set the first/last actions
            if i == 0:
                self.first_action = anim_empty
            self.last_action = anim_empty

            #Reset our frame
            anim_utils.goto_frame(0)

        #Now we need to add all the draw calls to the scene, then parent them to the empty
        for dc in self.draw_calls:
            start_index = dc[0]
            length = dc[1]

            #Get the indicies for this draw call
            dc_indicies = all_indicies[start_index:start_index+length]

            #Get the verticies for this draw call, and adjust the indicies references
            dc_verticies = []
            for i in range(len(dc_indicies)):
                dc_verticies.append(all_verts[dc_indicies[i]])
                dc_indicies[i] = i

            #To fix flipped normals
            dc_indicies.reverse()

            #Create the object for this draw call
            dc_obj = geometery_utils.create_obj_from_draw_call(dc_verticies, dc_indicies, f"TRIS {start_index} {length}")
            dc_obj.data.materials.append(in_mat)
            in_collection.objects.link(dc_obj)

            dc_obj.parent = self.last_action

        #Now that we added out draw calls, it's time to recurse
        for child in self.children:
            child.add_to_scene(self.last_action, all_verts, all_indicies, in_mat, in_collection)

        #Reset our frame
        anim_utils.goto_frame(0)

        #Now that everything is parented, we add the keyframes in reverse order so everything is applied correctly
        for i, action in enumerate(reversed(self.actions)):

            anim_empty = action.empty
            
            #Now, we apply the animations!
            if action.type == 'loc_keyframe':
                base_pos = anim_utils.get_obj_position_world(anim_empty)
                new_pos = (base_pos[0] + action.loc[0], base_pos[1] + action.loc[1], base_pos[2] + action.loc[2])
                anim_utils.set_obj_position_world(anim_empty, new_pos)
            
            elif action.type == 'rot_keyframe':
                new_rot = anim_utils.axis_angle_to_euler_xyz(action.rot_vector, action.rot)
                anim_utils.set_obj_rotation_from_euler(anim_empty, new_rot)
            
            elif action.type == 'loc_table':
                base_pos = anim_utils.get_obj_position_world(anim_empty)

                dataref = action.dataref

                action.get_frames()

                #Create a new track for this dataref
                anim_utils.add_xp_dataref_track(anim_empty, dataref)

                #Now, we need to add all the keyframes to the track
                for kf in action.keyframes:
                    #Set the current frame to the keyframe time
                    anim_utils.goto_frame(kf.frame)

                    #Set the position of the empty to the keyframe value
                    new_pos = (base_pos[0] + kf.loc[0], base_pos[1] + kf.loc[1], base_pos[2] + kf.loc[2])
                    anim_utils.set_obj_position_world(anim_empty, new_pos)

                    #Set the value of the dataref to the keyframe value
                    anim_utils.keyframe_obj_location(anim_empty)
                    anim_utils.keyframe_xp_dataref(anim_empty, dataref, kf.time)
            
            elif action.type == 'rot_table':
                dataref = action.dataref

                action.get_frames()

                anim_utils.add_xp_dataref_track(anim_empty, dataref)

                #Now, we need to add all the keyframes to the track
                for kf in action.keyframes:
                    #Set the current frame to the keyframe time
                    anim_utils.goto_frame(kf.frame)

                    #Set the rotation of the empty to the keyframe value
                    new_rot = anim_utils.axis_angle_to_euler_xyz(action.rot_vector, kf.rot)
                    anim_utils.set_obj_rotation_from_euler(anim_empty, new_rot)

                    #Set the value of the dataref to the keyframe value
                    anim_utils.keyframe_obj_rotation(anim_empty)
                    anim_utils.keyframe_xp_dataref(anim_empty, dataref, kf.time)

            #Reset our frame
            anim_utils.goto_frame(0)

class object:
    """
    Class to represent an X-Plane object. This class provides functions to import the object into Blender.
    """

    #Define instance variables
    def __init__(self):
        self.verticies = []  #List of vertices in the object. geometery_utils.xp_vertex
        self.indicies = []  #List of indices in the object
        self.draw_calls = [] #List of "draw calls". These are pairs of start indicies and lengths
        self.anims = []  #List of animations in the object. This is a list of anim_levels
        self.alb_texture = ""
        self.nml_texture = ""
        self.lit_texture = ""
        self.do_blend_alpha = False
        self.alpha_cutoff = 0.5
        self.cast_shadows = True
        self.name = ""

    def read(self, in_obj_path):
        self.name = os.path.basename(in_obj_path)

        trans_matrix = [1, -1, 1]

        #Stack for the current animation tree. This is used to keep track of the current animation level
        cur_anim_tree = []
        cur_rotate_keyframe_do_x = False
        cur_rotate_keyframe_do_y = False
        cur_rotate_keyframe_do_z = False

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
                    float(tokens[1]) * trans_matrix[0], float(tokens[3]) * trans_matrix[1], float(tokens[2]) * trans_matrix[2], 
                    float(tokens[4]) * trans_matrix[0], float(tokens[6]) * trans_matrix[1], float(tokens[5]) * trans_matrix[2], 
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

                #Add the draw call to the list of draw calls. This is the current animation in the tree, or the list of static draw calls it there is no current animation
                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this draw call to the current animation tree
                    cur_anim_tree[-1].draw_calls.append((start_index, length))
                else:
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

            elif tokens[0] == "ANIM_begin": 
                new_anim = anim_level()

                #If we are in an animation tree, add this animation to the current animation tree. Otherwise, add it directly to the anim list
                if len(cur_anim_tree) > 0:
                    cur_anim_tree[-1].children.append(new_anim)
                else:
                    self.anims.append(new_anim)

                #Append it to the current animation tree
                cur_anim_tree.append(new_anim)
            
            elif tokens[0] == "ANIM_trans":
                #If this command is missing the dataref, we assume it is a static translation
                if len(tokens) < 10:
                    #ANIM_trans <x1> <y1> <z1> <x2> <y2> <z2> <v1> <v2>
                    cur_static_translation = anim_loc_keyframe()
                    cur_static_translation.time = 0
                    cur_static_translation.loc = (float(tokens[1]) * trans_matrix[0], float(tokens[3]) * trans_matrix[1], float(tokens[2] * trans_matrix[2]))
                    cur_anim_tree[-1].actions.append(cur_static_translation)

                #Otherwise, we assume this is a shortened keyframe table
                elif len(tokens) == 10:
                    #ANIM_trans <x1> <y1> <z1> <x2> <y2> <z2> <v1> <v2>
                    cur_table = anim_loc_table()
                    cur_table.dataref = tokens[9]

                    key1 = anim_loc_keyframe()
                    key1.time = float(tokens[7])
                    key1.loc = (float(tokens[1]) * trans_matrix[0], float(tokens[3]) * trans_matrix[1], float(tokens[2]) * trans_matrix[2])
                    cur_table.add_keyframe(key1.time, key1.loc)

                    key2 = anim_loc_keyframe()
                    key2.time = float(tokens[8])
                    key2.loc = (float(tokens[4]) * trans_matrix[0], float(tokens[6]) * trans_matrix[1], float(tokens[5]) * trans_matrix[2])
                    cur_table.add_keyframe(key2.time, key2.loc)

                    cur_anim_tree[-1].actions.append(cur_table)
            
            elif tokens[0] == "ANIM_rotate":
                #This is the same as the translation, but for rotation
                if len(tokens) < 9:
                    #ANIM_rotate <ratiox> <ratioy> <ratioz> <rotate1> <rotate2> <v1> <v2> <dataref>
                    cur_static_rotation = anim_rot_keyframe()
                    cur_static_rotation.time = 0

                    cur_rotate_keyframe_do_x = float(tokens[1]) * trans_matrix[0]
                    cur_rotate_keyframe_do_y = float(tokens[3]) * trans_matrix[1]
                    cur_rotate_keyframe_do_z = float(tokens[2]) * trans_matrix[2]
                    cur_static_rotation.rot_vector = mathutils.Vector((cur_rotate_keyframe_do_x, cur_rotate_keyframe_do_y, cur_rotate_keyframe_do_z))
                    cur_static_rotation.rot = float(tokens[4])

                    cur_anim_tree[-1].actions.append(cur_static_rotation)

                elif len(tokens) == 9:
                    #ANIM_rotate <ratiox> <ratioy> <ratioz> <rotate1> <rotate2> <v1> <v2> <dataref>
                    cur_table = anim_rot_table()
                    cur_table.dataref = tokens[8]

                    cur_rotate_keyframe_do_x = float(tokens[1]) * trans_matrix[0]
                    cur_rotate_keyframe_do_y = float(tokens[3]) * trans_matrix[1]
                    cur_rotate_keyframe_do_z = float(tokens[2]) * trans_matrix[2]

                    cur_table.rot_vector = mathutils.Vector((cur_rotate_keyframe_do_x, cur_rotate_keyframe_do_y, cur_rotate_keyframe_do_z))

                    key1 = anim_rot_keyframe()
                    key1.time = float(tokens[6])
                    key1.rot = float(tokens[4]) * -1
                    
                    cur_table.add_keyframe(key1.time, key1.rot)

                    key2 = anim_rot_keyframe()
                    key2.time = float(tokens[7])
                    key2.rot = float(tokens[5])
                    cur_table.add_keyframe(key2.time, key2.rot)

                    cur_anim_tree[-1].actions.append(cur_table)
            
            elif tokens[0] == "ANIM_end":
                #Pop the current animation tree
                cur_anim_tree.pop()
            
            elif tokens[0] == "ANIM_rotate_begin":
                cur_table = anim_rot_table()
                cur_table.dataref = tokens[4]
                cur_rotate_keyframe_do_x = float(tokens[1]) * trans_matrix[0]
                cur_rotate_keyframe_do_y = float(tokens[3]) * trans_matrix[1]
                cur_rotate_keyframe_do_z = float(tokens[2]) * trans_matrix[2]

                cur_table.rot_vector = mathutils.Vector((cur_rotate_keyframe_do_x, cur_rotate_keyframe_do_y, cur_rotate_keyframe_do_z))
                
                cur_anim_tree[-1].actions.append(cur_table)
            
            elif tokens[0] == "ANIM_rotate_key":
                #ANIM_rotate_key <time> <angle>
                cur_keyframe = anim_rot_keyframe()
                cur_keyframe.time = float(tokens[1])
                cur_keyframe.rot = float(tokens[2])

                cur_anim_tree[-1].actions[-1].keyframes.append(cur_keyframe)

            elif tokens[0] == "ANIM_trans_begin":
                cur_table = anim_loc_table()
                cur_table.dataref = tokens[1]
                cur_anim_tree[-1].actions.append(cur_table)

            elif tokens[0] == "ANIM_trans_key":
                #ANIM_trans_key <value> <x> <y> <z>
                cur_keyframe = anim_loc_keyframe()
                cur_keyframe.time = float(tokens[1])
                cur_keyframe.loc = (0, 0, 0)
                new_pos = (float(tokens[2]) * trans_matrix[0], float(tokens[4]) * trans_matrix[1], float(tokens[3]) * trans_matrix[2])
                cur_keyframe.loc = new_pos

                cur_anim_tree[-1].actions[-1].keyframes.append(cur_keyframe)

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
        xp_mat.normal_texture = self.nml_texture
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

            #To fix flipped normals
            dc_indicies.reverse()

            #Create the object for this draw call
            dc_obj = geometery_utils.create_obj_from_draw_call(dc_verticies, dc_indicies, f"TRIS {start_index} {length}")
            dc_obj.data.materials.append(mat)
            collection.objects.link(dc_obj)
            bpy.context.view_layer.objects.active = dc_obj

        #Now that we have the basic geometery, we need to add the animated stuff.
        #This is very simple. We iterate through all our root animation levels, and add them to the scene. Aka we call the function to do the hard (sort of) stuff
        for anim in self.anims:
            anim.add_to_scene(None, self.verticies, self.indicies, mat, collection)
        
        #WE'RE DONE!