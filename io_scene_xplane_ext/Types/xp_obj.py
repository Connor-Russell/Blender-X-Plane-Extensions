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

class draw_call:
    """
    Class to represent a draw call. This class is used to store the draw calls for an object.
    """

    #Define instance variables
    def __init__(self):
        self.start_index = 0  #Start index of the draw call
        self.length = 0  #Length of the draw call
        self.lod_start = 0  #Start range of the LOD
        self.lod_end = 0  #End range of the LOD
        self.lod_bucket = -1  #LOD bucket of the draw call. Corresponds to the XP2B value.

    def add_to_scene(self, all_verts, all_indicies, in_mats, in_collection):
        """
        Adds the geometry represented by this draw call to the Blender scene as a new mesh object.

        Args:
            all_verts (list): List of all vertex objects (xp_vertex) for the parent X-Plane object.
            all_indicies (list): List of all indices for the parent X-Plane object.
            in_mats (list): List of Blender material(s) to assign to the created mesh. The first material is used.
            in_collection (bpy.types.Collection): The Blender collection to which the new mesh object will be linked.

        Returns:
            bpy.types.Object: The newly created Blender mesh object representing this draw call.

        Notes:
            - Extracts the relevant indices and vertices for this draw call from the full object arrays.
            - Reindexes and reverses indices to match Blender's winding order (fixes normal direction).
            - Creates a mesh object using geometery_utils.create_obj_from_draw_call.
            - Assigns LOD bucket and material if applicable.
            - Links the object to the provided collection.
        """
        # When adding geometry, we need verts and indicies. We have our range of indicies, and *all* the indicies and *all* the verts
        # So to add them, we need *just* our indicies and verts. So what we do is we get all the indicies we need, in the correct order
        # Then we iterate through them, getting the verticies they reference, and offsetting the indicies to start idx is at 0 here.
        # Then when we pass it to creat_obj_from_draw_call it's in the correct format.
        # Note, we do need to flip the indicies to fix reversed normals. I believe this an XP vs Blender winding thing, (TODO: Double check this) but it works for now
        dc_indicies = all_indicies[self.start_index:self.start_index+self.length]

        dc_verticies = []
        for i in range(len(dc_indicies)):
            dc_verticies.append(all_verts[dc_indicies[i]])
            dc_indicies[i] = i

        dc_indicies.reverse()

        dc_obj = geometery_utils.create_obj_from_draw_call(dc_verticies, dc_indicies, f"TRIS {self.start_index} {self.length}")
        in_collection.objects.link(dc_obj)

        if self.lod_bucket != -1:
            #Set the LOD bucket for this object
            dc_obj.xplane.override_lods = True
            if self.lod_bucket == 0:
                dc_obj.xplane.lod[0] = True
            elif self.lod_bucket == 1:
                dc_obj.xplane.lod[1] = True
            elif self.lod_bucket == 2:
                dc_obj.xplane.lod[2] = True
            elif self.lod_bucket == 3:
                dc_obj.xplane.lod[3] = True
            else:
                print(f"Unknown LOD bucket for obj {dc_obj.name} for range {self.lod_start}-{self.lod_end}. Bucket is {self.lod_bucket}. What?")

        # Set the material for this object. Right now this is very basic - we use the first material in the list. In the future, this list will contain all material variants which are based on the draw call state
        # We would have all these variants so if the material is in a state that is the same as us (i.e. the blend mode) we can reuse an existing material vs a new one
        if len(in_mats) > 0:
            dc_obj.data.materials.append(in_mats[0])

        return dc_obj

class anim_action:
    """
    Base class for all animation actions
    """

    def __init__(self):
        self.type = ''
        self.empty = None  #Empty for the animation

class anim_show_hide_command:
    """
    Class to represent a single show/hide command in an animation
    """

    def __init__(self):
        self.hide = False  #True if this command is a hide command. Otherwise, it's a show command
        self.start_value = 0  #Min dref value to show/hide at
        self.end_value = 0  #Max dref value to show/hide at
        self.dataref = ""  #Dataref for the animation

