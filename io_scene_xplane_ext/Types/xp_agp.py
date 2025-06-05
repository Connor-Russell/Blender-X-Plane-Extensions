#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      6/5/2025
#Module:    XP_AGP
#Purpose:   Provide classes that abstracts the X-Plane AGP format

from ..Helpers import agp_utils

import mathutils
import bpy

class crop_polygon:
    """
    Class to abstract the crop_polygon in X-Plane's AGP format
    """

    def __init__(self):
        self.perimeter = [] #List of mathutils.Vector. Stored in world coordinates

    def from_obj(self, obj):
        #Get the vertices in world coordinates
        self.perimeter = agp_utils.get_perimeter_from_mesh(obj)

    def to_obj(self, obj):
        #Set the vertices in world coordinates
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, self.height)

        return new_obj

    def to_commmand(self, transform: agp_utils.agp_transform):
        cmd = ""

        #Now we need to copy our perimeter and transform it
        transformed_perimeter = []
        for vert in self.perimeter:
            #Transform the vertex using the agp_transform
            pixel_x, pixel_y = agp_utils.to_pixel_coords(vert.x, vert.y, transform)
            transformed_perimeter.append(mathutils.Vector((pixel_x, pixel_y, 0)))

        cmd = f"CROP_POLY "

        for vert in transformed_perimeter:
            cmd += f"{vert.x} {vert.y} "

        if len(transformed_perimeter) < 3:
            raise ValueError("CROP_POLY must have at least 3 vertices.")
        
        return cmd

    def from_command(self, in_command, fac_resource_list, transform: agp_utils.agp_transform):
        tokens = in_command.strip().split()

        # The rest are perimeter coordinates (x, y pairs)
        coords = tokens[1:]
        if len(coords) % 2 != 0:
            raise ValueError(f"Invalid number of coordinates in CROP_POLY command: {in_command}")

        self.perimeter = []
        for i in range(0, len(coords), 2):
            pixel_x = float(coords[i])
            pixel_y = float(coords[i+1])
            blender_x, blender_y = agp_utils.to_blender_coords(pixel_x, pixel_y, transform)
            self.perimeter.append(mathutils.Vector((blender_x, blender_y, 0)))

class facade:
    """
    Class to abstract the placement of a facade in X-Plane's AGP format
    """

    def __init__(self):
        self.resource = ""
        self.height = 10.0
        self.perimeter = [] #List of mathutils.Vector. Stored in world coordinates

    def from_obj(self, obj):
        self.resource = obj.xp_agp.facade_resource
        self.height = obj.xp_agp.facade_height

        #Get the vertices in world coordinates
        self.perimeter = agp_utils.get_perimeter_from_mesh(obj)

    def to_obj(self, obj):
        obj.xp_agp.facade_resource = self.resource
        obj.xp_agp.facade_height = self.height

        #Set the vertices in world coordinates
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, self.height)

        return new_obj

    def to_commmand(self, fac_resource_list, transform: agp_utils.agp_transform):
        cmd = ""

        #Find out resource index
        resource_index = fac_resource_list.index(self.resource)

        #Now we need to copy our perimeter and transform it
        transformed_perimeter = []
        for vert in self.perimeter:
            #Transform the vertex using the agp_transform
            pixel_x, pixel_y = agp_utils.to_pixel_coords(vert.x, vert.y, transform)
            transformed_perimeter.append(mathutils.Vector((pixel_x, pixel_y, 0)))

        cmd = f"FAC {resource_index} {self.height} "

        for vert in transformed_perimeter:
            cmd += f"{vert.x} {vert.y} "

    def from_command(self, in_command, fac_resource_list, transform: agp_utils.agp_transform):
        """
        Parse a FAC command and set the facade's properties accordingly.
        Args:
            in_command (str): The FAC command string (e.g. 'FAC 0 10.0 x1 y1 x2 y2 ...').
            fac_resource_list (list): List of resource names, indexed by resource index.
            transform (agp_utils.agp_transform): Transform to convert pixel coords to Blender coords.
        """
        tokens = in_command.strip().split()
        if len(tokens) < 4 or tokens[0] != 'FAC':
            raise ValueError(f"Invalid FAC command: {in_command}")

        resource_index = int(tokens[1])
        self.resource = fac_resource_list[resource_index]
        self.height = float(tokens[2])

        # The rest are perimeter coordinates (x, y pairs)
        coords = tokens[3:]
        if len(coords) % 2 != 0:
            raise ValueError(f"Invalid number of coordinates in FAC command: {in_command}")

        self.perimeter = []
        for i in range(0, len(coords), 2):
            pixel_x = float(coords[i])
            pixel_y = float(coords[i+1])
            blender_x, blender_y = agp_utils.to_blender_coords(pixel_x, pixel_y, transform)
            self.perimeter.append(mathutils.Vector((blender_x, blender_y, 0)))

