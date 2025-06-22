#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      4-24/2025
#Module:    xp_obj.py
#Purpose:   Provide a class that abstracts the X-Plane object, and provides functions to import the object into Blender

import bpy
import os
import mathutils
import math

from .. import material_config
from ..Helpers import misc_utils
from ..Helpers import anim_utils
from ..Helpers import geometery_utils
from ..Helpers import anim_utils
from ..Helpers import light_data    #These are defines for the parameter layout of PARAM lights
from ..Helpers import decal_utils
from ..Helpers import log_utils

from functools import total_ordering

#Lights don't actually use LODs, but if there are LOD buckets, XP2B requires them to be in *one*. But if there's no LOD buckets they can't be in *any*. So we have a single global variable to set what bucket ot put them in
obj_does_use_lods = False

class wiper_param:
    """
    Class to represent the parameters for a wiper animation.
    """

    def __init__(self):
        self.dataref = ""
        self.start = 0.0
        self.end = 0.0
        self.width = 0.0

class cockpit_region:
    """
    Class to represent a region in the cockpit for panel textures.
    """
    
    def __init__(self):
        self.left = 0.0
        self.bottom = 0.0
        self.width = 1.0
        self.height = 1.0

class thermal_source:
    """
    Class to represent a thermal source in an X-Plane object.
    """

    def __init__(self):
        self.dataref = ""
        self.toggle_dataref = ""
        self.temperature = 0.0

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
        self.index = 0 #XP Param
        self.size = 0   #Light size measurement
        self.is_photometric = False #True if this light is photometric
        self.params = "" #String of additional params for the light, from LIGHT_PARAM
        self.bb_s1 = 0 #Left UV coordinate of the custom billboard light texture
        self.bb_s2 = 0 #Right UV coordinate of the custom billboard light texture
        self.bb_t1 = 0 #Top UV coordinate of the custom billboard light texture
        self.bb_t2 = 0 #Bottom UV coordinate of the custom billboard light texture
        self.frequency = 0 #Frequency of the light, used in beacons
        self.phase = 0 #Phase of the light, used in beacons
        self.lod_start = 0  #Start range of the LOD. We don't actually use LODs because lights aren't LODed, but, this is used to dedupe
        self.lod_end = 0    #End range of the LOD
        self.lod_bucket = -1  #LOD bucket of the light. This is used to determine which LOD bucket this light belongs to. -1 means no LOD bucket.

    def add_to_scene(self, in_collection, in_parent=None):
        """
        Adds a new light to the Blender scene with the specified properties.
        """

        # Create a new Blender light datablock
        light_data = bpy.data.lights.new(name="Light", type=self.type)
        b_light = bpy.data.objects.new(name="Light", object_data=light_data)
        in_collection.objects.link(b_light)

        b_light.data.color = (self.color_r, self.color_g, self.color_b)
        b_light.data.energy = self.size / 50 if self.is_photometric else self.size * 2  # All just kinda guesses here, these seem sort of correct. It's just visual anyway...
        if self.type == "SPOT":
            b_light.data.spot_size = math.radians(self.cone_angle)

        if in_parent != None:
            b_light.parent = in_parent
        
        anim_utils.set_obj_position_world(b_light, (self.loc_x, self.loc_y, self.loc_z))

        b_light.rotation_mode = 'XYZ'

        light_euler = anim_utils.euler_to_align_z_with_vector((-self.dir_x, -self.dir_y, -self.dir_z))
        anim_utils.set_obj_rotation_world(b_light, light_euler)

        #b_light.data.xplane.type = self.xp_type    #Let all lights use automatic for now
        b_light.data.xplane.params = self.params
        b_light.data.xplane.param_size = self.size
        b_light.data.xplane.param_intensity_new = self.size
        b_light.data.xplane.uv[0] = self.bb_s1   # left
        b_light.data.xplane.uv[1] = self.bb_t1   # top
        b_light.data.xplane.uv[2] = self.bb_s2   # right
        b_light.data.xplane.uv[3] = self.bb_t2   # bottom
        b_light.data.xplane.dataref = self.dataref
        b_light.data.xplane.param_index = self.index
        b_light.data.xplane.name = self.name
        b_light.data.xplane.param_freq = self.frequency
        b_light.data.xplane.param_phase = self.phase
        if obj_does_use_lods:
            b_light.xplane.lod[0] = True

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
                self.frequency == value.frequency and
                self.phase == value.phase and
                self.index == value.index and
                (self.lod_start != value.lod_start or
                self.lod_end != value.lod_end))

    def __lt__(self, other):
        """
        Less than operator for light objects. This is used to sort lights by their LOD range.
        """
        return (self.name, self.type, self.xp_type, self.color_r, self.color_g,self.color_b,self.loc_x,self.loc_y,self.loc_z,self.dir_x,self.dir_y,self.dir_z,self.cone_angle,self.dataref,self.size, self.is_photometric, self.params, self.xp_type, self.bb_s1, self.bb_s2, self.bb_t1, self.bb_t2, self.frequency, self.phase, self.index) < \
        (other.name, other.type, other.xp_type, other.color_r, other.color_g, other.color_b, other.loc_x, other.loc_y, other.loc_z, other.dir_x, other.dir_y, other.dir_z, other.cone_angle, other.dataref, other.size, other.is_photometric, other.params, other.xp_type, other.bb_s1, other.bb_s2, other.bb_t1, other.bb_t2, other.frequency, other.phase, other.index)

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
        self.detent_axis = mathutils.Vector((0, 0, 0))  #Axis of the manipulator's detent. This is used to set the axis of the manipulator for drag_axis and drag_rotate manips
        self.detent_v1 = 0
        self.detent_v2 = 0
        self.detent_dataref = ""  #Dataref for the detent manipulator. This is used to set the dataref for the manipulator for drag_axis and drag_rotate manips
    
    def get_datarefs_for_axis_or_rotate(self):
        if len(self.params) == 0:
            return False, []
        
        cmd = self.params[0]

        out_list = []

        animateable = False

        if cmd == "ATTR_manip_drag_axis" and len(self.params) >= 8:
            #This is a drag axis manipulator
            out_list.append(self.params[7])
            animateable = True

        if cmd == "ATTR_manip_drag_rotate" and len(self.params) >= 17:
            #This is a drag rotate manipulator
            out_list.append(self.params[15])
            out_list.append(self.params[16])
            animateable = True

        if self.detent_dataref != "":
            #If we have a detent dataref, we need to add it too
            out_list.append(self.detent_dataref)

        return animateable, out_list

    def apply_to_obj(self, obj, do_animate=False, in_collection=None):
        """
        Applies the manipulator settings to the given Blender object
        """
        param_len = len(self.params)

        if param_len == 0:
            #If there are no params, we can't apply this manipulator
            return None

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
            obj.xplane.manip.command = self.params[2]

            #Tooltip may or may not be included
            if param_len >= 4:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[3:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 3 and cmd == "ATTR_manip_command_switch_up_down2":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_switch_up_down2"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.command = self.params[2]

            #Tooltip may or may not be included
            if param_len >= 4:
                #Concat all the remaining params into a single string
                tooltip = " ".join(self.params[3:])
                obj.xplane.manip.tooltip = tooltip

        elif param_len >= 3 and cmd == "ATTR_manip_command_knob2":
            obj.xplane.manip.enabled = True
            obj.xplane.manip.type = "command_knob2"
            obj.xplane.manip.cursor = self.params[1].lower()
            obj.xplane.manip.command = self.params[2]

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

            log_utils.warning(f"Drag rotate manipulators are autodetected by X-Plane2Blender. Depending on this object's authoring, X-Plane2Blender may not autodetect this manipulator, requiring manual changes. Obj is {obj.name}")

        for det in self.detents:
            obj.xplane.manip.axis_detent_ranges.add()
            obj.xplane.manip.axis_detent_ranges[-1].start = det.start
            obj.xplane.manip.axis_detent_ranges[-1].end = det.end
            obj.xplane.manip.axis_detent_ranges[-1].height = det.length

            log_utils.warning("This manipulator has detents. X-Plane2Blender autodetects detents, but depending on the authoring of this object, it may not be able to detect them, requiring manual changes. Obj is " + obj.name)

        #Now we need to add animations if applicable
        if do_animate:
            return None
        
            # When I started writing this I thought it'd be easy. We have a manipulator mesh and we have the desired action right, so we just move it on that axis right?
            # That part is easy. But guess what? Now we moved the MESH and it's no longer where it was SUPPOSED to be!!! Sooo then that gives us the question - what was the original intent of the manipulator???
            # For example, in the default 172, the overhead lights have a slider for their brightness. The manipulator covers the entire physical slider.
            # In this situation, the manipulator acts sort of like a touch screen. So accepting the movement is fine, but if we MOVE the ENTIRE "touchscreen" that's a problem!
            # So for now this code is disabled, and will *likely* remain that way.
            # We're just keeping it here in case we get direction otherwise, or find out I and am missing something obvious


            #We will only potentially animate drag axis and rotation_axis manips, as all the other ones are just data
            if cmd == "ATTR_manip_drag_axis":
                manip_mesh_original_rotation = obj.rotation_euler.copy()  #Save the original rotation of the object, so we can restore it later
                manip_mesh_original_location = obj.location.copy()  #Save the original location of the object, so we can restore it later
                manip_mesh_original_parent = obj.parent  #Save the original parent of the object, so we can restore it later

                #Since this is along an axis, our first step is to add an empty that is aligned to the axis
                axis_empty = bpy.data.objects.new("Manipulator Axis", None)
                axis_empty.empty_display_type = "ARROWS"
                axis_empty.empty_display_size = 0.05
                in_collection.objects.link(axis_empty)

                rot_vector = mathutils.Vector((float(self.params[2]), float(self.params[4]) * -1, float(self.params[3])))

                #Now we will animate our empty. 
                #The way XP stores the length of the animation is a little weird - the alignment vector is *not* normalized, rather it's length is the length of the animation!!!
                #So get that length. Keyframe at local Z = 0 then local Z = length of the alignment vector
                alignment_length = rot_vector.length
                axis_empty.location = manip_mesh_original_location.copy()
                anim_utils.add_xp_dataref_track(axis_empty, self.params[7])
                anim_utils.goto_frame(0)
                anim_utils.keyframe_obj_location(axis_empty)
                anim_utils.keyframe_xp_dataref(axis_empty, self.params[7], float(self.params[5]))
                anim_utils.goto_frame(1)
                new_pos = anim_utils.move_along_axis(axis_empty.location, rot_vector, alignment_length)
                axis_empty.location = new_pos
                anim_utils.keyframe_obj_location(axis_empty)
                anim_utils.keyframe_xp_dataref(axis_empty, self.params[7], float(self.params[6]))

                #Now we have our basic movement animated!!! Next up we have to worry about the detent - if there is one
                if len(self.detents) > 0:
                    detent_empty = bpy.data.objects.new("Manipulator Detent Axis", None)
                    detent_empty.empty_display_type = "ARROWS"
                    detent_empty.empty_display_size = 0.05
                    in_collection.objects.link(detent_empty)

                    #Note these values have already been trasnformed from XP space to Blender space
                    rot_vector_detent = mathutils.Vector((float(self.detent_axis.x), float(self.detent_axis.y), float(self.detent_axis.z)))

                    #Now we will animate our detent empty.
                    alignment_length_detent = rot_vector_detent.length
                    detent_empty.location = mathutils.Vector((0, 0, 0))
                    anim_utils.add_xp_dataref_track(detent_empty, self.detent_dataref)
                    anim_utils.goto_frame(0)
                    anim_utils.keyframe_obj_location(detent_empty)
                    anim_utils.keyframe_xp_dataref(axis_empty, self.detent_dataref, self.detent_v1)
                    anim_utils.goto_frame(1)
                    new_pos = anim_utils.move_along_axis(detent_empty.location, rot_vector_detent, alignment_length_detent)
                    detent_empty.location = new_pos
                    anim_utils.keyframe_obj_location(detent_empty)
                    anim_utils.keyframe_xp_dataref(axis_empty, self.detent_dataref, self.detent_v2)

                    #Parent our object to the detent empty
                    axis_empty.parent = detent_empty
                    obj.parent = detent_empty
                    #Reset the positions since they're done via the parent
                    obj.location = mathutils.Vector((0, 0, 0))
                    obj.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')

                else:
                    #If there is no detent, we just parent it to the manipulator object
                    obj.parent = axis_empty
                    #Reset the positions since they're done via the parent
                    obj.location = mathutils.Vector((0, 0, 0))
                    obj.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')

                #Now the fun part *cries*. We need to parent this object to the manipulator mesh's parent. 
                # The good news is since the object was already parented, we have the desired rotation (we already dealt with the location when animating)
                # So all we need to do is set the rotation of the empty to match the manipulator mesh's rotation.
                # This works because we didn't actually rotate before - we just moved it *along* the axis, so we can just use the absolute rotation without worrying about merging
                # EDIT: This is called on an *unparented* object, so we don't even need to worry here! This will get parented instead of the obj then transforms will be applied int he natural process
                axis_empty.rotation_euler = manip_mesh_original_rotation
                axis_empty.location = manip_mesh_original_location
                axis_empty.parent = manip_mesh_original_parent

                return axis_empty

            elif cmd == "ATTR_manip_drag_rotate":
                pass
        return None
        
    def copy(self):
        """
        Returns a copy of this manipulator object.
        """
        new_manip = manipulator()
        new_manip.valid = self.valid
        new_manip.params = self.params.copy()
        new_manip.detents = self.detents.copy()
        new_manip.wheel_delta = self.wheel_delta
        new_manip.detent_axis = self.detent_axis.copy()
        new_manip.detent_v1 = self.detent_v1
        new_manip.detent_v2 = self.detent_v2
        new_manip.detent_dataref = self.detent_dataref

        return new_manip

class draw_call_state:
    """
    Class to represent the state used in a draw call. This is separate because many DCs can have the same state, so when parsing, we just have a cur state object which we then attach to the DC
    """

    def __init__(self):
        self.blend_mode = "BLEND"
        self.blend_cutoff = 0.5
        self.draped = False
        self.cast_shadow = True
        self.surface_type = "none"
        self.light_level_override = False
        self.draw = True
        self.hard_camera = False
        self.light_level_v1 = 0
        self.light_level_v2 = 0
        self.light_level_photometric = False
        self.light_level_brightness = 0
        self.light_level_dataref = ""
        self.is_hud = False

        #Cockpit device properties
        self.use_2d_panel = False
        self.panel_texture_region = 0
        self.cockpit_device = "NONE"
        self.custom_cockpit_device = ""
        self.cockpit_device_use_bus_1 = False
        self.cockpit_device_use_bus_2 = False
        self.cockpit_device_use_bus_3 = False
        self.cockpit_device_use_bus_4 = False
        self.cockpit_device_use_bus_5 = False
        self.cockpit_device_use_bus_6 = False
        self.cockpit_device_lighting_channel = 0

    def copy(self):
        """
        Returns a copy of this state object.
        """
        new_state = draw_call_state()
        new_state.blend_mode = self.blend_mode
        new_state.blend_cutoff = self.blend_cutoff
        new_state.draped = self.draped
        new_state.cast_shadow = self.cast_shadow
        new_state.surface_type = self.surface_type
        new_state.draw = self.draw
        new_state.hard_camera = self.hard_camera
        new_state.light_level_override = self.light_level_override
        new_state.light_level_v1 = self.light_level_v1
        new_state.light_level_v2 = self.light_level_v2
        new_state.light_level_photometric = self.light_level_photometric
        new_state.light_level_brightness = self.light_level_brightness
        new_state.light_level_dataref = self.light_level_dataref
        new_state.is_hud = self.is_hud
        new_state.use_2d_panel = self.use_2d_panel
        new_state.panel_texture_region = self.panel_texture_region
        new_state.cockpit_device = self.cockpit_device
        new_state.custom_cockpit_device = self.custom_cockpit_device
        new_state.cockpit_device_use_bus_1 = self.cockpit_device_use_bus_1
        new_state.cockpit_device_use_bus_2 = self.cockpit_device_use_bus_2
        new_state.cockpit_device_use_bus_3 = self.cockpit_device_use_bus_3
        new_state.cockpit_device_use_bus_4 = self.cockpit_device_use_bus_4
        new_state.cockpit_device_use_bus_5 = self.cockpit_device_use_bus_5
        new_state.cockpit_device_use_bus_6 = self.cockpit_device_use_bus_6
        new_state.cockpit_device_lighting_channel = self.cockpit_device_lighting_channel
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

    def add_to_scene(self, all_verts, all_indicies, in_mats, in_collection, in_parent=None):
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

        override_return_obj = None

        if self.manipulator != None:
            #Now we need to check if we need to animate it because there isn't an animating parent
            animatable, datarefs = self.manipulator.get_datarefs_for_axis_or_rotate()

            do_need_animate = True

            cur_parent = in_parent

            #Check if *any* of the parents here use the same datarefs. Not perfect but it's a best guess of whether the parent provides the given animation
            #Temporarily disabled. See line 517, toward end of manipulator.apply_to_obj
            #TODO: Re-enable this, but give a warning instead if we find we're not animated
            while True:
                if cur_parent == None:
                    break
                for dref in cur_parent.xplane.datarefs:
                    for used_dref in datarefs:
                        if dref.path == used_dref:
                            #If we find a dataref that matches, we don't need to animate this manipulator
                            do_need_animate = False
                            break

                cur_parent = cur_parent.parent

            if do_need_animate and (self.manipulator.params[0] == "ATTR_manip_drag_axis" or self.manipulator.params[0] == "ATTR_manip_drag_rotate"):
                log_utils.warning(f"Manipulator {self.manipulator.params[0]} on object {dc_obj.name} is not animated. X-Plane2Blender autodetects these manipulators from animations, so without animations, the manipulator will throw an error on export. Manual fixing is required for this object's manipulator. Obj is {dc_obj.name}")

            override_return_obj = self.manipulator.apply_to_obj(dc_obj)

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
                log_utils.warning(f"Unknown LOD bucket for obj {dc_obj.name} for range {self.lod_start}-{self.lod_end}. Bucket is {self.lod_bucket}. What?")

        #Set HUD state
        dc_obj.xplane.hud_glass = self.state.is_hud

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
                xp_props.blend_mode == self.state.blend_mode and \
                xp_props.blend_cutoff == self.state.blend_cutoff and \
                xp_props.cast_shadow == self.state.cast_shadow and \
                xp_props.surface_type == self.state.surface_type.upper() and \
                xp_props.drawing_enabled == self.state.draw and \
                xp_props.camera_collision_enabled == self.state.hard_camera and \
                xp_props.light_level_override == self.state.light_level_override and \
                xp_props.light_level_v1 == self.state.light_level_v1 and \
                xp_props.light_level_v2 == self.state.light_level_v2 and \
                xp_props.light_level_photometric == self.state.light_level_photometric and \
                xp_props.light_level_brightness == self.state.light_level_brightness and \
                xp_props.light_level_dataref == self.state.light_level_dataref and \
                xp_props.use_2d_panel_texture == self.state.use_2d_panel and \
                xp_props.panel_texture_region == self.state.panel_texture_region and \
                xp_props.cockpit_device.upper() == self.state.cockpit_device and \
                xp_props.custom_cockpit_device == self.state.custom_cockpit_device and \
                xp_props.cockpit_device_use_bus_1 == self.state.cockpit_device_use_bus_1 and \
                xp_props.cockpit_device_use_bus_2 == self.state.cockpit_device_use_bus_2 and \
                xp_props.cockpit_device_use_bus_3 == self.state.cockpit_device_use_bus_3 and \
                xp_props.cockpit_device_use_bus_4 == self.state.cockpit_device_use_bus_4 and \
                xp_props.cockpit_device_use_bus_5 == self.state.cockpit_device_use_bus_5 and \
                xp_props.cockpit_device_use_bus_6 == self.state.cockpit_device_use_bus_6 and \
                xp_props.cockpit_device_lighting_channel == self.state.cockpit_device_lighting_channel:
                
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
            new_mat.xp_materials.blend_mode = self.state.blend_mode.upper()
            new_mat.xp_materials.blend_cutoff = self.state.blend_cutoff
            new_mat.xp_materials.cast_shadow = self.state.cast_shadow
            new_mat.xp_materials.surface_type = self.state.surface_type.upper()
            new_mat.xp_materials.drawing_enabled = self.state.draw
            new_mat.xp_materials.camera_collision_enabled = self.state.hard_camera
            new_mat.xp_materials.light_level_override = self.state.light_level_override
            new_mat.xp_materials.light_level_v1 = self.state.light_level_v1
            new_mat.xp_materials.light_level_v2 = self.state.light_level_v2
            new_mat.xp_materials.light_level_photometric = self.state.light_level_photometric
            new_mat.xp_materials.light_level_brightness = int(float(self.state.light_level_brightness))
            new_mat.xp_materials.light_level_dataref = self.state.light_level_dataref
            new_mat.xp_materials.use_2d_panel_texture = self.state.use_2d_panel
            new_mat.xp_materials.panel_texture_region = self.state.panel_texture_region
            new_mat.xp_materials.cockpit_device = self.state.cockpit_device
            new_mat.xp_materials.custom_cockpit_device = self.state.custom_cockpit_device
            new_mat.xp_materials.cockpit_device_use_bus_1 = self.state.cockpit_device_use_bus_1
            new_mat.xp_materials.cockpit_device_use_bus_2 = self.state.cockpit_device_use_bus_2
            new_mat.xp_materials.cockpit_device_use_bus_3 = self.state.cockpit_device_use_bus_3
            new_mat.xp_materials.cockpit_device_use_bus_4 = self.state.cockpit_device_use_bus_4
            new_mat.xp_materials.cockpit_device_use_bus_5 = self.state.cockpit_device_use_bus_5
            new_mat.xp_materials.cockpit_device_use_bus_6 = self.state.cockpit_device_use_bus_6
            new_mat.xp_materials.cockpit_device_lighting_channel = self.state.cockpit_device_lighting_channel

            matching_mat = new_mat

            in_mats.append(new_mat)
                
        dc_obj.data.materials.append(matching_mat)

        if override_return_obj != None:
            #If we have a manipulator, we return the object that was created by the manipulator
            return override_return_obj
        
        return dc_obj

class static_offsets:
    """
    Class to represent a series of transformations that need to take place on an object in a certain order
    """
    def __init__(self):
        self.actions = []   #Tuples. xyz offsets or xyz euler
        self.action_types = []  #translate or rotate

    def copy(self):
        """
        Returns a copy of this static offsets object.
        """
        new_offsets = static_offsets()
        new_offsets.actions = self.actions.copy()
        new_offsets.action_types = self.action_types.copy()
        return new_offsets

    def apply(self, obj):
        """
        Applies the static offsets to the given object. This will apply all the actions in the order they were added.
        
        Args:
            obj (bpy.types.Object): The Blender object to apply the static offsets to.
        """

        if len(self.actions) == 0:
            #If there are no actions, we don't need to do anything
            return

        cur_location = mathutils.Vector((0, 0, 0))
        total_rot = mathutils.Euler((0, 0, 0), 'XYZ')

        reversed_actions = self.actions.copy()
        reversed_actions.reverse()
        reversed_types = self.action_types.copy()
        reversed_types.reverse()

        # Add the current loc/rot as actions. We do these here because it's just easier to apply them with all the same logic.
        # Note, we need to get these as translations/axis-angle rotations, as if they were animations. So that means translation in world space relative to the parent, and world space rotation to axis-angle
        obj_loc = mathutils.Vector(anim_utils.get_obj_position_world(obj))
        parent_loc = mathutils.Vector((0, 0, 0))
        if obj.parent != None:
            parent_loc = mathutils.Vector(anim_utils.get_obj_position_world(obj.parent))
        cur_translation = (obj_loc.x - parent_loc[0], obj_loc.y - parent_loc[1], obj_loc.z - parent_loc[2])
        reversed_actions.insert(0, cur_translation)
        reversed_types.insert(0, 'translate')

        original_axis, original_rot = anim_utils.euler_to_axis_angle(anim_utils.get_obj_rotation_world(obj))
        reversed_actions.insert(0, (original_axis, original_rot))
        reversed_types.insert(0, 'rotate')

        for i, action in enumerate(reversed_actions):
            action_type = reversed_types[i]

            if action_type == 'translate':
                #Apply translation
                cur_location.x += action[0]
                cur_location.y += action[1]
                cur_location.z += action[2]

            elif action_type == 'rotate':
                cur_location, total_rot = anim_utils.rotate_point_and_euler(cur_location, total_rot, action[0], action[1])

        #Apply the final location and rotation to the object
        new_pos = (parent_loc.x + cur_location.x, parent_loc.y + cur_location.y, parent_loc.z + cur_location.z)
        anim_utils.set_obj_position_world(obj, new_pos)

        #base_rot = anim_utils.get_obj_rotation_world(obj)
        #new_rot = (total_rot.to_quaternion() @ base_rot.to_quaternion()).to_euler('XYZ')
        anim_utils.set_obj_rotation_world(obj, total_rot)

class anim_action:
    """
    Base class for all animation actions
    """

    def __init__(self):
        self.type = ''
        self.empty = None  #Empty for the animation
        self.static_offsets = static_offsets()  #Static offsets for the animation. This is used to store the static offsets for the animation, such as translation and rotation
        self.show_hide_commands = []  #List of show/hide commands for the animation

class anim_show_hide_command:
    """
    Class to represent a single show/hide command in an animation
    """

    def __init__(self):
        self.hide = False  #True if this command is a hide command. Otherwise, it's a show command
        self.start_value = 0  #Min dref value to show/hide at
        self.end_value = 0  #Max dref value to show/hide at
        self.dataref = ""  #Dataref for the animation

    def apply(self, obj):
        obj.xplane.datarefs.add()
        obj.xplane.datarefs[-1].path = self.dataref
        if self.hide:
            obj.xplane.datarefs[-1].anim_type = 'hide'
        else:
            obj.xplane.datarefs[-1].anim_type = 'show'
        obj.xplane.datarefs[-1].show_hide_v1 = self.start_value
        obj.xplane.datarefs[-1].show_hide_v2 = self.end_value

    def copy(self):
        """
        Returns a copy of this show/hide command object.
        """
        new_cmd = anim_show_hide_command()
        new_cmd.hide = self.hide
        new_cmd.start_value = self.start_value
        new_cmd.end_value = self.end_value
        new_cmd.dataref = self.dataref
        return new_cmd

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

    def add_to_scene(self, parent_obj, all_verts, all_indicies, in_mats, in_collection, initial_static_offsets=None, initial_show_hide_commands=None):

        #For static translations, we will not create a new empty, rather we will just move all children by their translation
        cur_static_offsets = static_offsets()  #This will hold the static offsets for the animation level
        if initial_static_offsets != None:
            cur_static_offsets = initial_static_offsets.copy()

        cur_show_hide_commands = []  #This will hold the show/hide commands for the animation level
        if initial_show_hide_commands != None:
            cur_show_hide_commands = initial_show_hide_commands.copy()

        #Create a new empty for this animation level
        self.last_action = parent_obj
        cur_parent = parent_obj
        
        #Add all the actions, creating the hierarchy of empties with their rotations set. 
        for i, action in enumerate(self.actions):
            # Check if this is a drawcall, light, or. If so, we'll parent them to the last action. 
            # We need to do this on an action level because some objects may have actions, dc, more actions, more dcs, etc. And the dcs only have the actions *before* them applied.
            # So treating everything in an ANIM_begin/end pair as being effected by all the actions don't work :(
            # We don't actually have to do anything different with actions though because we are just parenting the dcs/lights to the last aciton. We don't actually change the meat of the action hierarchy
            # Also note again because next actions are *siblings* rather than children of this dc/light, we don't reset show/hide or static offset
            if isinstance(action, anim_level):
                action.add_to_scene(self.last_action, all_verts, all_indicies, in_mats, in_collection, cur_static_offsets.copy(), cur_show_hide_commands.copy())
            elif isinstance(action, draw_call):
                dc_obj = action.add_to_scene(all_verts, all_indicies, in_mats, in_collection)
                dc_obj.parent = self.last_action

                #So it doesn't take up it's parent's rotation
                eular = mathutils.Vector((0, 0, 0))
                anim_utils.set_obj_rotation_world(dc_obj, eular)

                #Apply the static offsets to the draw call object
                cur_static_offsets.apply(dc_obj)

                #Apply show hide animations
                for cmd in cur_show_hide_commands:
                    cmd.apply(dc_obj)

            elif isinstance(action, light):
                #Add the light to the scene. THis function takes the parent and sets the world space positon/rotation
                new_light = action.add_to_scene(in_collection, self.last_action)

                #Apply the static offsets to the light object
                cur_static_offsets.apply(new_light)  

                #Apply show hide animations
                for cmd in cur_show_hide_commands:
                    cmd.apply(new_light)

            elif isinstance(action, anim_action):
                #Create the empty for this action
                name = f"Anim"
                if len(self.draw_calls) > 0:
                    name += f" TRIS {self.draw_calls[0].start_index} {self.draw_calls[0].length}"
                name += f" Pt {i}"
                if action.type == 'rot_table_vector_transform':
                    name += " Rotation Transform"
                elif action.type == 'rot_keyframe':
                    name += " Static Rotation"
                    cur_static_offsets.actions.append((action.rot_vector, action.rot))
                    cur_static_offsets.action_types.append('rotate')
                    continue  #Static rotations are not animated, so we don't create a new empty for them
                elif action.type == 'loc_keyframe':
                    name += " Static Translation"
                    cur_static_offsets.actions.append(action.loc)
                    cur_static_offsets.action_types.append('translate')
                    continue  #Static translations are not animated, so we don't create a new empty for them
                elif action.type == 'loc_table':
                    name += " Keyframed Translation"
                elif action.type == 'rot_table':
                    name += " Keyframed Rotation"
                elif action.type == 'show_hide_series':
                    name += " Show/Hide Series"
                    for cmd in action.commands:
                        cur_show_hide_commands.append(cmd.copy())
                    continue  #Show/hide series are not animated, so we don't create a new empty for them. Their commands will be attached to all their direct children
                
                #Create the new objetc and link it
                anim_empty = bpy.data.objects.new(name, None)
                anim_empty.empty_display_type = "ARROWS"
                anim_empty.empty_display_size = 0.05
                in_collection.objects.link(anim_empty)
                self.actions[i].empty = anim_empty

                #Set this actions base loc/rot transforms and reset the offsets
                action.static_offsets = cur_static_offsets.copy()
                cur_static_offsets = static_offsets()  #Reset the static offsets for the next action

                #Apply show hide animations
                for cmd in cur_show_hide_commands:
                    cmd.apply(anim_empty)

                #Reset dataref show/hide commands
                action.show_hide_commands = cur_show_hide_commands.copy()
                cur_show_hide_commands = []  #Reset the show/hide commands for the next action

                #Reset the offsets because future objetcs will be parented to this one,
                if cur_parent != None:
                    anim_empty.parent = cur_parent
                cur_parent = anim_empty
            
                #If it is a rotation we need to align it to the rotation vector
                if action.type == 'rot_table_vector_transform':
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
                    log_utils.warning(f"Unknown action type {action.type} for animation {anim_empty.name}. This is not expected, please report this on this plugin's Github.")

                #Set the first/last actions
                if i == 0:
                    self.first_action = anim_empty
                self.last_action = anim_empty

                #Reset our frame
                anim_utils.goto_frame(0)
            
            else:
                log_utils.warning(f"Unknown action type for animation {action}. This is not expected, please report this on this plugin's Github.")

        #Now that we added out draw calls, it's time to recurse
        #for child in self.children:
         #   child.add_to_scene(self.last_action, all_verts, all_indicies, in_mats, in_collection, cur_static_offsets.copy(), cur_show_hide_commands.copy())

        #Reset our frame
        anim_utils.goto_frame(0)

        #Now that everything is parented, we add the keyframes in reverse order so everything is applied correctly
        for i, action in enumerate(reversed(self.actions)):

            if isinstance(action, draw_call) or isinstance(action, light) or isinstance(action, anim_level):
                #If this is a draw call or light, we don't need to do anything here. They were already added to the scene
                continue
        
            anim_empty = action.empty

            #Skip animations that just have their data propagated to their children
            if action.type == 'loc_keyframe' or action.type == 'rot_keyframe' or action.type == 'show_hide_series':
                continue

            #Apply the base static translation offset
            action.static_offsets.apply(anim_empty)

            #Apply show/hide commands. We do this here vs a dedicated empty because that can mess up manipulators sadly
            for cmd in action.show_hide_commands:
                    cmd.apply(anim_empty)
            
            if action.type == 'loc_table':
                
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

        self.obj_mode = "aircraft"  #aircraft, scenery, or cockpit

        #Base material
        self.alb_texture = ""
        self.nml_texture = ""
        self.lit_texture = ""
        self.mat_texture = ""
        self.blend_mode = "BLEND"
        self.blend_cutoff = 0.5
        self.cast_shadow = True
        self.imported_decal_commands = []
        self.layer_group = "objects"
        self.layer_group_offset = 0

        self.blend_glass = False
        self.brightness = -1
        self.particle_system = ""
        self.panel_texture_mode = "cockpit" #cockpit, cockpit_lit_only, or cockpit_region
        self.panel_texture_region = "0"

        #Draped material
        self.draped_alb_texture = ""
        self.draped_nml_tile_rat = 1.0
        self.draped_nml_texture = ""
        self.draped_lit_texture = ""
        self.imported_decal_commands_draped = []
        self.draped_layer_group = "objects"
        self.draped_layer_group_offset = -5

        #Thermal data. This just lets us store it between read and before to_collection
        self.thermal_texture = ""
        self.thermal_src_datarefs = []
        self.thermal_sources = []
        self.wiper_texture = ""
        self.wiper_params = []
        self.rain_scale = 1.0
        self.rain_friction = 1.0
        self.cockpit_regions = []

    def read(self, in_obj_path):

        log_utils.new_section(f"Read .obj {in_obj_path}")

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
        cur_in_draped_mat = False

        with open(in_obj_path, "r") as f:
            lines = f.readlines()
        
        for line in lines:

            line = line.strip()
            tokens = line.split()

            if len(tokens) == 0:
                continue

            # Defensive: check token count for each command before using tokens
            cmd = tokens[0]
            # Map of command to minimum required tokens (based on usage below)
            min_tokens = {
                'VT': 9,
                'IDX10': 11,
                'IDX': 2,
                'TRIS': 3,
                'PARTICLE_SYSTEM': 2,
                'BLEND_GLASS': 1,
                'GLOBAL_luminance': 2,
                'TEXTURE': 2,
                'TEXTURE_MAP': 3,
                'TEXTURE_NORMAL': 2,
                'TEXTURE_DRAPED': 2,
                'TEXTURE_DRAPED_NORMAL': 3,
                'TEXTURE_DRAPED_LIT': 2,
                'TEXTURE_LIT': 2,
                'GLOBAL_no_blend': 2,
                'GLOBAL_shadow_blend': 2,
                'ANIM_trans': 4, # 4 *minimum* tokens, but can be more
                'ANIM_rotate': 5, # 5 *minimum* tokens, but can be more
                'ANIM_keyframe_loop': 2,
                'ANIM_show': 4,
                'ANIM_hide': 4,
                'ANIM_rotate_begin': 5,
                'ANIM_rotate_key': 3,
                'ANIM_trans_begin': 2,
                'ANIM_trans_key': 5,
                'ATTR_LOD': 3,
                'LIGHT_NAMED': 5,
                'LIGHT_CUSTOM': 13, #13-14
                'LIGHT_SPILL_CUSTOM': 13, #13-14
                'LIGHT_PARAM': 6, # variable, but 6 is minimum
                'ATTR_hard': 2,
                'ATTR_hard_deck': 2,
                'ATTR_layer_group': 3,
                'ATTR_draped_layer_group': 3,
                'ATTR_cockpit_device': 5,
                'ATTR_cockpit_region': 2,
                'THERMAL_source': 3,
                'THERMAL_source2': 3,
                'WIPER_param': 5,
                'COCKPIT_REGION': 5,
                'RAIN_SCALE': 2,
                'RAIN_FRICTION': 2,
                'THERMAL_texture': 2,
                'WIPER_texture': 2,
                'WIPER_blend': 2,
            }
            
            # Only check if command is in our map
            if cmd in min_tokens and len(tokens) < min_tokens[cmd]:
                log_utils.warning(f"Not enough tokens for command '{cmd}'! Expected at least {min_tokens[cmd]}, got {len(tokens)}. Line: '{line}'")
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
                dc.state = cur_state.copy()  #Use the current state for this draw call
                dc.start_index = int(float(tokens[1]))
                dc.length = int(float(tokens[2]))
                dc.lod_start = cur_start_lod
                dc.lod_end = cur_end_lod
                if cur_manipulator.valid:
                    dc.manipulator = cur_manipulator.copy()  #Copy the current manipulator to the draw call

                #Reset the current manipulator for the next draw call
                cur_manipulator = manipulator()

                #Add the draw call to the list of draw calls. This is the current animation in the tree, or the list of static draw calls it there is no current animation
                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this draw call to the current animation tree
                    cur_anim_tree[-1].actions.append(dc)
                else:
                    self.draw_calls.append(dc)

            elif tokens[0] == "PARTICLE_SYSTEM":
                self.particle_system = tokens[1]

            elif tokens[0] == "BLEND_GLASS":
                self.blend_glass = True

            elif tokens[0] == "GLOBAL_luminance":
                #If the brightness ends in cd, remove the cd
                if tokens[1].endswith("cd"):
                    self.brightness = int(float(tokens[1][:-2]))
                else:
                    self.brightness = int(float(tokens[1]))

            elif tokens[0] == "TEXTURE" and len(tokens) >= 2:
                self.alb_texture = tokens[1]
                if self.draped_alb_texture == "":
                    self.draped_alb_texture = tokens[1]
                cur_in_draped_mat = False
            
            elif tokens[0] == "TEXTURE_MAP":
                if tokens[1].lower() == "normal":
                    self.nml_texture = tokens[2]
                elif tokens[1].lower() == "material_gloss":
                    self.mat_texture = tokens[2]
                cur_in_draped_mat = False

            elif tokens[0] == "TEXTURE_NORMAL":
                self.nml_texture = tokens[1]
                if self.draped_nml_texture == "":
                    self.draped_nml_texture = tokens[1]
                cur_in_draped_mat = False

            elif tokens[0] == "TEXTURE_DRAPED":
                self.draped_alb_texture = tokens[1]
                self.obj_mode = "scenery"
                cur_in_draped_mat = True

            elif tokens[0] == "TEXTURE_DRAPED_NORMAL":
                self.draped_nml_tile_rat = float(tokens[1])
                self.draped_nml_texture = tokens[2]
                cur_in_draped_mat = True

            elif tokens[0] == "TEXTURE_DRAPED_LIT":
                self.draped_lit_texture = tokens[1]
                cur_in_draped_mat = True

            elif tokens[0] == "TEXTURE_LIT":
                self.lit_texture = tokens[1]
                if self.draped_lit_texture == "":
                    self.draped_lit_texture = tokens[1]
                
            #Check for decals
            elif tokens[0].startswith("DECAL") or tokens[0].startswith("NORMAL_DECAL"):
                if cur_in_draped_mat:
                    self.imported_decal_commands_draped.append(line)
                else:
                    self.imported_decal_commands.append(line)

            elif tokens[0] == "GLOBAL_no_blend":
                self.blend_mode == "CLIP"
                self.blend_cutoff = float(tokens[1])
                cur_state.blend = False
                cur_state.blend_cutoff = self.blend_cutoff

            elif tokens[0] == "GLOBAL_shadow_blend":
                self.blend_mode == "SHADOW"
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
                    cur_anim_tree[-1].actions.append(new_anim)
                else:
                    self.anims.append(new_anim)

                #Append it to the current animation tree
                cur_anim_tree.append(new_anim)
            
            elif tokens[0] == "ANIM_trans":
                #If this command is missing the dataref, we assume it is a static translation
                if len(tokens) < 10:
                    #ANIM_trans <x1> <y1> <z1> <x2> <y2> <z2> <v1> <v2>
                    cur_table = anim_loc_table()

                    cur_static_translation = anim_loc_keyframe()
                    cur_static_translation.time = 0
                    cur_static_translation.loc = (float(tokens[1]) * trans_matrix[0], float(tokens[3]) * trans_matrix[1], float(tokens[2] * trans_matrix[2]))

                    cur_table.add_keyframe(0, cur_static_translation.loc)

                    cur_anim_tree[-1].actions.append(cur_table)

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
                    cur_rotate_transform = anim_rot_table_vector_transform()

                    cur_rotate_keyframe_do_x = float(tokens[1]) * trans_matrix[0]
                    cur_rotate_keyframe_do_y = float(tokens[3]) * trans_matrix[1]
                    cur_rotate_keyframe_do_z = float(tokens[2]) * trans_matrix[2]
                    cur_rotate_transform.rot_vector = mathutils.Vector((cur_rotate_keyframe_do_x, cur_rotate_keyframe_do_y, cur_rotate_keyframe_do_z))

                    cur_table = anim_rot_table()
                    
                    key1 = anim_rot_keyframe()
                    key1.time = 0
                    key1.rot = float(tokens[4])
                    
                    cur_table.add_keyframe(key1.time, key1.rot)
                    
                    cur_anim_tree[-1].actions.append(cur_rotate_transform)
                    cur_anim_tree[-1].actions.append(cur_table)

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
                if len(cur_anim_tree[-1].actions) > 0 and isinstance(cur_anim_tree[-1].actions[-1], anim_show_hide_series):
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
                if len(cur_anim_tree[-1].actions) > 0 and isinstance(cur_anim_tree[-1].actions[-1], anim_show_hide_series):
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

                new_light.type = "POINT"

                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this light to the current animation tree
                    cur_anim_tree[-1].actions.append(new_light)

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

                new_light.type = "POINT"

                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this light to the current animation tree
                    cur_anim_tree[-1].actions.append(new_light)

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

                new_light.type = "POINT" if float(tokens[12]) > 0.99 else "SPOT"

                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this light to the current animation tree
                    cur_anim_tree[-1].actions.append(new_light)

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
                    log_utils.warning(f"Unknown light type {new_light.name} in object {self.name}. Skipping light.")
                    continue

                #Make sure we have the right number of additional params
                if len(tokens) - 5 != len(additional_params_keys):
                    log_utils.warning(f"Light {new_light.name} in object {self.name} has {len(tokens) - 5} additional params, but expected {len(additional_params_keys)}. Skipping light.")
                    continue

                new_light.type = "POINT"

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
                        if float(tokens[i + 5]) < 0.99:
                            new_light.type = "SPOT"
                    elif param == 'INTENSITY' or param == 'SIZE':
                        light_size = tokens[i + 5]
                        if light_size.endswith('cd'):
                            new_light.is_photometric = True #What do we do with this? There's no setting in XP2B for this???
                            light_size = light_size[:-2] #Remove the 'cd' suffix
                            new_light.size = float(light_size)
                        else:
                            new_light.size = float(tokens[i + 5])
                    elif param == 'FREQ':
                        new_light.frequency = float(tokens[i + 5])
                    elif param == 'PHASE':
                        new_light.phase = float(tokens[i + 5])
                    elif param == 'INDEX':
                        new_light.index =int(float(tokens[i + 5]))

                    if (param == 'INTENSITY' or param == 'SIZE') and tokens[i + 5].endswith('cd'):
                        tokens[i + 5] = tokens[i + 5][:-2]  #Remove the 'cd' suffix
                    new_light.params += f"{tokens[i + 5]} "

                

                if len(cur_anim_tree) > 0:
                    #If we are in an animation tree, add this light to the current animation tree
                    cur_anim_tree[-1].actions.append(new_light)

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
                cur_state.blend_mode = "CLIP"
                if len(tokens) > 1:
                    cur_state.blend_cutoff = float(tokens[1])

            elif tokens[0] == "ATTR_shadow_blend ":
                cur_state.blend_mode = "SHADOW"
                if len(tokens) > 1:
                    cur_state.blend_cutoff = float(tokens[1])

            elif tokens[0] == "ATTR_blend":
                cur_state.blend_mode = "BLEND"
                cur_state.blend_cutoff = 0.5
    
            elif tokens[0] == "ATTR_hard":
                cur_state.surface_type = tokens[1]
                self.obj_mode = "scenery"

            elif tokens[0] == "ATTR_hard_deck":
                cur_state.surface_type = tokens[1]
                self.obj_mode = "scenery"

            elif tokens[0] == "ATTR_no_hard":
                cur_state.surface_type = "none"

            elif tokens[0] == "ATTR_layer_group":
                self.layer_group = tokens[1]
                self.layer_group_offset =int(float(tokens[2])) if len(tokens) > 2 else 0

            elif tokens[0] == "ATTR_draped_layer_group":
                self.draped_layer_group = tokens[1]
                self.draped_layer_group_offset = int(float(tokens[2])) if len(tokens) > 2 else 0

            elif tokens[0] == "ATTR_draw_enable":
                cur_state.draw = True

            elif tokens[0] == "ATTR_draw_disable":
                cur_state.draw = False

            elif tokens[0] == "ATTR_solid_camera":
                cur_state.hard_camera = True
                
            elif tokens[0] == "ATTR_no_solid_camera":
                cur_state.hard_camera = False
           
            elif tokens[0] == "ATTR_light_level":
                #ATTR_light_level <v1> <v2> <dataref> [<brightness>]
                cur_state.light_level_override = True
                cur_state.light_level_v1 = float(tokens[1])
                cur_state.light_level_v2 = float(tokens[2])
                if len(tokens) >= 4:
                    cur_state.light_level_dataref = tokens[3]
                if len(tokens) >= 5:
                    cur_state.light_level_photometric = True
                    if tokens[4].endswith('cd'):
                        cur_state.light_level_brightness = float(tokens[4][:-2])
                    else:
                        cur_state.light_level_brightness = float(tokens[4])
            
            elif tokens[0] == "ATTR_light_level_reset":
                cur_state.light_level_override = False
                cur_state.light_level_v1 = 0.0
                cur_state.light_level_v2 = 0.0
                cur_state.light_level_dataref = ""
                cur_state.light_level_photometric = False
                cur_state.light_level_brightness = 0.0

            elif tokens[0] == "ATTR_manip_wheel":
                cur_manipulator.wheel_delta = float(tokens[1]) if len(tokens) > 1 else 0

            elif tokens[0] == "ATTR_axis_detent_range":
                new_detent = manipulator_detent()
                new_detent.start = float(tokens[1])
                new_detent.end = float(tokens[2])
                new_detent.length = float(tokens[3])
                cur_manipulator.detents.append(new_detent)

            elif tokens[0] == "ATTR_manip_keyframe":
                #TODO: What does this even do? I don't understand docs nor see corresponding settings in X-Plane2Blender
                pass

            elif tokens[0] == "ATTR_cockpit_device":
                #ATTR_cockpit_device <name> <bus> <lighting channel> <auto_adjust>
                valid_names = ["GNS430_1", "GNS430_1", "GNS530_2", "GNS530_2", "CDU739_1", "CDU739_2", "G1000_MFD", "G1000_PFD1", "G1000_PFD2", "MCDU_1", "MCDU_2", \
                               "Primus_RMU_1", "Primus_RMU_2", "Primus_PFD_1", "Primus_PFD_2", "Primus_MFD_1", "Primus_MFD_2", "Primus_MFD_3"]
                
                if not tokens[1] in valid_names:
                    cur_state.cockpit_device = "Plugin Device"
                    cur_state.custom_cockpit_device = tokens[1]
                else:
                    cur_state.cockpit_device = tokens[1].upper()

                bus = int(float(tokens[2]))
                cur_state.cockpit_device_use_bus_1 = bus & 1 > 0
                cur_state.cockpit_device_use_bus_2 = bus & 2 > 0
                cur_state.cockpit_device_use_bus_3 = bus & 4 > 0
                cur_state.cockpit_device_use_bus_4 = bus & 8 > 0
                cur_state.cockpit_device_use_bus_5 = bus & 16 > 0
                cur_state.cockpit_device_use_bus_6 = bus & 32 > 0

                cur_state.cockpit_device_lighting_channel = int(float(tokens[3]))

            elif tokens[0] == "ATTR_cockpit_lit_only":
                self.panel_texture_mode = "cockpit_lit_only"

            elif tokens[0] == "ATTR_cockpit":
                cur_state.use_2d_panel = True

            elif tokens[0] == "ATTR_cockpit_region":
                self.panel_texture_mode = "cockpit_region"
                self.panel_texture_region = tokens[1]
                cur_state.panel_texture_region = int(float(tokens[1]))

            elif tokens[0] == "ATTR_no_cockpit":
                cur_state.cockpit_device = "NONE"
                cur_state.custom_cockpit_device = ""
                cur_state.cockpit_device_use_bus_1 = False
                cur_state.cockpit_device_use_bus_2 = False
                cur_state.cockpit_device_use_bus_3 = False
                cur_state.cockpit_device_use_bus_4 = False
                cur_state.cockpit_device_use_bus_5 = False
                cur_state.cockpit_device_use_bus_6 = False
                cur_state.cockpit_device_lighting_channel = 0

            elif tokens[0] == "ATTR_manip_device":
                #ATTR_manip_device <cursor> <device> <tooltip>
                cur_state.cockpit_device = "Plugin Device"
                cur_state.custom_cockpit_device = tokens[1]
                pass

            elif tokens[0].startswith("ATTR_manip"):
                cur_manipulator.valid = True
                cur_manipulator.params = tokens.copy()
                self.obj_mode = "cockpit"
                
            elif tokens[0] == "COCKPIT_REGION":
                region = cockpit_region()
                region.left = float(tokens[1])
                region.bottom = float(tokens[2])
                region.width = float(tokens[3]) - region.left
                region.height = float(tokens[4]) - region.bottom

            elif tokens[0] == "RAIN_SCALE":
                self.rain_scale = float(tokens[1])

            elif tokens[0] == "RAIN_FRICTION":
                self.rain_friction = float(tokens[1])

            elif tokens[0] == "THERMAL_texture":
                self.thermal_texture = tokens[1]

            elif tokens[0] == "WIPER_texture":
                self.wiper_texture = tokens[1]

            elif tokens[0] == "WIPER_blend":
                self.wiper_texture = tokens[1]

            elif tokens[0] == "THERMAL_source":
                new_source = thermal_source()
                new_source.dataref = tokens[1]
                new_source.toggle_dataref = tokens[2]
                self.thermal_sources.append(new_source)

            elif tokens[0] == "THERMAL_source2":
                new_source = thermal_source()
                new_source.temperature = float(tokens[1])
                new_source.toggle_dataref = tokens[2]
                self.thermal_sources.append(new_source)

            elif tokens[0] == "WIPER_param":
                new_wiper = wiper_param()
                new_wiper.dataref = tokens[1]
                new_wiper.start = float(tokens[2])
                new_wiper.end = float(tokens[3])
                new_wiper.width = float(tokens[4])

                self.wiper_params.append(new_wiper)
            
    def to_scene(self):
        log_utils.new_section(f"Creating .obj collection {self.name}")

        #Create a new collection for this object
        collection = bpy.data.collections.new(self.name)
        collection.name = self.name
        bpy.context.scene.collection.children.link(collection)

        #Set the collection settings
        collection.xplane.is_exportable_collection = True
        collection.xplane.layer.export_type = self.obj_mode
        collection.xplane.layer.texture = self.alb_texture
        collection.xplane.layer.texture_lit = self.lit_texture
        collection.xplane.layer.texture_normal = self.nml_texture
        collection.xplane.layer.texture_map_material_gloss = self.mat_texture
        collection.xplane.layer.texture_draped = self.draped_alb_texture
        collection.xplane.layer.texture_draped_normal = self.draped_nml_texture
        collection.xplane.layer.blend_glass = self.blend_glass
        collection.xplane.layer.normal_metalness = True
        if self.brightness > 0:
            collection.xplane.layer.luminance_override = True
            collection.xplane.layer.luminance = self.brightness
        collection.xplane.layer.cockpit_panel_mode = self.panel_texture_mode
        collection.xplane.layer.cockpit_regions = self.panel_texture_region
        collection.xplane.layer.particle_system_file = self.particle_system
        collection.xplane.layer.rain.rain_scale = self.rain_scale
        collection.xplane.layer.rain.thermal_texture = self.thermal_texture
        collection.xplane.layer.rain.wiper_texture = self.wiper_texture

        for i, src, in enumerate(self.thermal_sources):
            target = None
            if i == 0:
                collection.xplane.layer.rain.thermal_source_1_enabled = True
                target = collection.xplane.layer.rain.thermal_source_1
            elif i == 1:
                collection.xplane.layer.rain.thermal_source_2_enabled = True
                target = collection.xplane.layer.rain.thermal_source_2
            elif i == 2:
                collection.xplane.layer.rain.thermal_source_3_enabled = True
                target = collection.xplane.layer.rain.thermal_source_3
            elif i == 3:
                collection.xplane.layer.rain.thermal_source_4_enabled = True
                target = collection.xplane.layer.rain.thermal_source_4
            else:
                #Only 4 thermal sources are supported, so we just break out of the loop
                break

            if src.temperature != 0:
                target.defrost_time = str(src.temperature)
            else:
                target.defrost_time = src.dataref
            target.dataref_on_off = src.toggle_dataref

        for i, src, in enumerate(self.wiper_params):
            target = None
            if i == 0:
                collection.xplane.layer.rain.wiper_1_enabled = True
                target = collection.xplane.layer.rain.wiper_1
            elif i == 1:
                collection.xplane.layer.rain.wiper_2_enabled = True
                target = collection.xplane.layer.rain.wiper_2
            elif i == 2:
                collection.xplane.layer.rain.wiper_3_enabled = True
                target = collection.xplane.layer.rain.wiper_3
            elif i == 3:
                collection.xplane.layer.rain.wiper_4_enabled = True
                target = collection.xplane.layer.rain.wiper_4
            else:
                #Only 4 wipers are supported, so we just break out of the loop
                break

            target.dataref = src.dataref
            target.start = src.start
            target.end = src.end
            target.nominal_width = src.width
        
        for i, region in enumerate(self.cockpit_regions):
            target = None
            if i == 0:
                collection.xplane.layer.cockpit_regions = 1
                target = collection.xplane.layer.cockpit_region[0]
            elif i == 1:
                collection.xplane.layer.cockpit_regions = 2
                target = collection.xplane.layer.cockpit_region[1]
            elif i == 2:
                collection.xplane.layer.cockpit_regions = 3
                target = collection.xplane.layer.cockpit_region[2]
            elif i == 3:
                collection.xplane.layer.cockpit_regions = 4
                target = collection.xplane.layer.cockpit_region[3]
            else:
                #Only 4 cockpit regions are supported, so we just break out of the loop
                break

            target.left = region.left
            target.top = region.bottom
            target.width = region.width
            target.height = region.height

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
        xp_mat.blend_mode = self.blend_mode
        xp_mat.blend_cutoff = self.blend_cutoff
        xp_mat.cast_shadow = self.cast_shadow
        mat.name = self.name

        decal_alb_index = 0
        decal_nml_index = 2

        material_config.update_settings(mat)

        for decal in self.imported_decal_commands:
            if decal.startswith("NORMAL"):
                if decal_nml_index > 3:
                    log_utils.warning("Too many normal decals! X-Plane only supports 2 normal decals per material.")
                    break
                decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_nml_index])
                decal_nml_index += 1
            else:
                if decal_alb_index > 2:
                    log_utils.warning("Too many albedo decals! X-Plane only supports 2 decals per material.")
                    break
                decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_alb_index])
                decal_alb_index += 1

        all_mats.append(mat)

        #Create the draped material if it exists
        if self.draped_alb_texture != "":
            draped_mat = mat.copy()
            draped_mat.name = self.name + "_draped"
            draped_mat.use_nodes = True
            xp_draped_mat = draped_mat.xp_materials
            xp_draped_mat.alb_texture = self.draped_alb_texture
            xp_draped_mat.normal_texture = self.draped_nml_texture
            xp_draped_mat.lit_texture = self.draped_lit_texture
            xp_draped_mat.blend_mode = self.blend_mode
            xp_draped_mat.blend_cutoff = self.blend_cutoff
            xp_draped_mat.cast_shadow = self.cast_shadow
            xp_draped_mat.draped = True
            xp_draped_mat.draped_nml_tile_rat = self.draped_nml_tile_rat
            draped_mat.name = self.name + "_draped"

            decal_alb_index = 0
            decal_nml_index = 2

            for decal in self.imported_decal_commands_draped:
                if decal.startswith("NORMAL"):
                    if decal_nml_index > 3:
                        log_utils.warning("Too many normal decals! X-Plane only supports 2 normal decals per material.")
                        break
                    decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_nml_index])
                    decal_nml_index += 1
                else:
                    if decal_alb_index > 2:
                        log_utils.warning("Too many albedo decals! X-Plane only supports 2 decals per material.")
                        break
                    decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_alb_index])
                    decal_alb_index += 1

            all_mats.append(draped_mat)

        #In X-Plane2Blender, the LOD system is done via buckets. There are 4 buckets, with their start/end distances set at a collection level
        #In X-Plane however, the LOD sysytem is done via ranges on a potentially per-tris basis, so we could potentially
        #have more LODs than buckets! We... can't fix this. So what we'll do is just get a dictionary of all the LODs, then assign draw calls to the appropriate bucket
        #In X-Plane, there are two LOD methods, additive and selective.
        #In Additive mode, all LODs that are in range are drawn
        #In Selective mode, a single LOD is drawn, based on the distance being within the min and max.
        #We determine additive by checking if any LODs *don't* start with 0, in which case we assume it's selective
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
                log_utils.warning(f"Too many LOD buckets for object {self.name}. Skipping LOD {lod_range} for draw call {dc.start_index}-{dc.length}. Object will be added to best guess bucket. Double check this choice!")

        obj_does_use_lods = True
        if len(all_lod_buckets) == 1:
            if all_lod_buckets[0] == (0, 0):
                #If we only have one bucket, and it's the default bucket, we don't need to do anything
                all_lod_buckets = []
                obj_does_use_lods = False

        #Determine additive vs selective
        for bucket in all_lod_buckets:
            if bucket[0] != 0:
                is_selective_lod = True
                break

        all_lod_buckets.sort()

        def put_draw_call_in_bucket(dc, all_lod_buckets, is_selective_lod):
            if all_lod_buckets == []:
                #If there are no LOD buckets, we don't need to do anything
                dc.lod_bucket = -1
                return
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
        
        #Lastly, we'll go through and update the materials
        for mat in all_mats:
            material_config.update_settings(mat)
