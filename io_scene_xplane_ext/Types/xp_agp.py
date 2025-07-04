#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      6/5/2025
#Module:    XP_AGP
#Purpose:   Provide classes that abstracts the X-Plane AGP format

from ..Helpers import agp_utils
from ..Helpers import file_utils
from ..Helpers import decal_utils
from ..Helpers import misc_utils
from ..Helpers import log_utils
from .. import material_config

from ..Helpers.misc_utils import ftos

import os
import math
import mathutils
import bpy
import bmesh

class crop_polygon:
    """
    Class to abstract the crop_polygon in X-Plane's AGP format
    """

    def __init__(self):
        self.perimeter = [] #List of mathutils.Vector. Stored in world coordinates
        self.valid = True

    def from_obj(self, obj):
        #Get the vertices in world coordinates
        self.perimeter = agp_utils.get_perimeter_from_mesh(obj)

        if len(self.perimeter) < 3:
            log_utils.warning(f"CROP_POLY must have at least three coordinates! {obj.name}")
            self.valid = False
            return

    def to_obj(self):
        if len(self.perimeter) == 0:
            return
        #Set the vertices in world coordinates
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, 0.1)
        new_obj.xp_agp.exportable = True
        new_obj.xp_agp.type = 'CROP_POLY'

        return new_obj

    def to_command(self, transform: agp_utils.agp_transform):
        if not self.valid:
            return ""

        cmd = ""

        #Now we need to copy our perimeter and transform it
        transformed_perimeter = []
        for vert in self.perimeter:
            #Transform the vertex using the agp_transform
            pixel_x, pixel_y = agp_utils.to_pixel_coords(vert.x, vert.y, transform)
            transformed_perimeter.append(mathutils.Vector((pixel_x, pixel_y, 0)))

        #If the last point is the same as the first, remove it
        if len(transformed_perimeter) > 0 and transformed_perimeter[-1] == transformed_perimeter[0]:
            transformed_perimeter.pop()

        cmd = f"CROP_POLY "

        for vert in transformed_perimeter:
            cmd += f"{ftos(vert.x, 4)} {ftos(vert.y, 4)} "

        if len(transformed_perimeter) < 3:
            log_utils.warning("CROP_POLY must have at least 3 vertices.")
            self.perimeter = []
            return
        
        return cmd

    def from_command(self, in_command, transform: agp_utils.agp_transform, in_x_mult=1.0, in_y_mult=1.0):
        tokens = in_command.strip().split()

        # The rest are perimeter coordinates (x, y pairs)
        coords = tokens[1:]
        if len(coords) % 2 != 0:
            log_utils.warning(f"Invalid number of coordinates in CROP_POLY command: {in_command}")
            self.perimeter = []
            return

        self.perimeter = []
        for i in range(0, len(coords), 2):
            pixel_x = float(coords[i]) * in_x_mult
            pixel_y = float(coords[i+1]) * in_y_mult
            blender_x, blender_y = agp_utils.to_blender_coords(pixel_x, pixel_y, transform)
            self.perimeter.append(mathutils.Vector((blender_x, blender_y, 0)))

        #Re add the last point to close the polygon
        if len(self.perimeter) > 0:
            self.perimeter.append(self.perimeter[0])

class facade:
    """
    Class to abstract the placement of a facade in X-Plane's AGP format
    """

    def __init__(self):
        self.resource = ""
        self.height = 10.0
        self.perimeter = [] #List of mathutils.Vector. Stored in world coordinates
        self.valid = True

    def from_obj(self, obj):
        self.resource = obj.xp_agp.facade_resource
        self.height = obj.xp_agp.facade_height

        #Get the vertices in world coordinates
        self.perimeter = agp_utils.get_perimeter_from_mesh(obj)

        if len(self.perimeter) < 2:
            log_utils.warning(f"FAC must have at least two coordinates! {obj.name}")
            self.valid = False
            return

    def to_obj(self):
        if not self.valid:
            return

        #Set the vertices in world coordinates
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, self.height)

        new_obj.xp_agp.facade_resource = self.resource
        new_obj.xp_agp.facade_height = self.height
        new_obj.xp_agp.exportable = True
        new_obj.xp_agp.type = 'FACADE'

        return new_obj

    def to_command(self, fac_resource_list, transform: agp_utils.agp_transform):
        if not self.valid:
            return ""

        cmd = ""

        #Find out resource index
        resource_index = fac_resource_list.index(self.resource)

        #Now we need to copy our perimeter and transform it
        transformed_perimeter = []
        for vert in self.perimeter:
            #Transform the vertex using the agp_transform
            pixel_x, pixel_y = agp_utils.to_pixel_coords(vert.x, vert.y, transform)
            transformed_perimeter.append(mathutils.Vector((pixel_x, pixel_y, 0)))

        cmd = f"FAC {int(resource_index)} {ftos(self.height, 2)} "

        for vert in transformed_perimeter:
            cmd += f"{ftos(vert.x, 4)} {ftos(vert.y, 4)} "

        return cmd

    def from_command(self, in_command, fac_resource_list, transform: agp_utils.agp_transform, in_x_mult=1.0, in_y_mult=1.0):
        """
        Parse a FAC command and set the facade's properties accordingly.
        Args:
            in_command (str): The FAC command string (e.g. 'FAC 0 10.0 x1 y1 x2 y2 ...').
            fac_resource_list (list): List of resource names, indexed by resource index.
            transform (agp_utils.agp_transform): Transform to convert pixel coords to Blender coords.
        """
        tokens = in_command.strip().split()
        if len(tokens) < 4 or tokens[0] != 'FAC':
            log_utils.warning(f"Invalid FAC command: {in_command}")
            self.valid = False
            return

        resource_index = int(tokens[1])
        self.resource = fac_resource_list[resource_index]
        self.height = float(tokens[2])

        # The rest are perimeter coordinates (x, y pairs)
        coords = tokens[3:]
        if len(coords) % 2 != 0:
            log_utils.warning(f"Invalid number of coordinates in FAC command: {in_command}")
            self.valid = False
            return

        self.perimeter = []
        for i in range(0, len(coords), 2):
            pixel_x = float(coords[i]) * in_x_mult
            pixel_y = float(coords[i+1]) * in_y_mult
            blender_x, blender_y = agp_utils.to_blender_coords(pixel_x, pixel_y, transform)
            self.perimeter.append(mathutils.Vector((blender_x, blender_y, 0)))