class tree_line:
    """
    Class to abstract the placement of a tree line in X-Plane's AGP format
    """

    def __init__(self):
        self.layer = 0
        self.perimeter = [] #List of mathutils.Vector. Stored in world coordinates

    def from_obj(self, obj):
        self.layer = obj.xp_agp.tree_layer

        #Get the vertices in world coordinates
        self.perimeter = agp_utils.get_perimeter_from_mesh(obj)

    def to_obj(self, obj):
        obj.xp_agp.tree_layer = self.layer

        #Set the vertices in world coordinates
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, self.layer)

        return new_obj

    def to_commmands(self, transform: agp_utils.agp_transform):
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
            cur_cmd = f"TREE_LINE {transformed_perimeter[i].x} {transformed_perimeter[i].y} {transformed_perimeter[i+1].x} {transformed_perimeter[i+1].y} {self.layer}"
            cmds.append(cur_cmd)

        return cmds

    def from_command(self, in_command, transform: agp_utils.agp_transform):
        """
        Parse a TREE_LINE command and set the tree line's properties accordingly.
        Args:
            in_command (str): The FAC command string (e.g. 'FAC 0 10.0 x1 y1 x2 y2 ...').
            transform (agp_utils.agp_transform): Transform to convert pixel coords to Blender coords.
        """

        tokens = in_command.strip().split()
        if len(tokens) < 4 or tokens[0] != 'FAC':
            raise ValueError(f"Invalid FAC command: {in_command}")

        resource_index = int(tokens[1])
        start_x = float(tokens[2])
        start_y = float(tokens[3])
        end_x = float(tokens[4])
        end_y = float(tokens[5])

        self.perimeter = []
        self.perimeter.append(mathutils.Vector((start_x, start_y, 0)))
        self.perimeter.append(mathutils.Vector((end_x, end_y, 0)))

        for vert in self.perimeter:
            blender_x, blender_y = agp_utils.to_blender_coords(vert.x, vert.y, transform)
            self.perimeter.append(mathutils.Vector((blender_x, blender_y, 0)))

class tree:
    """
    Class to abstract an individual tree in X-Plane's AGP format
    """

    def __init__(self):
        self.layer = ""
        self.x = 0.0
        self.y = 0.0
        self.width = 10
        self.height = 10

    def from_obj(self, obj):
        self.resource = obj.xp_agp.tree_resource

        #We'll extract the width and height from the empty
        #First we'll get the arrow length. Then we'll multiply that by 2, then the avg x/y scale and z scale for width/height, respectively
        self.width = obj.empty_display_size * 2 * ((obj.scale.x + obj.scale.y) / 2)
        self.height = obj.empty_display_size * 2 * obj.scale.z

        self.x = obj.location.x
        self.y = obj.location.y

    def to_obj(self):
        #Create a new empty and set it's properties
        new_empty = bpy.data.objects.new("Tree", None)
        new_empty.xp_agp.tree_resource = self.resource
        new_empty.empty_display_size = 1

        new_empty.scale.x = self.width / (2 * new_empty.empty_display_size)
        new_empty.scale.y = self.width / (2 * new_empty.empty_display_size)
        new_empty.scale.z = self.height / (2 * new_empty.empty_display_size)

        new_empty.location.x = self.x
        new_empty.location.y = self.y
        
        return new_empty

    def to_command(self, transform: agp_utils.agp_transform):
        cmd = ""

        x_pixel, y_pixel = agp_utils.to_pixel_coords(self.x, self.y, transform)

        cmd = f"TREE {x_pixel} {y_pixel} {self.height} {self.width} {self.layer}"

    def from_command(self, in_command, fac_resource_list, transform: agp_utils.agp_transform):
        tokens = in_command.split()

        x_pixel = float(tokens[1])
        y_pixel = float(tokens[2])
        self.height = float(tokens[3])
        self.width = float(tokens[4])
        self.layer = int(tokens[5])

        #Convert the pixel coords to Blender coords
        self.x, self.y = agp_utils.to_blender_coords(x_pixel, y_pixel, transform)