class anim_show_hide_series(anim_action):
    """
    Class to represent a series of show/hide commands for an animation. This class is used to store the show/hide commands for an animation.
    """

    #Define instance variables
    def __init__(self):
        super().__init__()
        self.type = 'show_hide_series'
        self.commands = []  #List of show/hide commands for the animation
        self.empty = None  #Empty for the animation

    def add_command(self, cmd):
        """
        Add a command to the list of commands

        Args:
            cmd (anim_show_hide_command): Command to add to the list of commands
        """
        self.commands.append(cmd)

class anim_loc_keyframe(anim_action):
    """
    Class to represent a keyframe for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        super().__init__()
        self.type = 'loc_keyframe'
        self.frame = 0
        self.time = 0  #Time of the keyframe
        self.loc = (0, 0, 0)  #Location of the keyframe
        self.empty = None  #Empty for the animation

class anim_rot_keyframe(anim_action):
    """
    Class to represent a keyframe for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        super().__init__()
        self.type = 'rot_keyframe'
        self.frame = 0
        self.time = 0  #Time of the keyframe
        self.rot_vector = (0, 0, 0)  #Rotation vector of the keyframe. Only used if standalone
        self.rot = 0  #Rotation of the keyframe
        self.empty = None  #Empty for the animation

class anim_rot_table_vector_transform(anim_action):
    """
    Class to represent the vector transform that must come before an anim_rot_table. This will act as a parent for the keyframed table, allowing for smooth animations along an arbitrary axis
    """

    def __init__(self):
        super().__init__()
        self.type = 'rot_table_vector_transform'
        self.rot_vector = (0, 0, 0)  #Rotation vector of the table