class tree_line:
    """
    Class to abstract the placement of a tree line in X-Plane's AGP format
    """

    def __init__(self):
        self.layer = 0
        self.perimeter = [] #List of mathutils.Vector. Stored in world coordinates
        self.valid = True

    def from_obj(self, obj):
        self.layer = obj.xp_agp.tree_layer

        #Get the vertices in world coordinates
        self.perimeter = agp_utils.get_perimeter_from_mesh(obj)

        if len(self.perimeter) < 2:
            log_utils.warning(f"Tree Line must have at least two coordinates! {obj.name}")
            self.valid = False
            return

    def to_obj(self):
        if not self.valid:
            return

        #Set the vertices in world coordinates
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, 1)

        new_obj.xp_agp.tree_layer = self.layer
        new_obj.xp_agp.exportable = True
        new_obj.xp_agp.type = 'TREE_LINE'

        return new_obj

    def to_commands(self, transform: agp_utils.agp_transform):
        if not self.valid:
            return []

        #TREE_LINE commands in .agps are only a start and end.
        # In here we allow more but will auto split them into multiple commands
        cmds = []
        cur_cmd = ""

        transformed_perimeter = []
        for vert in self.perimeter:
            #Transform the vertex using the agp_transform
            pixel_x, pixel_y = agp_utils.to_pixel_coords(vert.x, vert.y, transform)
            transformed_perimeter.append(mathutils.Vector((pixel_x, pixel_y, 0)))

        for i in range(0, len(transformed_perimeter) - 1):
            cur_cmd = f"TREE_LINE {ftos(transformed_perimeter[i].x, 4)} {ftos(transformed_perimeter[i].y, 4)} {ftos(transformed_perimeter[i+1].x, 4)} {ftos(transformed_perimeter[i+1].y, 4)} {self.layer}"
            cmds.append(cur_cmd)

        return cmds

    def from_command(self, in_command, transform: agp_utils.agp_transform, in_x_mult=1.0, in_y_mult=1.0):
        """
        Parse a TREE_LINE command and set the tree line's properties accordingly.
        Args:
            in_command (str): The FAC command string (e.g. 'FAC 0 10.0 x1 y1 x2 y2 ...').
            transform (agp_utils.agp_transform): Transform to convert pixel coords to Blender coords.
        """

        tokens = in_command.strip().split()
        if len(tokens) < 6:
            log_utils.warning(f"Invalid Tree Line command: {in_command}")
            self.valid = False
            return

        start_x = float(tokens[1]) * in_x_mult
        start_y = float(tokens[2]) * in_y_mult
        end_x = float(tokens[3]) * in_x_mult
        end_y = float(tokens[4]) * in_y_mult
        self.layer = int(tokens[5])

        temp_perimeter = []
        temp_perimeter.append(mathutils.Vector((start_x, start_y, 0)))
        temp_perimeter.append(mathutils.Vector((end_x, end_y, 0)))

        self.perimeter = []
        for vert in temp_perimeter:
            blender_x, blender_y = agp_utils.to_blender_coords(vert.x, vert.y, transform)
            self.perimeter.append(mathutils.Vector((blender_x, blender_y, 0)))

class tree:
    """
    Class to abstract an individual tree in X-Plane's AGP format
    """

    def __init__(self):
        self.layer = 0
        self.x = 0.0
        self.y = 0.0
        self.width = 10
        self.height = 10
        self.valid = True

    def from_obj(self, obj):
        #Make sure this is an empty
        if obj.type != 'EMPTY':
            log_utils.warning(f"Tree must be an empty! {obj.name}")
            self.valid = False
            return
        
        parent_scale = mathutils.Vector((1, 1, 1))
        if obj.parent is not None:
            parent_scale = obj.parent.scale

        #We'll extract the width and height from the empty
        #First we'll get the arrow length. Then we'll multiply that by 2, then the avg x/y scale and z scale for width/height, respectively
        self.width = obj.empty_display_size * 2 * ((obj.scale.x + obj.scale.y) / 2)
        self.height = obj.empty_display_size * 2 * obj.scale.z

        self.x = obj.location.x * parent_scale.x
        self.y = obj.location.y * parent_scale.y

        self.layer = obj.xp_agp.tree_layer

    def to_obj(self):
        #Create a new empty and set it's properties
        new_empty = bpy.data.objects.new("Tree", None)
        new_empty.empty_display_size = 1

        new_empty.scale.x = self.width / (2 * new_empty.empty_display_size)
        new_empty.scale.y = self.width / (2 * new_empty.empty_display_size)
        new_empty.scale.z = self.height / (2 * new_empty.empty_display_size)

        new_empty.location.x = self.x
        new_empty.location.y = self.y

        new_empty.xp_agp.exportable = True
        new_empty.xp_agp.type = 'TREE'
        new_empty.xp_agp.tree_layer = self.layer
        
        return new_empty

    def to_command(self, transform: agp_utils.agp_transform):
        if not self.valid:
            return ""

        cmd = ""

        x_pixel, y_pixel = agp_utils.to_pixel_coords(self.x, self.y, transform)

        cmd = f"TREE {ftos(x_pixel, 4)} {ftos(y_pixel, 4)} {ftos(self.height, 2)} {ftos(self.width, 2)} {self.layer}"

        return cmd

    def from_command(self, in_command, transform: agp_utils.agp_transform, in_x_mult=1.0, in_y_mult=1.0):
        tokens = in_command.split()

        x_pixel = float(tokens[1]) * in_x_mult
        y_pixel = float(tokens[2]) * in_y_mult
        self.height = float(tokens[3])
        self.width = float(tokens[4])
        self.layer = int(tokens[5])

        #Convert the pixel coords to Blender coords
        self.x, self.y = agp_utils.to_blender_coords(x_pixel, y_pixel, transform)

