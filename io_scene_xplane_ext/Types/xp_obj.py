#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      4-24/2025
#Module:    xp_obj.py
#Purpose:   Provide a class that abstracts the X-Plane object, and provides functions to import the object into Blender

import bpy
import os
import mathutils
import math

from ..Helpers import misc_utils
from ..Helpers import anim_utils
from ..Helpers import geometery_utils
from ..Helpers import anim_utils
from ..Helpers import light_data    #These are defines for the parameter layout of PARAM lights
from .. import props

from functools import total_ordering

@total_ordering
class light:
    """
    Class to represent a light in an X-Plane object. This class is used to store the lights for an object.
    """

    #Define instance variables
    def __init__(self):
        self.name = "" #Name of the light. Really a type.
        self.type = "POINT" #Type. POINT or SPOT
        self.xp_type = "NONE" #The X-Plane light type. This is a string that corresponds to the X-Plane light type.
        self.color_r = 1
        self.color_g = 1
        self.color_b = 1
        self.loc_x = 0
        self.loc_y = 0
        self.loc_z = 0
        self.dir_x = 0
        self.dir_y = 0
        self.dir_z = 0
        self.cone_angle = 0
        self.dataref = "" #Dataref for the light
        self.size = 0   #Light size measurement
        self.is_photometric = False #True if this light is photometric
        self.params = "" #String of additional params for the light, from LIGHT_PARAM
        self.xp_type = '' #The X-Plane light type.
        self.bb_s1 = 0 #Left UV coordinate of the custom billboard light texture
        self.bb_s2 = 0 #Right UV coordinate of the custom billboard light texture
        self.bb_t1 = 0 #Top UV coordinate of the custom billboard light texture
        self.bb_t2 = 0 #Bottom UV coordinate of the custom billboard light texture
        self.lod_start = 0  #Start range of the LOD. We don't actually use LODs because lights aren't LODed, but, this is used to dedupe
        self.lod_end = 0    #End range of the LOD

    def add_to_scene(self, in_collection):
        """
        Adds a new light to the Blender scene with the specified properties.
        """

        # Create a new Blender light datablock
        if self.cone_angle != 0:
            self.type = "SPOT"

        light_data = bpy.data.lights.new(name="Light", type=self.type)
        b_light = bpy.data.objects.new(name="Light", object_data=light_data)
        in_collection.objects.link(b_light)

        b_light.data.color = (self.color_r, self.color_g, self.color_b)
        b_light.data.energy = self.size / 50 if self.is_photometric else self.size * 2  # All just kinda guesses here, these seem sort of correct. It's just visual anyway...
        if self.type == "SPOT":
            b_light.data.spot_size = math.radians(self.cone_angle)

        b_light.location = (self.loc_x, self.loc_y, self.loc_z)
        b_light.rotation_mode = 'XYZ'

        light_euler = anim_utils.euler_to_align_z_with_vector((-self.dir_x, -self.dir_y, -self.dir_z))
        b_light.rotation_euler = light_euler

        b_light.data.xplane.param_size = self.size
        b_light.data.xplane.uv[0] = self.bb_s1   # left
        b_light.data.xplane.uv[1] = self.bb_t1   # top
        b_light.data.xplane.uv[2] = self.bb_s2   # right
        b_light.data.xplane.uv[3] = self.bb_t2   # bottom
        b_light.data.xplane.dataref = self.dataref
        b_light.data.xplane.name = self.name

        return b_light
    
    def __eq__(self, value):
        """
        Slightly unconventional. Checks if all params BUT LOD are equal. This is because if there are multiple lights in the SAME LOD they are intentional.
        But, if they are in DIFFERENT LODs, then they are a duplicate of the SAME light because of how LODs work in XP .objs.
        """
        if not isinstance(value, light):
            return NotImplemented

        return (self.name == value.name and
                self.type == value.type and
                self.xp_type == value.xp_type and
                self.color_r == value.color_r and
                self.color_g == value.color_g and
                self.color_b == value.color_b and
                self.loc_x == value.loc_x and
                self.loc_y == value.loc_y and
                self.loc_z == value.loc_z and
                self.dir_x == value.dir_x and
                self.dir_y == value.dir_y and
                self.dir_z == value.dir_z and
                self.cone_angle == value.cone_angle and
                self.dataref == value.dataref and
                self.size == value.size and
                self.is_photometric == value.is_photometric and
                self.params == value.params and
                self.xp_type == value.xp_type and
                self.bb_s1 == value.bb_s1 and
                self.bb_s2 == value.bb_s2 and
                self.bb_t1 == value.bb_t1 and
                self.bb_t2 == value.bb_t2 and
                (self.lod_start != value.lod_start or
                self.lod_end != value.lod_end))

    def __lt__(self, other):
        """
        Less than operator for light objects. This is used to sort lights by their LOD range.
        """
        return (self.name, self.type, self.xp_type, self.color_r, self.color_g,self.color_b,self.loc_x,self.loc_y,self.loc_z,self.dir_x,self.dir_y,self.dir_z,self.cone_angle,self.dataref,self.size, self.is_photometric, self.params, self.xp_type, self.bb_s1, self.bb_s2, self.bb_t1, self.bb_t2) < \
        (other.name, other.type, other.xp_type, other.color_r, other.color_g, other.color_b, other.loc_x, other.loc_y, other.loc_z, other.dir_x, other.dir_y, other.dir_z, other.cone_angle, other.dataref, other.size, other.is_photometric, other.params, other.xp_type, other.bb_s1, other.bb_s2, other.bb_t1, other.bb_t2)