class anim_rot_table(anim_action):
    """
    Class to represent a table of keyframes for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        super().__init__()
        self.type = 'rot_table'
        self.dataref = ''  #Dataref for the animation
        self.keyframes = []  #List of keyframes for the animation
        self.empty = None  #Empty for the animation
        self.loop = 0 #The *loop animation every this dref value* value.

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

class anim_loc_table(anim_action):
    """
    Class to represent a table of keyframes for an animation. This class is used to store the keyframes for an animation.
    """

    #Define instance variables
    def __init__(self):
        super().__init__()
        self.type = 'loc_table'
        self.dataref = ""  #Dataref for the animation
        self.keyframes = []  #List of keyframes for the animation
        self.empty = None  #Empty for the animation
        self.loop = 0 #The *loop animation every this dref value* value.

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
            name = f"Anim"
            if len(self.draw_calls) > 0:
                name += f" TRIS {self.draw_calls[0].start_index} {self.draw_calls[0].length}"
            name += f" Pt {i}"
            if action.type == 'rot_table_vector_transform':
                name += " Rotation Transform"
            elif action.type == 'rot_keyframe':
                name += " Static Rotation"
            elif action.type == 'loc_keyframe':
                name += " Static Translation"
            elif action.type == 'loc_table':
                name += " Keyframed Translation"
            elif action.type == 'rot_table':
                name += " Keyframed Rotation"
            elif action.type == 'show_hide_series':
                name += " Show/Hide Series"
            anim_empty = bpy.data.objects.new(name, None)
            anim_empty.empty_display_type = "ARROWS"
            anim_empty.empty_display_size = 0.1
            in_collection.objects.link(anim_empty)
            self.actions[i].empty = anim_empty

            if cur_parent != None:
                anim_empty.parent = cur_parent
            cur_parent = anim_empty

            #If it is a rotation we need to align it to the rotation vector
            if action.type == 'rot_keyframe' or action.type == 'rot_table_vector_transform':
                eular = anim_utils.euler_to_align_z_with_vector(action.rot_vector)  #We align rotations to their rotation vector so they can be rotated into static place, or their child keyframe controller can be rotated along it's local Z (which is this vector)
                anim_utils.set_obj_rotation_world(anim_empty, eular)
            elif action.type == "rot_table":
                #Rotation tables are always aligned with their parent. Their parent is transformed so it points in the vector of the rotation vector.
                #By having no rotation, our Z rotates along the rotation vector
                anim_empty.rotation_euler = mathutils.Vector((0, 0, 0)).xyz
            elif action.type == 'loc_keyframe' or action.type == 'loc_table' or action.type == "show_hide_series":
                #Most actions should have no rotation in world space
                eular = mathutils.Vector((0, 0, 0))
                anim_utils.set_obj_rotation_world(anim_empty, eular)
            else:
                #TODO: Warn here once we have a proper logging system
                pass

            #Set the first/last actions
            if i == 0:
                self.first_action = anim_empty
            self.last_action = anim_empty

            #Reset our frame
            anim_utils.goto_frame(0)

        #Now we need to add all the draw calls to the scene, then parent them to the empty
        for dc in self.draw_calls:
            dc_obj = dc.add_to_scene(all_verts, all_indicies, [in_mat], in_collection)
            dc_obj.parent = self.last_action

            #So it doesn't take up it's parent's rotation
            eular = mathutils.Vector((0, 0, 0))
            anim_utils.set_obj_rotation_world(dc_obj, eular)

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
                base_rot = anim_utils.get_base_rot_for_local_z_rotation(anim_empty)
                anim_utils.rotate_obj_around_local_z(anim_empty, action.rot, base_rot)
            
            elif action.type == 'loc_table':
                
                base_pos = anim_utils.get_obj_position_world(anim_empty)

                dataref = action.dataref

                action.get_frames()

                anim_utils.add_xp_dataref_track(anim_empty, dataref)
                anim_empty.xplane.datarefs[-1].loop = action.loop

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
                anim_empty.xplane.datarefs[-1].loop = action.loop

                base_rot = anim_utils.get_obj_rotation(anim_empty)

                #Now, we need to add all the keyframes to the track
                for kf in action.keyframes:
                    #Set the current frame to the keyframe time
                    anim_utils.goto_frame(kf.frame)

                    #Set the rotation of the empty to the keyframe value
                    new_rot = (base_rot[0], base_rot[1], base_rot[2] + kf.rot)
                    anim_utils.set_obj_rotation(anim_empty, new_rot)

                    #Set the value of the dataref to the keyframe value
                    anim_utils.keyframe_obj_rotation(anim_empty)
                    anim_utils.keyframe_xp_dataref(anim_empty, dataref, kf.time)

            elif action.type == 'show_hide_series':
                for cmd in action.commands:
                    anim_empty.xplane.datarefs.add()
                    anim_empty.xplane.datarefs[-1].path = cmd.dataref
                    if cmd.hide:
                        anim_empty.xplane.datarefs[-1].anim_type = 'hide'
                    else:
                        anim_empty.xplane.datarefs[-1].anim_type = 'show'
                    anim_empty.xplane.datarefs[-1].show_hide_v1 = cmd.start_value
                    anim_empty.xplane.datarefs[-1].show_hide_v2 = cmd.end_value

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
        self.do_blend_alpha = True
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
        cur_start_lod = 0
        cur_end_lod = 0

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
                dc = draw_call()
                dc.start_index = int(tokens[1])
                dc.length = int(tokens[2])
                dc.lod_start = cur_start_lod
                dc.lod_end = cur_end_lod

                #Add the draw call to the list of draw calls. This is the current animation in the tree, or the list of static draw calls it there is no current animation
                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this draw call to the current animation tree
                    cur_anim_tree[-1].draw_calls.append(dc)
                else:
                    self.draw_calls.append(dc)

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
                    
                    cur_rotate_transform = anim_rot_table_vector_transform()

                    cur_rotate_keyframe_do_x = float(tokens[1]) * trans_matrix[0]
                    cur_rotate_keyframe_do_y = float(tokens[3]) * trans_matrix[1]
                    cur_rotate_keyframe_do_z = float(tokens[2]) * trans_matrix[2]

                    cur_rotate_transform.rot_vector = mathutils.Vector((cur_rotate_keyframe_do_x, cur_rotate_keyframe_do_y, cur_rotate_keyframe_do_z))

                    cur_table = anim_rot_table()
                    cur_table.dataref = tokens[8]

                    key1 = anim_rot_keyframe()
                    key1.time = float(tokens[6])
                    key1.rot = float(tokens[4])
                    
                    cur_table.add_keyframe(key1.time, key1.rot)

                    key2 = anim_rot_keyframe()
                    key2.time = float(tokens[7])
                    key2.rot = float(tokens[5])
                    cur_table.add_keyframe(key2.time, key2.rot)

                    cur_anim_tree[-1].actions.append(cur_rotate_transform)
                    cur_anim_tree[-1].actions.append(cur_table)
            
            elif tokens[0] == "ANIM_keyframe_loop":
                #ANIM_keyframe_loop <value>
                #If there is a anim tree, and it has an actions, and the last item in actions is a loc_table/rot_table, we it's loop value
                if len(cur_anim_tree) > 0 and cur_anim_tree[-1].actions != None:
                    if cur_anim_tree[-1].actions[-1].type == 'loc_table' or cur_anim_tree[-1].actions[-1].type == 'rot_table':
                        cur_anim_tree[-1].actions[-1].loop = float(tokens[1])

            elif tokens[0] == "ANIM_show":
                #ANIM_show <v1> <v2> <dataref>

                #Make sure we have a current animation tree
                if len(cur_anim_tree) == 0:
                    continue

                cur_show = anim_show_hide_command()
                cur_show.hide = False
                cur_show.start_value = float(tokens[1])
                cur_show.end_value = float(tokens[2])
                cur_show.dataref = tokens[3]
                
                #Check if we have a current show/hide series
                cur_show_hide_series = None
                if len(cur_anim_tree[-1].actions) > 0:
                    if cur_anim_tree[-1].actions[-1].type == 'show_hide_series':
                        cur_show_hide_series = cur_anim_tree[-1].actions[-1]

                #If we don't have a current show/hide series, create one
                if cur_show_hide_series == None:
                    cur_show_hide_series = anim_show_hide_series()
                    cur_anim_tree[-1].actions.append(cur_show_hide_series)

                cur_show_hide_series.add_command(cur_show)

            elif tokens[0] == "ANIM_hide":
                #ANIM_hide <v1> <v2> <dataref>

                #Make sure we have a current animation tree
                if len(cur_anim_tree) == 0:
                    continue

                cur_show = anim_show_hide_command()
                cur_show.hide = True
                cur_show.start_value = float(tokens[1])
                cur_show.end_value = float(tokens[2])
                cur_show.dataref = tokens[3]
                
                #Check if we have a current show/hide series
                cur_show_hide_series = None
                if len(cur_anim_tree[-1].actions) > 0:
                    if cur_anim_tree[-1].actions[-1].type == 'show_hide_series':
                        cur_show_hide_series = cur_anim_tree[-1].actions[-1]

                #If we don't have a current show/hide series, create one
                if cur_show_hide_series == None:
                    cur_show_hide_series = anim_show_hide_series()
                    cur_anim_tree[-1].actions.append(cur_show_hide_series)

                cur_show_hide_series.add_command(cur_show)

            elif tokens[0] == "ANIM_end":
                #Pop the current animation tree
                cur_anim_tree.pop()
            
            elif tokens[0] == "ANIM_rotate_begin":
                cur_rotate_transform = anim_rot_table_vector_transform()

                cur_rotate_keyframe_do_x = float(tokens[1]) * trans_matrix[0]
                cur_rotate_keyframe_do_y = float(tokens[3]) * trans_matrix[1]
                cur_rotate_keyframe_do_z = float(tokens[2]) * trans_matrix[2]

                cur_rotate_transform.rot_vector = mathutils.Vector((cur_rotate_keyframe_do_x, cur_rotate_keyframe_do_y, cur_rotate_keyframe_do_z))

                cur_table = anim_rot_table()
                cur_table.dataref = tokens[4]
                
                cur_anim_tree[-1].actions.append(cur_rotate_transform)
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

            elif tokens[0] == "ATTR_LOD":
                #ANIM_lod <start> <end>
                cur_start_lod = float(tokens[1])
                cur_end_lod = float(tokens[2])

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

        #In X-Plane2Blender, the LOD system is done via buckets. There are 4 buckets, with their start/end distances set at a collection level
        #In X-Plane however, the LOD sysytem is done via ranges on a potentially per-tris basis, so we could potentially
        #have more LODs than buckets! We... can't fix this. So what we'll do is just get a dictionary of all the LODs, then assign draw calls to the appropriate bucket
        #In X-Plane, there are two LOD methods, additive and selective.
        #In Additive mode, all LODs that are in range are drawn
        #In Selective mode, a single LOD is drawn, based on the distance being within the min and max.
        #We determine additive by checking if any LODs *don't* start with 0, in which case we assume it's selective
        #This is relevant because if the LOD is additive, the objects that don't fit in a bucket will be put in every bucket that their range is *less* than
        #If the LOD is selective, they'll be put in the bucket that their average range is cloest to. 
        all_lod_buckets = []
        is_selective_lod = False

        #Define the LOD buckets
        for dc in self.draw_calls:
            lod_range = (int(dc.lod_start), int(dc.lod_end))

            if len(all_lod_buckets) < 4:
                did_find_matching_bucket = False
                for bucket in all_lod_buckets:
                    if bucket == lod_range:
                        did_find_matching_bucket = True
                        break
                
                if not did_find_matching_bucket:
                    all_lod_buckets.append(lod_range)
            else:
                print(f"Too many LOD buckets for object {self.name}. Skipping LOD {lod_range} for draw call {dc.start_index}-{dc.length}. Object will be added to best guess bucket. Double check this choice!")

        #Determine additive vs selective
        for bucket in all_lod_buckets:
            if bucket[0] != 0:
                is_selective_lod = True
                break

        all_lod_buckets.sort()

        def put_draw_call_in_bucket(dc, all_lod_buckets, is_selective_lod):
            matching_bucket_idx = -1
            for bucket in all_lod_buckets:
                if bucket == (int(dc.lod_start), int(dc.lod_end)):
                    matching_bucket_idx = all_lod_buckets.index(bucket)
                    break
            if matching_bucket_idx != -1:
                dc.lod_bucket = matching_bucket_idx

            else:
                if is_selective_lod:
                    closest_bucket = -1
                    closest_distance = 9999999999

                    for i, bucket in enumerate(all_lod_buckets):
                        avg_bucket_range = (bucket[0] + bucket[1]) / 2

                        distance = abs(avg_bucket_range - ((dc.lod_start + dc.lod_end) / 2))

                        if distance < closest_distance:
                            closest_distance = distance
                            closest_bucket = i
                        
                    if closest_bucket != -1:
                        dc.lod_bucket = closest_bucket
                else:
                    best_lod_match = -1

                    for i, bucket in enumerate(all_lod_buckets):
                        if bucket[1] >= dc.lod_end:
                            best_lod_match = i
                            break

                    if best_lod_match == -1:
                        best_lod_match = len(all_lod_buckets) - 1
                    
                    if best_lod_match != -1:
                        dc.lod_bucket = best_lod_match

        #Now assign draw calls to buckets
        for dc in self.draw_calls:
            put_draw_call_in_bucket(dc, all_lod_buckets, is_selective_lod)

        def recurse_anim_levels_to_assign_lod_buckets(level):
            for child in level.children:
                recurse_anim_levels_to_assign_lod_buckets(child)

            #Now assign lod buckets
            for dc in level.draw_calls:
                put_draw_call_in_bucket(dc, all_lod_buckets, is_selective_lod)

        for anim in self.anims:
            recurse_anim_levels_to_assign_lod_buckets(anim)

        #Lastly for LODs, we'll assign them to the collection
        if len(all_lod_buckets) > 0:
            collection.xplane.layer.lods = str(len(all_lod_buckets))
        for i, bucket in enumerate(all_lod_buckets):
            collection.xplane.layer.lod[i].near = bucket[0]
            collection.xplane.layer.lod[i].far = bucket[1]

        #For the basic draw calls just add 'em to the scene
        for dc in self.draw_calls:
            dc.add_to_scene(self.verticies, self.indicies, [mat], collection)


        #Now that we have the basic geometery, we need to add the animated stuff.
        #This is very simple. We iterate through all our root animation levels, and add them to the scene. Aka we call the function to do the hard (sort of) stuff
        for anim in self.anims:
            anim.add_to_scene(None, self.verticies, self.indicies, mat, collection)
        
        #WE'RE DONE!