class attached_obj:
    """
    Class to abstract an individual tree in X-Plane's AGP format
    """

    def __init__(self):
        self.resource = ""
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.heading = 0.0
        self.draped = False
        self.show_low = 0
        self.show_high = 0
        self.valid = True

    def from_obj(self, obj):

        parent_scale = mathutils.Vector((1, 1, 1))
        if obj.parent is not None:
            parent_scale = obj.parent.scale

        self.resource = obj.xp_agp.attached_obj_resource
        self.draped = obj.xp_agp.attached_obj_draped

        self.x = obj.location.x * parent_scale.x
        self.y = obj.location.y * parent_scale.y
        self.z = obj.location.z * parent_scale.z
        self.heading = misc_utils.resolve_heading(math.degrees(obj.rotation_euler.z) * -1)

        self.show_low = obj.xp_agp.attached_obj_show_between_low
        self.show_high = obj.xp_agp.attached_obj_show_between_high

    def to_obj(self):
        if not self.valid:
            return None

        #Create a new empty and set it's properties
        new_empty = bpy.data.objects.new("Attached Obj", None)

        new_empty.xp_agp.attached_obj_resource = self.resource
        new_empty.xp_agp.attached_obj_draped = self.draped

        new_empty.xp_agp.attached_obj_show_between_low = self.show_low
        new_empty.xp_agp.attached_obj_show_between_high = self.show_high

        new_empty.xp_agp.exportable = True
        new_empty.xp_agp.type = 'ATTACHED_OBJ'

        new_empty.location.x = self.x
        new_empty.location.y = self.y
        new_empty.location.z = self.z
        new_empty.rotation_euler.z = math.radians(misc_utils.resolve_heading(self.heading * -1))

        return new_empty

    def to_command(self, obj_resource_list, transform: agp_utils.agp_transform):
        cmd = ""

        x_pixel, y_pixel = agp_utils.to_pixel_coords(self.x, self.y, transform)

        obj_index = obj_resource_list.index(self.resource)

        if not self.draped:
            cmd = f"OBJ_DELTA {ftos(x_pixel, 4)} {ftos(y_pixel, 4)} {ftos(self.heading, 4)} {ftos(self.z, 4)} {obj_index} {self.show_low} {self.show_high}"
        else:
            cmd = f"OBJ_DRAPED {ftos(x_pixel, 4)} {ftos(y_pixel, 4)} {ftos(self.heading, 4)} {obj_index} {self.show_low} {self.show_high}"

        return cmd

    def from_command(self, in_command, obj_resource_list, transform: agp_utils.agp_transform, in_x_mult=1.0, in_y_mult=1.0):
        """
        Parse an OBJ_DELTA or OBJ_DRAPED command and set the attached_obj's properties accordingly.
        Args:
            in_command (str): The OBJ_DELTA or OBJ_DRAPED command string.
            obj_resource_list (list): List of resource names, indexed by resource index.
            transform (agp_utils.agp_transform): Transform to convert pixel coords to Blender coords.
        """
        tokens = in_command.strip().split()
        if not tokens:
            log_utils.warning(f"Empty command: {in_command}")
            self.valid = False
            return
        if tokens[0] == 'OBJ_DELTA':
            # OBJ_DELTA x_pixel y_pixel heading z obj_index show_low show_high
            if len(tokens) < 6:
                log_utils.warning(f"Invalid OBJ_DELTA command: {in_command}")
                self.valid = False
                return
            x_pixel = float(tokens[1]) * in_x_mult
            y_pixel = float(tokens[2]) * in_y_mult
            self.heading = float(tokens[3])
            self.z = float(tokens[4])
            obj_index = int(tokens[5])
            if len(tokens) >= 8:
                self.show_low = int(tokens[6])
                self.show_high = int(tokens[7])
            self.draped = False
        elif tokens[0] == 'OBJ_DRAPED':
            if len(tokens) < 5:
                log_utils.warning(f"Invalid OBJ_DRAPED command: {in_command}")
                self.valid = False
                return
            x_pixel = float(tokens[1]) * in_x_mult
            y_pixel = float(tokens[2]) * in_y_mult
            self.heading = float(tokens[3])
            obj_index = int(tokens[4])
            if len(tokens) >= 7:
                self.show_low = int(tokens[5])
                self.show_high = int(tokens[6])
            self.z = 0.0
            self.draped = True
        elif tokens[0] == 'OBJ_GRADED' or tokens[0] == 'OBJ_SCRAPER':
            if len(tokens) < 5:
                log_utils.warning(f"Invalid OBJ_GRADED command: {in_command}")
                self.valid = False
                return
            x_pixel = float(tokens[1]) * in_x_mult
            y_pixel = float(tokens[2]) * in_y_mult
            self.heading = float(tokens[3])
            obj_index = int(tokens[4])
            if len(tokens) >= 7:
                self.show_low = int(tokens[5])
                self.show_high = int(tokens[6])
            self.z = 0.0
            self.draped = False
        else:
            log_utils.warning(f"Unknown command type for attached_obj: {tokens[0]}")
            self.valid = False
            return

        self.resource = obj_resource_list[obj_index]
        self.x, self.y = agp_utils.to_blender_coords(x_pixel, y_pixel, transform)