class manipulator_detent:
    """
    Class to represent a detent in a manipulator. This class is used to store the detents for a manipulator.
    """

    def __init__(self):
        self.start = 0
        self.end = 0
        self.length = 0

    def copy(self):
        """
        Returns a copy of this detent object.
        """
        new_detent = manipulator_detent()
        new_detent.start = self.start
        new_detent.end = self.end
        new_detent.length = self.length

        return new_detent

class manipulator:
    """
    Class to represent a manipulator in an X-Plane object. This class is used to store the manipulators for an object.
    """

    #Define instance variables
    def __init__(self):
        self.valid = False  #True if this manipulator is valid. If not, it will be ignored
        #List of parameters for the manipulator. This is a list of strings. It's easier to store here then to have 500 different param types. We'll just grab directly from these string values when configuring
        self.params = []
        self.detents = []  #List of detents for the manipulator. This is a list of manipulator_detent objects
        self.wheel_delta = 0  #Wheel delta for the manipulator. This is used to set how much the scroll wheel changes the value
    
    def apply_to_obj(self, obj):
        """
        Applies the manipulator settings to the given Blender object
        """
        param_len = len(self.params)

        if param_len == 0:
            #If there are no params, we can't apply this manipulator
            return

        cmd = self.params[0]

        #Almost all manips have this, and if they don't they just ignore it anyway so we can just set it once
        obj.xplane.manip.wheel_delta = self.wheel_delta

        if param_len == 1 and cmd == "ATTR_manip_noop":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "noop"

        elif param_len >= 10 and cmd == "ATTR_manip_drag_xy":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "drag_xy"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.dx = float(self.params[2])
            obj.xplane.manip.dy = float(self.params[3])
            obj.xplane.manip.v1_min = float(self.params[4])
            obj.xplane.manip.v1_max = float(self.params[5])
            obj.xplane.manip.v2_min = float(self.params[6])
            obj.xplane.manip.v2_max = float(self.params[7])
            obj.xplane.manip.dataref1 = self.params[8]
            obj.xplane.manip.dataref2 = self.params[9]

            #Tooltip may or may not be included
            if param_len >= 11:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[10:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 8 and cmd == "ATTR_manip_drag_axis":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "drag_axis"
            if len(self.detents) > 0:
                obj.xplane.manip.type = "drag_axis_detent"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.dx = float(self.params[2])
            obj.xplane.manip.dy = float(self.params[3])
            obj.xplane.manip.dz = float(self.params[4])
            obj.xplane.manip.v1 = float(self.params[5])
            obj.xplane.manip.v2 = float(self.params[6])
            obj.xplane.manip.dataref1 = self.params[7]

            #Tooltip may or may not be included
            if param_len >= 9:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[8:])
                obj.xplane.manip.tooltip = tooltip

            #TODO: Implement detents. This should be easy but X-Plane2Blender isn't exposing the arguments so I need to dive into it's code1

        elif param_len >= 3 and cmd == "ATTR_manip_command":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.command = self.params[2]

            #Tooltip may or may not be included
            if param_len >= 4:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[3:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 7 and cmd == "ATTR_manip_command_axis":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_axis"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.dx = float(self.params[2])
            obj.xplane.manip.dy = float(self.params[3])
            obj.xplane.manip.dz = float(self.params[4])
            obj.xplane.manip.positive_command = self.params[5]
            obj.xplane.manip.negative_command = self.params[6]

            #Tooltip may or may not be included
            if param_len >= 8:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[7:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 5 and cmd == "ATTR_manip_push":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "push"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.v_down = float(self.params[2])
            obj.xplane.manip.v_up = float(self.params[3])
            obj.xplane.manip.dataref1 = self.params[4]

            #Tooltip may or may not be included
            if param_len >= 6:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[5:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 4 and cmd == "ATTR_manip_radio":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "radio"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.v_down = float(self.params[2])
            obj.xplane.manip.dataref1 = self.params[3]

            #Tooltip may or may not be included
            if param_len >= 5:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[4:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 5 and cmd == "ATTR_manip_toggle":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "toggle"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.v_on = float(self.params[2])
            obj.xplane.manip.v_off = float(self.params[3])
            obj.xplane.manip.dataref1 = self.params[4]

            #Tooltip may or may not be included
            if param_len >= 6:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[5:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 7 and cmd == "ATTR_manip_delta":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "delta"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.v_down = float(self.params[2])
            obj.xplane.manip.v_hold = float(self.params[3])
            obj.xplane.manip.v1_min = float(self.params[4])
            obj.xplane.manip.v1_max = float(self.params[5])
            obj.xplane.manip.dataref1 = self.params[6]

            #Tooltip may or may not be included
            if param_len >= 8:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[7:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 7 and cmd == "ATTR_manip_wrap":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "wrap"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.v_down = float(self.params[2])
            obj.xplane.manip.v_hold = float(self.params[3])
            obj.xplane.manip.v1_min = float(self.params[4])
            obj.xplane.manip.v1_max = float(self.params[5])
            obj.xplane.manip.dataref1 = self.params[6]

            #Tooltip may or may not be included
            if param_len >= 8:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[7:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 8 and cmd == "ATTR_manip_drag_axis_pix":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "drag_axis_pix"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.dx = float(self.params[2])
            obj.xplane.manip.step = float(self.params[3])
            obj.xplane.manip.exp = float(self.params[4])
            obj.xplane.manip.v1 = float(self.params[5])
            obj.xplane.manip.v2 = float(self.params[6])
            obj.xplane.manip.dataref1 = self.params[7]

            #Tooltip may or may not be included
            if param_len >= 9:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[8:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 4 and cmd == "ATTR_manip_command_knob":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_knob"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.positive_command = self.params[2]
            obj.xplane.manip.negative_command = self.params[3]

            #Tooltip may or may not be included
            if param_len >= 5:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[4:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 4 and cmd == "ATTR_manip_command_switch_up_down":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_switch_up_down"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.positive_command = self.params[2]
            obj.xplane.manip.negative_command = self.params[3]

            #Tooltip may or may not be included
            if param_len >= 5:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[4:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 4 and cmd == "ATTR_manip_command_switch_left_right":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_switch_left_right"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.positive_command = self.params[2]
            obj.xplane.manip.negative_command = self.params[3]

            #Tooltip may or may not be included
            if param_len >= 5:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[4:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 7 and cmd == "ATTR_manip_axis_knob":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "axis_knob"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.v1 = float(self.params[2])
            obj.xplane.manip.v2 = float(self.params[3])
            obj.xplane.manip.click_step = float(self.params[4])
            obj.xplane.manip.hold_step = float(self.params[5])
            obj.xplane.manip.dataref1 = self.params[6]

            #Tooltip may or may not be included
            if param_len >= 8:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[7:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 7 and cmd == "ATTR_manip_axis_switch_up_down":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "axis_switch_up_down"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.v1 = float(self.params[2])
            obj.xplane.manip.v2 = float(self.params[3])
            obj.xplane.manip.click_step = float(self.params[4])
            obj.xplane.manip.hold_step = float(self.params[5])
            obj.xplane.manip.dataref1 = self.params[6]

            #Tooltip may or may not be included
            if param_len >= 8:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[7:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 7 and cmd == "ATTR_manip_axis_switch_left_right":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "axis_switch_left_right"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.v1 = float(self.params[2])
            obj.xplane.manip.v2 = float(self.params[3])
            obj.xplane.manip.click_step = float(self.params[4])
            obj.xplane.manip.hold_step = float(self.params[5])
            obj.xplane.manip.dataref1 = self.params[6]

            #Tooltip may or may not be included
            if param_len >= 8:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[7:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 3 and cmd == "ATTR_manip_command_switch_left_right2":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_switch_left_right2"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.xplane.manip.command = self.params[2]

            #Tooltip may or may not be included
            if param_len >= 4:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[3:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 3 and cmd == "ATTR_manip_command_switch_up_down2":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_switch_up_down2"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.xplane.manip.command = self.params[2]

            #Tooltip may or may not be included
            if param_len >= 4:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[3:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 3 and cmd == "ATTR_manip_command_knob2":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_knob2"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.xplane.manip.command = self.params[2]

            #Tooltip may or may not be included
            if param_len >= 4:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[3:])
                obj.xplane.manip.tooltip = tooltip
        
        elif param_len >= 17 and cmd == "ATTR_manip_drag_rotate":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "drag_rotate"
            if len(self.detents) > 0:
                obj.xplane.manip.type = "drag_rotate_detent"
            obj.xplane.manip.cursor = self.params[1].lower()

        for det in self.detents:
            obj.xplane.manip.axis_detent_ranges.append((det.start, det.end, det.length))

    def copy(self):
        """
        Returns a copy of this manipulator object.
        """
        new_manip = manipulator()
        new_manip.valid = self.valid
        new_manip.params = self.params.copy()
        new_manip.detents = [detent.copy() for detent in self.detents]
        new_manip.wheel_delta = self.wheel_delta

        return new_manip

class draw_call_state:
    """
    Class to represent the state used in a draw call. This is separate because many DCs can have the same state, so when parsing, we just have a cur state object which we then attach to the DC
    """

    def __init__(self):
        self.blend = True
        self.blend_cutoff = 0.5
        self.draped = False
        self.cast_shadow = True
        self.surface_type = "none"

    def copy(self):
        """
        Returns a copy of this state object.
        """
        new_state = draw_call_state()
        new_state.blend = self.blend
        new_state.blend_cutoff = self.blend_cutoff
        new_state.draped = self.draped
        new_state.cast_shadow = self.cast_shadow
        new_state.surface_type = self.surface_type
        return new_state

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
        self.state = draw_call_state()  #State of the draw call. This is used to store the state of the draw call, such as blend mode, alpha cutoff, etc.
        self.manipulator = None  #Manipulator for the draw call. This is used to store the manipulator for the draw call, if it has one.

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

        if self.manipulator != None:
            self.manipulator.apply_to_obj(dc_obj)

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

        # Lastly, we need to get the correct material. Soo, here's out logic
        # First, we need to either get a regular material, or a draped material. 
        # From there, we need to check if the material matches our state - specifically, blend mode, alpha cutoff, shadows, and hard surface
        # So, with that in mind, we can iterate over all the materials in the list. We save the first basic and first draped we find, and keep going
        # If we find an actual match, we use it! If not, we create a new material based on the basic material we found, use that, and add it to the list
        basic_mat = None
        basic_draped_mat = None
        matching_mat = None
        for mat in in_mats:
            xp_props = mat.xp_materials

            #Save our basic materials
            if xp_props.draped and basic_draped_mat == None:
                basic_draped_mat = mat
            elif basic_mat == None:
                basic_mat = mat

            #Compare to state
            if xp_props.draped == self.state.draped and \
                xp_props.blend_alpha == self.state.blend and \
                xp_props.blend_cutoff == self.state.blend_cutoff and \
                xp_props.cast_shadow == self.state.cast_shadow and \
                xp_props.surface_type == self.state.surface_type.upper():
                matching_mat = mat

        if basic_draped_mat == None:
            basic_draped_mat = basic_mat

        #If we didn't get a matching material, we'll create a new one based on the basic
        if matching_mat == None:
            new_mat = None

            #Duplicate draped material
            if self.state.draped:
                new_mat = basic_draped_mat.copy()
            else:
                new_mat = basic_mat.copy()

            new_mat.xp_materials.draped = self.state.draped
            new_mat.xp_materials.blend_alpha = self.state.blend
            new_mat.xp_materials.blend_cutoff = self.state.blend_cutoff
            new_mat.xp_materials.cast_shadow = self.state.cast_shadow
            new_mat.xp_materials.surface_type = self.state.surface_type.upper()

            matching_mat = new_mat

            in_mats.append(new_mat)
                
        dc_obj.data.materials.append(matching_mat)

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
        self.lights = []  #List of lights for the animation
        self.children = []  #List of children anim_levels for the animation

    def add_to_scene(self, parent_obj, all_verts, all_indicies, in_mats, in_collection):
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
            dc_obj = dc.add_to_scene(all_verts, all_indicies, in_mats, in_collection)
            dc_obj.parent = self.last_action

            #So it doesn't take up it's parent's rotation
            eular = mathutils.Vector((0, 0, 0))
            anim_utils.set_obj_rotation_world(dc_obj, eular)

        #Dedupe our lights
        self.lights = misc_utils.dedupe_list(self.lights)
        for lt in self.lights:
            #Add the light to the scene
            new_light = lt.add_to_scene(in_collection)
            new_light.parent = self.last_action

            eular = new_light.rotation_euler
            anim_utils.set_obj_rotation_world(new_light, eular)

        #Now that we added out draw calls, it's time to recurse
        for child in self.children:
            child.add_to_scene(self.last_action, all_verts, all_indicies, in_mats, in_collection)

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
        self.draw_calls = [] #List of draw calls. This is a list of draw_call objects.
        self.lights = []  #List of lights in the object. This is a list of light objects
        self.anims = []  #List of animations in the object. This is a list of anim_levels
        self.name = ""

        #Base material
        self.alb_texture = ""
        self.nml_texture = ""
        self.lit_texture = ""
        self.mat_texture = ""
        self.do_blend_alpha = True
        self.blend_cutoff = 0.5
        self.cast_shadow = True
        #self.decal_one = props.PROP_decal()
        #self.decal_two = props.PROP_decal()
        self.layer_group = "objects"
        self.layer_group_offset = 0

        #Draped material
        self.draped_alb_texture = ""
        self.draped_nml_tile_rat = 1.0
        self.draped_nml_texture = ""
        self.draped_lit_texture = ""
        #self.draped_decal_one = props.PROP_decal()
        #self.draped_decal_two = props.PROP_decal()
        self.draped_layer_group = "objects"
        self.draped_layer_group_offset = -5
        

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
        cur_state = draw_call_state()
        cur_manipulator = manipulator()

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
                dc.state = cur_state  #Use the current state for this draw call
                cur_state = cur_state.copy()  #Reset the current state for the next draw call
                dc.start_index = int(tokens[1])
                dc.length = int(tokens[2])
                dc.lod_start = cur_start_lod
                dc.lod_end = cur_end_lod
                if cur_manipulator.valid:
                    dc.manipulator = cur_manipulator.copy()  #Copy the current manipulator to the draw call

                #Reset the current manipulator for the next draw call
                cur_manipulator = manipulator()

                #Add the draw call to the list of draw calls. This is the current animation in the tree, or the list of static draw calls it there is no current animation
                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this draw call to the current animation tree
                    cur_anim_tree[-1].draw_calls.append(dc)
                else:
                    self.draw_calls.append(dc)

            elif tokens[0] == "TEXTURE":
                self.alb_texture = tokens[1]
                if self.draped_alb_texture == "":
                    self.draped_alb_texture = tokens[1]
            
            elif tokens[0] == "TEXTURE_MAP":
                if tokens[1].lower() == "normal":
                    self.nml_texture = tokens[2]
                elif tokens[1].lower() == "material_gloss":
                    self.mat_texture = tokens[2]

            elif tokens[0] == "TEXTURE_NORMAL":
                self.nml_texture = tokens[1]
                if self.draped_nml_texture == "":
                    self.draped_nml_texture = tokens[1]

            elif tokens[0] == "TEXTURE_DRAPED":
                self.draped_alb_texture = tokens[1]

            elif tokens[0] == "TEXTURE_DRAPED_NORMAL":
                self.draped_nml_tile_rat = float(tokens[1])
                self.draped_nml_texture = tokens[2]

            elif tokens[0] == "TEXTURE_DRAPED_LIT":
                self.draped_lit_texture = tokens[1]

            elif tokens[0] == "TEXTURE_LIT":
                self.lit_texture = tokens[1]
                if self.draped_lit_texture == "":
                    self.draped_lit_texture = tokens[1]

            elif tokens[0] == "GLOBAL_no_blend":
                self.do_blend_alpha = False
                self.blend_cutoff = float(tokens[1])
                cur_state.blend = False
                cur_state.blend_cutoff = self.blend_cutoff

            elif tokens[0] == "GLOBAL_no_shadow":
                self.cast_shadow = False
                cur_state.cast_shadow = False

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

            elif tokens[0] == "LIGHT_NAMED":
                #LIGHT_NAMED <name> <x> <y> <z>
                new_light = light()
                new_light.lod_start = cur_start_lod
                new_light.lod_end = cur_end_lod
                new_light.xp_type = "named"
                new_light.name = tokens[1]
                new_light.loc_x = float(tokens[2]) * trans_matrix[0]
                new_light.loc_y = float(tokens[4]) * trans_matrix[1]
                new_light.loc_z = float(tokens[3]) * trans_matrix[2]

                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this light to the current animation tree
                    cur_anim_tree[-1].lights.append(new_light)

                else:
                    #Otherwise, add it directly to the lights list
                    self.lights.append(new_light)

            elif tokens[0] == "LIGHT_CUSTOM":
                #LIGHT_CUSTOM <x> <y> <z> <r> <g> <b> <a> <s> <s1> <t1> <s2> <t2> <dataref>
                new_light = light()
                new_light.lod_start = cur_start_lod
                new_light.lod_end = cur_end_lod
                new_light.xp_type = "custom"
                new_light.name = tokens[1]
                new_light.loc_x = float(tokens[1]) * trans_matrix[0]
                new_light.loc_y = float(tokens[3]) * trans_matrix[1]
                new_light.loc_z = float(tokens[2]) * trans_matrix[2]
                new_light.color_r = float(tokens[4])
                new_light.color_g = float(tokens[5])
                new_light.color_b = float(tokens[6])
                new_light.size = float(tokens[8])
                new_light.bb_s1 = float(tokens[9])
                new_light.bb_t1 = float(tokens[10])
                new_light.bb_s2 = float(tokens[11])
                new_light.bb_t2 = float(tokens[12])
                if len(tokens) > 13:
                    new_light.dataref = tokens[13]

                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this light to the current animation tree
                    cur_anim_tree[-1].lights.append(new_light)

                else:
                    #Otherwise, add it directly to the lights list
                    self.lights.append(new_light)

            elif tokens[0] == "LIGHT_SPILL_CUSTOM":
                #LIGHT_SPILL_CUSTOM <x> <y> <z> <r> <g> <b> <a> <s> <dx> <dy> <dz> <semi> <dref>
                new_light = light()
                new_light.lod_start = cur_start_lod
                new_light.lod_end = cur_end_lod
                new_light.xp_type = "light_spill_custom"
                new_light.name = tokens[1]
                new_light.loc_x = float(tokens[1]) * trans_matrix[0]
                new_light.loc_y = float(tokens[3]) * trans_matrix[1]
                new_light.loc_z = float(tokens[2]) * trans_matrix[2]
                new_light.color_r = float(tokens[4])
                new_light.color_g = float(tokens[5])
                new_light.color_b = float(tokens[6])
                new_light.size = float(tokens[8])
                new_light.dir_x = float(tokens[9]) * trans_matrix[0]
                new_light.dir_y = float(tokens[11]) * trans_matrix[1]
                new_light.dir_z = float(tokens[10]) * trans_matrix[2]
                #The cone angle is 2x the inverse cosine of the semi. This is in degrees.
                new_light.cone_angle = 2 * math.degrees(math.acos(float(tokens[12])))
                if len(tokens) > 13:
                    new_light.dataref = tokens[13]

                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this light to the current animation tree
                    cur_anim_tree[-1].lights.append(new_light)

                else:
                    #Otherwise, add it directly to the lights list
                    self.lights.append(new_light)

            elif tokens[0] == "LIGHT_PARAM":
                #This is the most complex light as it's parameters are variable based on it's type.
                #It's base format is: LIGHT_PARAM <name> <x> <y> <z> [<additional params>]
                #We get [<additional params>] based on the dictionary light_data.param_lights_dict.
                #We then iterate over the rest of the params, comparing them to the keys in the value of that name in the dictionary, and assigning values based on the key
                
                new_light = light()
                new_light.lod_start = cur_start_lod
                new_light.lod_end = cur_end_lod
                new_light.xp_type = "param"
                new_light.name = tokens[1]
                new_light.loc_x = float(tokens[2]) * trans_matrix[0]
                new_light.loc_y = float(tokens[4]) * trans_matrix[1]
                new_light.loc_z = float(tokens[3]) * trans_matrix[2]
                new_light.params = ""

                additional_params_keys = light_data.param_lights_dict.get(new_light.name, None)
                if additional_params_keys is None:
                    print(f"Unknown light type {new_light.name} in object {self.name}. Skipping light.")
                    continue

                #Make sure we have the right number of additional params
                if len(tokens) - 5 != len(additional_params_keys):
                    print(f"Light {new_light.name} in object {self.name} has {len(tokens) - 5} additional params, but expected {len(additional_params_keys)}. Skipping light.")
                    continue

                #Now iterate over the additional params and assign them to the light
                for i, param in enumerate(additional_params_keys):
                    if param == 'R':
                        new_light.color_r = float(tokens[i + 5])
                    elif param == 'G':
                        new_light.color_g = float(tokens[i + 5])
                    elif param == 'B':
                        new_light.color_b = float(tokens[i + 5])
                    elif param == 'DX':
                        new_light.dir_x = float(tokens[i + 5]) * trans_matrix[0]
                    elif param == 'DY':
                        new_light.dir_z = float(tokens[i + 5]) * trans_matrix[2]
                    elif param == 'DZ':
                        new_light.dir_y = float(tokens[i + 5]) * trans_matrix[1]
                    elif param == 'WIDTH':
                        #The cone angle is 2x the inverse cosine of the semi. This is in degrees.
                        new_light.cone_angle = 2 * math.degrees(math.acos(float(tokens[i + 5])))
                    elif param == 'INTENSITY' or param == 'SIZE':
                        light_size = tokens[i + 5]
                        if light_size.endswith('cd'):
                            new_light.is_photometric = True #What do we do with this? There's no setting in XP2B for this???
                            light_size = light_size[:-2] #Remove the 'cd' suffix
                            new_light.size = float(light_size)
                        else:
                            new_light.size = float(tokens[i + 5])

                        new_light.params += f" {light_size}"
                    #Everything else we just drop in the params string as there is no corresponding setting in Blender.
                    else:
                        new_light.params += f" {tokens[i + 5]}"

                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this light to the current animation tree
                    cur_anim_tree[-1].lights.append(new_light)

                else:
                    #Otherwise, add it directly to the lights list
                    self.lights.append(new_light)
                pass

            elif tokens[0] == "ATTR_draped":
                cur_state.draped = True

            elif tokens[0] == "ATTR_no_draped":
                cur_state.draped = False

            elif tokens[0] == "ATTR_no_shadow":
                cur_state.cast_shadow = False

            elif tokens[0] == "ATTR_shadow":
                cur_state.cast_shadow = True

            elif tokens[0] == "ATTR_no_blend":
                cur_state.blend = False
                if len(tokens) > 1:
                    cur_state.blend_cutoff = float(tokens[1])

            elif tokens[0] == "ATTR_blend":
                cur_state.blend = True
                cur_state.blend_cutoff = 0.5
    
            elif tokens[0] == "ATTR_hard":
                cur_state.surface_type = tokens[1]

            elif tokens[0] == "ATTR_hard_deck":
                cur_state.surface_type = tokens[1]

            elif tokens[0] == "ATTR_no_hard":
                cur_state.surface_type = "none"

            elif tokens[0] == "ATTR_layer_group":
                self.layer_group = tokens[1]
                self.layer_group_offset = int(tokens[2]) if len(tokens) > 2 else 0

            elif tokens[0] == "ATTR_draped_layer_group":
                self.draped_layer_group = tokens[1]
                self.draped_layer_group_offset = int(tokens[2]) if len(tokens) > 2 else 0

            elif tokens[0] == "ATTR_manip_wheel":
                cur_manipulator.wheel_delta = float(tokens[1]) if len(tokens) > 1 else 0

            elif tokens[0] == "ATTR_axis_detented":
                new_detent = manipulator_detent()
                new_detent.start = float(tokens[1])
                new_detent.end = float(tokens[2])
                new_detent.length = float(tokens[3])
                cur_manipulator.detents.append(new_detent)

            elif tokens[0] == "ATTR_manip_keyframe":
                #TODO: What does this even do? I don't understand docs nor see corresponding settings in X-Plane2Blender
                pass

            elif tokens[0] == "ATTR_manip_device":
                #TODO: Not implemented in XP2Blender, so nothing we can do afaik
                pass

            elif tokens[0].startswith("ATTR_manip"):
                cur_manipulator.valid = True
                cur_manipulator.params = tokens.copy()
                
    def to_scene(self):
        #Create a new collection for this object
        collection = bpy.data.collections.new(self.name)
        collection.name = self.name
        bpy.context.scene.collection.children.link(collection)

        #Create the base material
        all_mats = []
        mat = bpy.data.materials.new(name=self.name)
        mat.use_nodes = True
        xp_mat = mat.xp_materials
        xp_mat.alb_texture = self.alb_texture
        xp_mat.normal_texture = self.nml_texture
        if self.mat_texture != "":
            xp_mat.material_texture = self.mat_texture
            xp_mat.do_separate_material_texture = True
        xp_mat.lit_texture = self.lit_texture
        xp_mat.blend_alpha = self.do_blend_alpha
        xp_mat.blend_cutoff = self.blend_cutoff
        xp_mat.cast_shadow = self.cast_shadow
        mat.name = self.name

        all_mats.append(mat)

        #Create the draped material if it exists
        if self.draped_alb_texture != "":
            draped_mat = bpy.data.materials.new(name=self.name + "_draped")
            draped_mat.use_nodes = True
            xp_draped_mat = draped_mat.xp_materials
            xp_draped_mat.alb_texture = self.draped_alb_texture
            xp_draped_mat.normal_texture = self.draped_nml_texture
            xp_draped_mat.lit_texture = self.draped_lit_texture
            xp_draped_mat.do_blend_alpha = self.do_blend_alpha
            xp_draped_mat.blend_cutoff = self.blend_cutoff
            xp_draped_mat.cast_shadow = self.cast_shadow
            xp_draped_mat.draped = True
            xp_draped_mat.draped_nml_tile_rat = self.draped_nml_tile_rat
            draped_mat.name = self.name + "_draped"

            all_mats.append(draped_mat)

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
            dc.add_to_scene(self.verticies, self.indicies, all_mats, collection)

        #For basic lights just add them
        self.lights = misc_utils.dedupe_list(self.lights)
        for lt in self.lights:
            lt.add_to_scene(collection)

        #Now that we have the basic geometery, we need to add the animated stuff.
        #This is very simple. We iterate through all our root animation levels, and add them to the scene. Aka we call the function to do the hard (sort of) stuff
        for anim in self.anims:
            anim.add_to_scene(None, self.verticies, self.indicies, all_mats, collection)
        
        #WE'RE DONE!