class auto_split_obj:
    """
    Class to represent an object that is auto-split off material and has it's parts added to the obj
    """

    def __init__(self):
        self.resources = []
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.heading = 0.0
        self.draped = False
        self.show_low = 0
        self.show_high = 0

    def export(self, obj, agp_name):
        """
        Automatically splits the object by material, exports all the parts, and configures the settings
        """

        parent_scale = mathutils.Vector((1, 1, 1))
        if obj.parent is not None:
            parent_scale = obj.parent.scale

        self.x = obj.location.x * parent_scale.x
        self.y = obj.location.y * parent_scale.y
        self.z = obj.location.z * parent_scale.z
        self.draped = False
        self.show_low = 0
        self.show_high = 0

        mat_name_to_collection = {}  # Maps material names to collections
        all_objs = []

        try:
            #Duplicate and split all the objects by material
            for child in obj.children:
                all_objs.extend(agp_utils.recursively_split_objects(child))

            all_objs_have_mats = True

            #Get a list of all materials
            all_mats = []
            for split_obj in all_objs:
                if split_obj.type != 'MESH':
                    #Non-mesh objects just get dumped into the first collection
                    continue
                if len(split_obj.data.materials) > 0:
                    all_mats.append(split_obj.active_material.name)
                else:
                    all_objs_have_mats = False
                    log_utils.warning(f"Object {split_obj.name} has no materials assigned. X-Plane2Blender would throw an error on export!")
            all_mats = list(set(all_mats))  # Dedupe
            #Go through all our objects and check if we have any lights. If so, we'll add a lights collection
            for split_obj in all_objs:
                if split_obj.type != 'MESH':    #Technically this should only be lights. But to be safe we'll just say "not mesh"
                    #Add a collection for lights
                    if "Lights" not in all_mats:
                        all_mats.append("Lights")
                    break

            #Now we need to check the parents for materials
            objects_with_no_mats = []
            for root_obj in obj.children:
                cur_obj = root_obj
                while cur_obj != None:
                    if cur_obj.type == 'MESH':
                        if len(cur_obj.data.materials) == 0:
                            #Save this object name and only log it once
                            objects_with_no_mats.append(cur_obj.name)
                            if not cur_obj.name in objects_with_no_mats:
                                log_utils.warning(f"Object {cur_obj.name} has no materials assigned. X-Plane2Blender would throw an error on export!")

                            all_objs_have_mats = False
                    cur_obj = cur_obj.parent
            
            if not all_objs_have_mats:
                raise Exception(f"Some objects have no materials assigned. X-Plane2Blender would throw an error on export! Skipping export of autosplit object {obj.name}")

            self.resoures = []
            for mat in all_mats:
                #Create a new collection for this material
                obj_name = ""
                if obj.xp_agp.autosplit_obj_name != "":
                    obj_name = agp_name + "_PT_" + obj.xp_agp.autosplit_obj_name + "_" + mat + ".obj"
                else:
                    obj_name = agp_name + "_PT_" + obj.name + "_" + mat + ".obj"
                obj_name = obj_name.replace(" ", "_")  # Replace spaces with underscores
                mat_collection = bpy.data.collections.new(obj_name)
                mat_collection.xplane.layer.name = obj_name
                self.resources.append(obj_name)
                mat_collection.xplane.is_exportable_collection = True
                mat_collection.xplane.layer.export_type = 'scenery'
                bpy.context.scene.collection.children.link(mat_collection)
                mat_name_to_collection[mat] = mat_collection

                #Set the LODs
                mat_collection.xplane.layer.lods = str(obj.xp_agp.autosplit_lod_count)
                mat_collection.xplane.layer.lod[0].near =   int(obj.xp_agp.autosplit_lod_1_min)
                mat_collection.xplane.layer.lod[0].far =    int(obj.xp_agp.autosplit_lod_1_max)
                mat_collection.xplane.layer.lod[1].near =   int(obj.xp_agp.autosplit_lod_2_min)
                mat_collection.xplane.layer.lod[1].far =    int(obj.xp_agp.autosplit_lod_2_max)
                mat_collection.xplane.layer.lod[2].near =   int(obj.xp_agp.autosplit_lod_3_min)
                mat_collection.xplane.layer.lod[2].far =    int(obj.xp_agp.autosplit_lod_3_max)
                mat_collection.xplane.layer.lod[3].near =   int(obj.xp_agp.autosplit_lod_4_min)
                mat_collection.xplane.layer.lod[3].far =    int(obj.xp_agp.autosplit_lod_4_max)

            #Now we need to move our new objects into the correct collections
            for split_obj in all_objs:
                if split_obj.type != 'MESH':
                    #Non-mesh objects go into "Light"
                    target_collection = mat_name_to_collection["Lights"]
                    target_collection.objects.link(split_obj)
                    continue

                #Find the material for this object
                obj_material = split_obj.data.materials[0]

                if obj_material is not None:
                    #Find the collection for this material
                    target_col = mat_name_to_collection[obj_material.name]
                    target_col.objects.link(split_obj)

            #Now we need to configure the settings for each collection
            for col in mat_name_to_collection.values():
                material_config.update_xplane_collection_settings(col)

            #Now we need to disable export on all other objects, export ours, then reenable ours
            original_collection_export_states = {}

            for col in bpy.data.collections:
                # Store the original export state
                original_collection_export_states[col.name] = col.xplane.is_exportable_collection

                col.xplane.is_exportable_collection = False

            for col in mat_name_to_collection.values():
                col.xplane.is_exportable_collection = True

            #Finally, we'll move the origin object to 0 0 0, with 0 heading, and export. Then we'll restore it's loc/rot
            obj_original_location = obj.location.copy()
            obj_original_rotation = obj.rotation_euler.copy()
            obj.location = mathutils.Vector((0, 0, 0))
            obj.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')

            bpy.ops.scene.export_to_relative_dir()

            obj.location = obj_original_location
            obj.rotation_euler = obj_original_rotation

            #Restore the original export states
            for col in bpy.data.collections:
                col.xplane.is_exportable_collection = original_collection_export_states[col.name]

            #Now we need to extract any errors for the XP2B log. So we will get the text file, iterate over every line, and log it as a warning. File is xplane2blender.log in text editor
            xp2b_log = bpy.data.texts.get("xplane2blender.log")
            if xp2b_log is not None:
                for line in xp2b_log.lines:
                    if line.body.strip():
                        log_utils.error(f"X-Plane2Blender Error exporting object {obj.name}: {line.body.strip()}")
        except Exception as e:
            log_utils.error(f"Error exporting auto-split object {obj.name}: {e}")
            good = False

        #We are now done with exporting, so we can remove the new objects and new collections
        try:
            for col in mat_name_to_collection.values():
                bpy.data.collections.remove(col, do_unlink=True)
        except Exception as e:
            log_utils.error(f"Error removing auto-split collections: {e}")

        #Now we can remove the duplicate objects
        try:
            for split_obj in all_objs:
                bpy.data.objects.remove(split_obj, do_unlink=True)
        except Exception as e:
            log_utils.error(f"Error removing duplicate objects: {e}")

    def to_commands(self, obj_resource_list, transform: agp_utils.agp_transform):
        cmds = []

        x_pixel, y_pixel = agp_utils.to_pixel_coords(self.x, self.y, transform)

        for resource in self.resources:
            obj_index = obj_resource_list.index(resource)
            cmd = f"OBJ_DELTA {ftos(x_pixel, 4)} {ftos(y_pixel, 4)} {ftos(self.heading, 4)} {ftos(self.z, 4)} {obj_index} {self.show_low} {self.show_high}"
            cmds.append(cmd)

        return cmds

class tile:
    def __init__(self):
        self.left_uv = 0.0
        self.right_uv = 1.0
        self.top_uv = 0.0
        self.bottom_uv = 1.0
        self.anchor_x_uv = 0.5
        self.anchor_y_uv = 0.5
        self.transform = agp_utils.agp_transform()
        self.rotation_n = 0
        self.material = None

        #Annotations (aka attached stuff)
        self.crop_poly = None
        self.facades = []   #List of facade objects
        self.tree_lines = []    #List of tree_line objects
        self.trees = []   #List of tree objects
        self.attached_objs = []   #List of attached_obj objects
        self.auto_split_objs = []   #List of auto_split_obj objects

    def from_obj(self, in_obj, agp_name):
        self.left_uv, self.bottom_uv, self.right_uv, self.top_uv, self.transform = agp_utils.get_tile_bounds_and_transform(in_obj)

        #Count of CCW rotations
        cur_rot = misc_utils.resolve_heading(math.degrees(in_obj.rotation_euler.z))

        if abs(cur_rot) < 1:
            self.rotation_n = 0
        elif abs(cur_rot - 90) < 1:
            self.rotation_n = 3
        elif abs(cur_rot - 180) < 1:
            self.rotation_n = 2
        elif abs(cur_rot - 270) < 1:
            self.rotation_n = 1
        
        #Now that we have the transform, we can get the child data
        for obj in in_obj.children:
            if not obj.xp_agp.exportable:
                continue

            if obj.xp_agp.type == 'ATTACHED_OBJ':
                new_obj = attached_obj()
                new_obj.from_obj(obj)
                self.attached_objs.append(new_obj)

            elif obj.xp_agp.type == 'AUTO_SPLIT_OBJ':
                new_obj = auto_split_obj()
                new_obj.export(obj, agp_name)
                self.auto_split_objs.append(new_obj)

            elif obj.xp_agp.type == 'FACADE':
                new_fac = facade()
                new_fac.from_obj(obj)
                self.facades.append(new_fac)

            elif obj.xp_agp.type == 'TREE':
                new_tree = tree()
                new_tree.from_obj(obj)
                self.trees.append(new_tree)

            elif obj.xp_agp.type == 'TREE_LINE':
                new_tree_line = tree_line()
                new_tree_line.from_obj(obj)
                self.tree_lines.append(new_tree_line)

            elif obj.xp_agp.type == 'CROP_POLY':
                new_crop_poly = crop_polygon()
                new_crop_poly.from_obj(obj)
                self.crop_poly = new_crop_poly

    def to_obj(self, target_collection, in_material):
        new_objs = []
        if self.crop_poly is not None:
            new_obj = self.crop_poly.to_obj()
            if new_obj is not None:
                new_objs.append(new_obj)

        for obj in self.attached_objs:
            new_obj = obj.to_obj()
            if new_obj is not None:
                new_objs.append(new_obj)

        for obj in self.facades:
            new_obj = obj.to_obj()
            if new_obj is not None:
                new_objs.append(new_obj)

        for obj in self.trees:
            new_obj = obj.to_obj()
            if new_obj is not None:
                new_objs.append(new_obj)

        for obj in self.tree_lines:
            new_obj = obj.to_obj()
            if new_obj is not None:
                new_objs.append(new_obj)

        print(target_collection.name)

        #Create our tile object
        new_tile_obj = agp_utils.create_tile_obj(self.left_uv, self.bottom_uv, self.right_uv, self.top_uv, self.transform)
        new_tile_obj.data.materials.append(in_material)
        new_tile_obj.xp_agp.exportable = True
        new_tile_obj.xp_agp.type = 'BASE_TILE'
        target_collection.objects.link(new_tile_obj)

        #Link the new objects to the tile object
        for new_obj in new_objs:
            #Link to the target collection
            target_collection.objects.link(new_obj)

            new_obj.parent = new_tile_obj

        #Rotate the tile object based on the rotation_n
        if self.rotation_n == 1:
            new_tile_obj.rotation_euler.z = math.radians(270)
        elif self.rotation_n == 2:
            new_tile_obj.rotation_euler.z = math.radians(180)
        elif self.rotation_n == 3:
            new_tile_obj.rotation_euler.z = math.radians(90)
        else:
            new_tile_obj.rotation_euler.z = 0.0

    def from_commands(self, commands, in_transfom, in_x_mult, in_y_mult, fac_resource_list, obj_resource_list):
        #Tiles have *many* commands, their TILE, their ANCHOR_PT, and all annotations.
        #So to handle all these we'll just loop through and set properties as we encounter them

        #Because anchors are used for transforms, we will read all lines and get the anchor point first
        for cmd in commands:
            tokens = cmd.strip().split()
            if not tokens:
                continue
            if tokens[0] == 'ANCHOR_PT':
                self.transform.anchor_x = float(tokens[1]) * in_x_mult
                self.transform.anchor_y = float(tokens[2]) * in_y_mult

        for cmd in commands:
            tokens = cmd.strip().split()
            if not tokens:
                continue

            if tokens[0] == 'TILE':
                self.left_uv = float(tokens[1]) * in_x_mult
                self.bottom_uv = float(tokens[2]) * in_y_mult
                self.right_uv = float(tokens[3]) * in_x_mult
                self.top_uv = float(tokens[4]) * in_y_mult
            elif tokens[0] == 'ROTATION':
                self.rotation_n = int(float(tokens[1]))
            elif tokens[0] == 'CROP_POLY':
                self.crop_poly = crop_polygon()
                self.crop_poly.from_command(cmd, in_transfom, in_x_mult, in_y_mult)
            elif tokens[0] == 'FAC':
                self.facades.append(facade())
                self.facades[-1].from_command(cmd, fac_resource_list, in_transfom, in_x_mult, in_y_mult)
            elif tokens[0] == 'OBJ_DELTA' or tokens[0] == 'OBJ_DRAPED' or tokens[0] == 'OBJ_GRADED' or tokens[0] == 'OBJ_SCRAPER':
                self.attached_objs.append(attached_obj())
                self.attached_objs[-1].from_command(cmd, obj_resource_list, in_transfom, in_x_mult, in_y_mult)
            elif tokens[0] == 'TREE':
                self.trees.append(tree())
                self.trees[-1].from_command(cmd, in_transfom, in_x_mult, in_y_mult)
            elif tokens[0] == 'TREE_LINE':
                self.tree_lines.append(tree_line())
                self.tree_lines[-1].from_command(cmd, in_transfom, in_x_mult, in_y_mult)

    def get_resources(self):
        """
        Returns a list of all used .objs and .facs as a tuple
        """
        objs = []
        facs = []
        
        for obj in self.attached_objs:
            objs.append(obj.resource)

        for obj in self.auto_split_objs:
            objs.extend(obj.resources)

        for fac in self.facades:
            facs.append(fac.resource)

        return objs, facs

    def to_commands(self, fac_resource_list, obj_resource_list):
        commands = []
        
        cur_cmd = ""

        cur_cmd = f"TILE {ftos(self.left_uv * 4096, 4)} {ftos(self.bottom_uv * 4096, 4)} {ftos(self.right_uv * 4096, 4)} {ftos(self.top_uv * 4096, 4)}"
        commands.append(cur_cmd)

        cur_cmd = f"ANCHOR_PT {ftos(self.anchor_x_uv * 4096, 4)} {ftos(self.anchor_y_uv * 4096, 4)}"
        commands.append(cur_cmd)

        cur_cmd = f"GROUND_PT {ftos(self.anchor_x_uv * 4096, 4)} {ftos(self.anchor_y_uv * 4096, 4)}"
        commands.append(cur_cmd)

        cur_cmd = f"ROTATION {self.rotation_n}"
        commands.append(cur_cmd)

        if self.crop_poly != None:
            cur_cmd = self.crop_poly.to_command(self.transform)
            commands.append(cur_cmd)

        for obj in self.attached_objs:
            cur_cmd = obj.to_command(obj_resource_list, self.transform)
            commands.append(cur_cmd)

        for obj in self.auto_split_objs:
            cmds = obj.to_commands(obj_resource_list, self.transform)
            commands.extend(cmds)

        for obj in self.facades:
            cur_cmd = obj.to_command(fac_resource_list, self.transform)
            commands.append(cur_cmd)

        for obj in self.trees:
            cur_cmd = obj.to_command(self.transform)
            commands.append(cur_cmd)

        for obj in self.tree_lines:
            cmds = obj.to_commands(self.transform)
            commands.extend(cmds)

        return commands

class agp:
    """
    Class to represent an X-Plane AGP (autogen point) file.
    """

    def __init__(self):
        self.alb_texture = ""
        self.nml_texture = ""
        self.nml_tile_rat = 1.0
        self.lit_texture = ""
        self.weather_texture = ""
        self.blend_mode = "BLEND"
        self.blend_cutoff = 0.5
        self.cast_shadow = True
        self.decals = []
        self.imported_decal_commands = []
        self.layer_group = "objects"
        self.layer_group_offset = 0

        self.imported_texture_scale_w = 1.0
        self.imported_texture_scale_h = -1.0
        self.imported_texture_width = 4096
        self.imported_texture_height = 4096

        self.surface = 'NONE'

        self.do_tiling = False
        self.tiling_x_pages = 0
        self.tiling_y_pages = 0
        self.tiling_map_x_res = 0
        self.tiling_map_y_res = 0
        self.tiling_map_texture = ""

        self.transform = agp_utils.agp_transform()

        self.vegetation = ""

        self.tiles = []  # List of tile objects

        self.render_tiles = True
        self.tile_lod = 20000

        self.name = ""

    def from_collection(self, in_collection):
        log_utils.new_section(f"Loading .agp collection {in_collection.name}")

        # Set texture tiling properties
        self.do_tiling = in_collection.xp_agp.is_texture_tiling
        self.tiling_x_pages = in_collection.xp_agp.texture_tiling_x_pages
        self.tiling_y_pages = in_collection.xp_agp.texture_tiling_y_pages
        self.tiling_map_x_res = in_collection.xp_agp.texture_tiling_map_x_res
        self.tiling_map_y_res = in_collection.xp_agp.texture_tiling_map_y_res
        self.tiling_map_texture = in_collection.xp_agp.texture_tiling_map_texture
        self.render_tiles = in_collection.xp_agp.render_tiles
        self.tile_lod = in_collection.xp_agp.tile_lod
        self.vegetation = in_collection.xp_agp.vegetation_asset

        #Get the material from the first mesh object in the collection
        mat = None
        for obj in in_collection.objects:
            if obj.type == 'MESH':
                #Check if it is the base tile. That is what we care about
                if obj.xp_agp.type == 'BASE_TILE' and obj.xp_agp.exportable:
                    if len(obj.data.materials) > 0:
                        mat = obj.data.materials[0]
                        break

        if mat is None:
            log_utils.error(f"No material found in the collection {in_collection.name}")
            return

        # Extract material data
        mat = mat.xp_materials

        if mat.do_separate_material_texture:
            log_utils.error("Error: X-Plane does not support separate material textures on lines/polygons/facades/agps. Please use a normal map with the metalness and glossyness in the blue and alpha channels respectively.")
            return

        self.alb_texture = mat.alb_texture
        self.lit_texture = mat.lit_texture
        self.nml_texture = mat.normal_texture
        self.weather_texture = mat.weather_texture
        self.do_blend = mat.blend_mode == 'BLEND'
        self.blend_cutoff = mat.blend_cutoff
        for decal in mat.decals:
            self.decals.append(decal)
        self.surface = mat.surface_type
        self.layer_group = mat.layer_group
        self.layer_group_offset = mat.layer_group_offset

        #Now that we have the material setup, we need to load all the individual tiles and their children
        for obj in in_collection.objects:
            if obj.parent == None and obj.xp_agp.type == 'BASE_TILE':
                new_tile = tile()
                new_tile.from_obj(obj, self.name)
                self.tiles.append(new_tile)

    def to_collection(self):
        log_utils.new_section(f"Creating .agp collection {self.name}")

        #Create the collection and set it's settings
        new_collection = bpy.data.collections.new(name=self.name)
        bpy.context.scene.collection.children.link(new_collection)

        new_collection.xp_agp.exportable = True
        new_collection.xp_agp.is_texture_tiling = self.do_tiling
        new_collection.xp_agp.texture_tiling_x_pages = self.tiling_x_pages
        new_collection.xp_agp.texture_tiling_y_pages = self.tiling_y_pages
        new_collection.xp_agp.texture_tiling_map_x_res = self.tiling_map_x_res
        new_collection.xp_agp.texture_tiling_map_y_res = self.tiling_map_y_res
        new_collection.xp_agp.texture_tiling_map_texture = self.tiling_map_texture
        new_collection.xp_agp.render_tiles = self.render_tiles
        new_collection.xp_agp.tile_lod = self.tile_lod
        new_collection.xp_agp.vegetation_asset = self.vegetation

        #Create the material for the collection
        mat = bpy.data.materials.new(name=self.name + "_Material")
        mat.xp_materials.alb_texture = self.alb_texture
        mat.xp_materials.lit_texture = self.lit_texture
        mat.xp_materials.normal_texture = self.nml_texture
        mat.xp_materials.blend_mode = self.blend_mode
        mat.xp_materials.blend_cutoff = self.blend_cutoff
        mat.xp_materials.surface_type = self.surface
        mat.xp_materials.is_separate_material_texture = False  # X-Plane does not support separate material textures on lines/polygons/facades/agps
        mat.xp_materials.layer_group = self.layer_group.upper()
        mat.xp_materials.layer_group_offset = self.layer_group_offset

        decal_alb_index = 0
        decal_nml_index = 2

        material_config.update_settings(mat)

        for decal in self.imported_decal_commands:
            if decal.startswith("NORMAL"):
                if decal_nml_index > 3:
                    log_utils.warning("Error: Too many normal decals! X-Plane only supports 2 normal decals per material.")
                    break
                decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_nml_index])
                decal_nml_index += 1
            else:
                if decal_alb_index > 2:
                    log_utils.warning("Error: Too many albedo decals! X-Plane only supports 2 decals per material.")
                    break
                decal_utils.get_decal_from_command(decal, mat.xp_materials.decals[decal_alb_index])
                decal_alb_index += 1

        for tile in self.tiles:
            #Create the tile object and link it to the collection
            tile.to_obj(new_collection, mat)

    def write(self, output_path):
        log_utils.new_section(f"Writing .agp {output_path}")

        output_folder = os.path.dirname(output_path)

        if len(self.tiles) == 0:
            log_utils.error("Must have at least 1 tile for .agp!")
            return

        #Define a string to hold the file contents
        of = "A\n1000\nAG_POINT\n\n"

        #Write the material data
        of += "#Materials\n"

        if self.alb_texture != "":
            of += "TEXTURE " + os.path.relpath(file_utils.rel_to_abs(self.alb_texture), output_folder) + "\n"
        if self.lit_texture != "":
            of += "TEXTURE_LIT " + os.path.relpath(file_utils.rel_to_abs(self.lit_texture), output_folder) + "\n"
        if self.nml_texture != "":
            of += "TEXTURE_NORMAL " + str(self.nml_tile_rat) + "\t" + os.path.relpath(file_utils.rel_to_abs(self.nml_texture), output_folder) + "\n"
        if self.weather_texture != "":
            of += "WEATHER " + os.path.relpath(file_utils.rel_to_abs(self.weather_texture), output_folder) + "\n"
        else:
            of += "WEATHER_TRANSPARENT\n"
        
        if not self.do_blend:
            of += "NO_BLEND " + misc_utils.ftos(self.blend_cutoff, 2) + "\n"
        
        of += "\n"

        #Write the decals
        if len(self.decals) > 0:
            of += "#Decals\n"
            for decal in self.decals:
                #Get the decal command
                decal_command = decal_utils.get_decal_command(decal, output_folder)
                if decal_command:
                    of += decal_command

            of += "\n"

        #Write the main polygon params
        of += "LAYER_GROUP " + self.layer_group.lower() + " " + str(self.layer_group_offset) + "\n"
        if self.surface != None:
            of += "SURFACE " + self.surface + "\n"
        if self.do_tiling:
            of += "TEXTURE_TILE " + str(int(self.tiling_x_pages)) + " " + str(int(self.tiling_y_pages)) + " " + str(int(self.tiling_map_x_res)) + " " + str(int(self.tiling_map_y_res)) + " " + os.path.relpath(file_utils.rel_to_abs(self.tiling_map_texture), output_folder) + "\n"
        if not self.render_tiles:
            of += "HIDE_TILES\n"
        if self.tile_lod != 20000:
            of += "TILE_LOD " + str(self.tile_lod) + "\n"

        self.transform = self.tiles[0].transform

        of += "\n#Scale\n"
        of += "TEXTURE_SCALE 4096 4096\n"
        of += "TEXTURE_WIDTH " + ftos(1 / (self.transform.x_ratio / 4096), 4) + "\n"
        of += "TEXTURE_HEIGHT " + ftos(1 / (self.transform.x_ratio / 4096) * self.transform.height_ratio, 4) + "\n"
        of += "\n"

        #Tiles
        of += "\n#Resources\n"

        fac_resource_list = []
        obj_resource_list = []

        #Now we need to get all our resources
        for t in self.tiles:
            objs, facs = t.get_resources()
            obj_resource_list.extend(objs)
            fac_resource_list.extend(facs)

        fac_resource_list = list(set(fac_resource_list))  # Remove duplicates
        obj_resource_list = list(set(obj_resource_list))  # Remove duplicates

        for fac in fac_resource_list:
            of += "FACADE " + fac + "\n"

        for obj in obj_resource_list:
            of += "OBJECT " + obj + "\n"

        if self.vegetation != "":
            of += "VEGETATION " + self.vegetation + "\n"

        #Tiles
        of += "\n#Tile Definitions\n\n"

        for t in self.tiles:
            cmds = t.to_commands(fac_resource_list, obj_resource_list)

            print(cmds)

            for c in cmds:
                of += c + "\n"

            of += "\n"

        #Write the output to the file
        with open(output_path, 'w') as f:
            f.write(of)

    def read(self, in_file):
        log_utils.new_section(f"Reading .agp {in_file}")

        self.name = in_file.split(os.sep)[-1]

        # Read the file
        with open(in_file, 'r') as f:
            lines = f.readlines()

        obj_resource_list = []
        fac_resource_list = []

        cur_tile_commands = []

        upscale_w = 1.0
        upscale_h = 1.0

        # Now we need to parse the file
        for line in lines:
            # Get the line
            line = line.strip()

            tokens = line.split()
            if not tokens:
                continue

            # Defensive: check token count for each command before using tokens
            cmd = tokens[0]
            min_tokens = {
                'TEXTURE_NOWRAP': 2,
                'TEXTURE': 2,
                'TEXTURE_LIT': 2,
                'WEATHER': 2,
                'NO_BLEND': 2,
                'LAYER_GROUP': 2, # can be 2 or 3, but 2 is safe
                'SURFACE': 2,
                'LOAD_CENTER': 5,
                'TEXTURE_TILE': 6
            }
            if cmd in min_tokens and len(tokens) < min_tokens[cmd]:
                log_utils.warning(f"Not enough tokens for command '{cmd}'! Expected at least {min_tokens[cmd]}, got {len(tokens)}. Line: '{line}'")
                continue

            #If we are in a tile command we need to add it to the list of current tile commands'
            if len(cur_tile_commands) > 0 and cmd != "TILE":
                cur_tile_commands.append(line)
                continue

            # Check for material data
            if cmd == "TEXTURE_NORMAL":
                self.nml_texture = tokens[2]
                self.normal_scale = float(tokens[1])
            elif cmd == "TEXTURE":
                self.alb_texture = tokens[1]
            elif cmd == "TEXTURE_LIT":
                self.lit_texture = tokens[1]
            elif cmd == "WEATHER" and cmd != "WEATHER_TRANSPARENT":
                self.weather_texture = tokens[1]
            elif cmd == "NO_BLEND":
                self.do_blend = False
                self.blend_cutoff = float(tokens[1])
            if cmd.startswith("DECAL") or cmd.startswith("NORMAL_DECAL"):
                self.imported_decal_commands.append(line)
            elif cmd == "LAYER_GROUP":
                self.layer_group = tokens[1].upper()
                if len(tokens) > 2:
                    self.layer_group_offset = tokens[2]
            elif cmd == "TEXTURE_WIDTH":
                self.imported_texture_scale_w = int(float(tokens[1]))
                if self.imported_texture_scale_h == -1:
                    self.imported_texture_scale_h = self.imported_texture_scale_w
            elif cmd == "TEXTURE_HEIGHT":
                self.imported_texture_scale_h = int(float(tokens[1]))
            elif cmd == "TEXTURE_SCALE":
                self.imported_texture_width = int(float(tokens[1]))
                if len(tokens) > 2:
                    self.imported_texture_height = int(float(tokens[2]))
                else:
                    self.imported_texture_height = self.imported_texture_width
                
                upscale_w = 4096.0 / self.imported_texture_width
                upscale_h = 4096.0 / self.imported_texture_height

                self.imported_texture_width *= upscale_w
                self.imported_texture_height *= upscale_h

            elif cmd == "SURFACE":
                self.surface = tokens[1]
                self.surface = self.surface.upper()
            elif cmd == "TEXTURE_TILE":
                self.do_tiling = True
                self.tiling_x_pages = int(tokens[1])
                self.tiling_y_pages = int(tokens[2])
                self.tiling_map_x_res = int(tokens[3])
                self.tiling_map_y_res = int(tokens[4])
                self.tiling_map_texture = tokens[5]
            elif cmd == "VEGETATION":
                self.vegetation = tokens[1]
            elif cmd == "OBJECT":
                # Add the object resource to the list
                obj_resource = tokens[1]
                obj_resource_list.append(obj_resource)
            elif cmd == "FACADE":
                # Add the facade resource to the list
                facade_resource = tokens[1]
                fac_resource_list.append(facade_resource)
            elif cmd == "HIDE_TILES":
                self.render_tiles = False
            elif cmd == "TILE_LOD":
                self.tile_lod = int(float(tokens[1]))
            elif cmd == "TILE":
                if len(cur_tile_commands) > 0:
                    #Define our transform
                    #First scale up our texture dimensions to 4096x4096 and scale down our texture scale so positions remain the same
                    self.transform.x_ratio = self.imported_texture_width / self.imported_texture_scale_w
                    self.transform.y_ratio = self.imported_texture_height / self.imported_texture_scale_h

                    print("Transforms")
                    print(self.transform.x_ratio)
                    print(self.transform.y_ratio)
                    
                    # We have a tile to process
                    new_tile = tile()
                    new_tile.transform = self.transform
                    new_tile.from_commands(cur_tile_commands, self.transform, upscale_w, upscale_h, fac_resource_list, obj_resource_list)
                    self.tiles.append(new_tile)
                    cur_tile_commands = []
                
                #Add this command and all future to the current tile
                cur_tile_commands.append(line)

        if len(cur_tile_commands) > 0:
            #Define our transform
            #First scale up our texture dimensions to 4096x4096 and scale down our texture scale so positions remain the same
            self.transform.x_ratio = self.imported_texture_width / self.imported_texture_scale_w
            self.transform.y_ratio = self.imported_texture_height / self.imported_texture_scale_h
            
            # We have a tile to process
            new_tile = tile()
            new_tile.transform = self.transform
            new_tile.from_commands(cur_tile_commands, self.transform, upscale_w, upscale_h, fac_resource_list, obj_resource_list)
            self.tiles.append(new_tile)
