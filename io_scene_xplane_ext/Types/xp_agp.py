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

    def to_obj(self, obj):
        if len(self.perimeter) == 0:
            return
        #Set the vertices in world coordinates
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, self.height)

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

        cmd = f"CROP_POLY "

        for vert in transformed_perimeter:
            cmd += f"{vert.x} {vert.y} "

        if len(transformed_perimeter) < 3:
            log_utils.warning("CROP_POLY must have at least 3 vertices.")
            self.perimeter = []
            return
        
        return cmd

    def from_command(self, in_command, fac_resource_list, transform: agp_utils.agp_transform):
        tokens = in_command.strip().split()

        # The rest are perimeter coordinates (x, y pairs)
        coords = tokens[1:]
        if len(coords) % 2 != 0:
            log_utils.warning(f"Invalid number of coordinates in CROP_POLY command: {in_command}")
            self.perimeter = []
            return

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

    def to_obj(self, obj):
        if not self.valid:
            return
        
        obj.xp_agp.facade_resource = self.resource
        obj.xp_agp.facade_height = self.height

        #Set the vertices in world coordinates
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, self.height)

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

        cmd = f"FAC {resource_index} {self.height} "

        for vert in transformed_perimeter:
            cmd += f"{vert.x} {vert.y} "

        return cmd

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
        new_obj = agp_utils.create_obj_from_perimeter(self.perimeter, self.layer)

        new_obj.xp_agp.tree_layer = self.layer

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
            log_utils.warning(f"Invalid Tree Line command: {in_command}")
            self.valid = False
            return

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

    def to_obj(self):
        #Create a new empty and set it's properties
        new_empty = bpy.data.objects.new("Tree", None)
        new_empty.empty_display_size = 1

        new_empty.scale.x = self.width / (2 * new_empty.empty_display_size)
        new_empty.scale.y = self.width / (2 * new_empty.empty_display_size)
        new_empty.scale.z = self.height / (2 * new_empty.empty_display_size)

        new_empty.location.x = self.x
        new_empty.location.y = self.y
        
        return new_empty

    def to_command(self, transform: agp_utils.agp_transform):
        if not self.valid:
            return ""

        cmd = ""

        x_pixel, y_pixel = agp_utils.to_pixel_coords(self.x, self.y, transform)

        cmd = f"TREE {x_pixel} {y_pixel} {self.height} {self.width} {self.layer}"

        return cmd

    def from_command(self, in_command, fac_resource_list, transform: agp_utils.agp_transform):
        tokens = in_command.split()

        x_pixel = float(tokens[1])
        y_pixel = float(tokens[2])
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

        new_empty.location.x = self.x
        new_empty.location.y = self.y
        new_empty.location.z = self.z
        new_empty.rotation_euler.z = self.heading

        return new_empty

    def to_command(self, obj_resource_list, transform: agp_utils.agp_transform):
        cmd = ""

        x_pixel, y_pixel = agp_utils.to_pixel_coords(self.x, self.y, transform)

        obj_index = obj_resource_list.index(self.resource)

        if not self.draped:
            cmd = f"OBJ_DELTA {x_pixel} {y_pixel} {self.heading} {self.z} {obj_index} {self.show_low} {self.show_high}"
        else:
            cmd = f"OBJ_DRAPED {x_pixel} {y_pixel} {self.heading} {obj_index} {self.show_low} {self.show_high}"

        return cmd

    def from_command(self, in_command, obj_resource_list, transform: agp_utils.agp_transform):
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
            x_pixel = float(tokens[1])
            y_pixel = float(tokens[2])
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
            x_pixel = float(tokens[1])
            y_pixel = float(tokens[2])
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
            x_pixel = float(tokens[1])
            y_pixel = float(tokens[2])
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

        #Get all the children of this object, recursively
        def get_children_recursive(obj):
            children = []
            for child in obj.children:
                children.append(child)
                children.extend(get_children_recursive(child))
            return children
        
        children = get_children_recursive(obj)

        def split_obj_by_material(obj):
            """
            Splits the given mesh object by material, returning a list of new objects (one per material).
            The original object is not modified.
            """
            mesh = obj.data
            mat_count = len(mesh.materials)
            new_objects = []

            for mat_index in range(mat_count):
                # Create a new mesh and object
                new_mesh = bpy.data.meshes.new(f"{obj.name}_mat_{mat_index}")
                new_obj = bpy.data.objects.new(f"{obj.name}_mat_{mat_index}", new_mesh)
                new_obj.matrix_world = obj.matrix_world.copy()
                new_obj.data.materials.append(mesh.materials[mat_index])

                # Use bmesh to filter faces by material
                bm = bmesh.new()
                bm.from_mesh(mesh)
                faces_to_keep = [f for f in bm.faces if f.material_index == mat_index]
                if not faces_to_keep:
                    bm.free()
                    bpy.data.meshes.remove(new_mesh)
                    continue

                # Deselect all, then select only the faces for this material
                for f in bm.faces:
                    f.select_set(False)
                for f in faces_to_keep:
                    f.select_set(True)

                # Duplicate the selected faces into a new bmesh
                bm_new = bmesh.new()
                bmesh.ops.duplicate(bm_new, geom=faces_to_keep)
                bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != mat_index], context='FACES')

                # Write the new bmesh to the new mesh
                bm.to_mesh(new_mesh)
                bm.free()
                bm_new.free()

                new_objects.append(new_obj)

            return new_objects

        all_mats = []
        mat_collections = []    #Aligned with all_mats
        all_objs = []

        for child in children:
            if child.type == 'MESH':
                split_objs = split_obj_by_material(child)

                #Move all the split objects by the inverse of their parent's location
                for split_obj in split_objs:
                    split_obj.location.x -= self.x
                    split_obj.location.y -= self.y
                    split_obj.location.z -= self.z

                all_objs.extend(split_objs)
                all_mats.extend(child.data.materials)

            else:
                #Move the object by the inverse of the parent's location
                child.location.x -= self.x
                child.location.y -= self.y
                child.location.z -= self.z

                all_objs.append(child)
        
        #Create the collections for each material
        all_mats = list(set(all_mats))  # Remove duplicates

        self.resoures = []
        for mat in all_mats:
            #Create a new collection for this material
            obj_name = agp_name + "_PT_" + obj.name + "_" + mat.name + ".obj"
            mat_collection = bpy.data.collections.new(obj_name)
            mat_collection.xplane.layer.name = obj_name
            self.resources.append(obj_name)
            mat_collection.xplane.is_exportable_collection = True
            mat_collection.xplane.layer.export_type = 'scenery'
            bpy.context.scene.collection.children.link(mat_collection)
            mat_collections.append(mat_collection)

        #Add one more collection for objects that don't have a material
        no_mat_collection = bpy.data.collections.new(agp_name + "_PT_" + obj.name + "_NO_MAT.obj")
        no_mat_collection.xplane.layer.name = no_mat_collection.name
        no_mat_collection.xplane.is_exportable_collection = True
        no_mat_collection.xplane.layer.export_type = 'scenery'
        bpy.context.scene.collection.children.link(no_mat_collection)
        mat_collections.append(no_mat_collection)

        #Now we need to move our new objetcs into the correct collections
        for obj in all_objs:
            if obj.type != 'MESH':
                #Non-mesh objects just get dumped into the first collection
                target_col = mat_collections[-1]  # The last collection is the "no material" collection
                target_col.objects.link(obj)
                continue
            #Find the material for this object
            obj_material = obj.active_material
            if obj_material is not None:
                #Find the collection for this material
                mat_index = all_mats.index(obj_material.name)
                if mat_index != -1:
                    mat_collection = mat_collections[mat_index]
                    #Move the object to the material collection
                    mat_collection.objects.link(obj)

        #Now we need to configure the settings for each collection
        for col in mat_collections:
            material_config.update_xplane_collection_settings(col)

        #Now we need to disable export on all other objects, export ours, then reenable ours

        original_collection_export_states = {}

        for col in bpy.data.collections:
            # Store the original export state
            original_collection_export_states[col.name] = col.xplane.is_exportable_collection

            col.xplane.is_exportable_collection = False

        for col in mat_collections:
            col.xplane.is_exportable_collection = True

        bpy.ops.scene.export_to_relative_dir()

        #Restore the original export states
        for col in bpy.data.collections:
            col.xplane.is_exportable_collection = original_collection_export_states[col.name]
        
        #We are now done with exporting, so we can remove the new objects and new colletcions
        for col in mat_collections:
            for obj in col.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col, do_unlink=True)

    def to_commands(self, obj_resource_list, transform: agp_utils.agp_transform):
        cmds = []

        x_pixel, y_pixel = agp_utils.to_pixel_coords(self.x, self.y, transform)

        for resource in self.resources:
            obj_index = obj_resource_list.index(resource)
            cmd = f"OBJ_DELTA {x_pixel} {y_pixel} {self.heading} {self.z} {obj_index} {self.show_low} {self.show_high}"
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

    def to_obj(self, obj):
        pass

    def from_commands(self, command, in_transfom):
        pass

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

        cur_cmd = f"TILE {self.left_uv * 4096} {self.bottom_uv * 4096} {self.right_uv * 4096} {self.top_uv * 4096}"
        commands.append(cur_cmd)

        cur_cmd = f"ANCHOR_PT {self.anchor_x_uv * 4096} {self.anchor_y_uv * 4096}"
        commands.append(cur_cmd)

        cur_cmd = f"GROUND_PT {self.anchor_x_uv * 4096} {self.anchor_y_uv * 4096}"
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

        self.name = ""

    def from_collection(self, in_collection):
        #Set the layer group and offset
        self.layer = in_collection.xp_pol.layer_group
        self.layer_offset = in_collection.xp_pol.layer_group_offset

        # Set texture tiling properties
        self.do_tiling = in_collection.xp_pol.is_texture_tiling
        self.tiling_x_pages = in_collection.xp_pol.texture_tiling_x_pages
        self.tiling_y_pages = in_collection.xp_pol.texture_tiling_y_pages
        self.tiling_map_x_res = in_collection.xp_pol.texture_tiling_map_x_res
        self.tiling_map_y_res = in_collection.xp_pol.texture_tiling_map_y_res
        self.tiling_map_texture = in_collection.xp_pol.texture_tiling_map_texture

        #Get the material from the first mesh object in the collection
        mat = None
        for obj in in_collection.objects:
            if obj.type == 'MESH':
                #Check if it has a material
                if len(obj.data.materials) > 0:
                    #Get the first material
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

        #Now that we have the material setup, we need to load all the individual tiles and their children
        for obj in in_collection.objects:
            if obj.parent == None and obj.xp_agp.type == 'BASE_TILE':
                new_tile = tile()
                new_tile.from_obj(obj, self.name)
                self.tiles.append(new_tile)

    def write(self, output_path):
        output_folder = os.path.dirname(output_path)

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
        of += "LAYER_GROUP " + self.layer.lower() + " " + str(self.layer_offset) + "\n"
        if self.surface != None:
            of += "SURFACE " + self.surface + "\n"
        if self.do_tiling:
            of += "TEXTURE_TILE " + str(int(self.tiling_x_pages)) + " " + str(int(self.tiling_y_pages)) + " " + str(int(self.tiling_map_x_res)) + " " + str(int(self.tiling_map_y_res)) + " " + os.path.relpath(file_utils.rel_to_abs(self.tiling_map_texture), output_folder) + "\n"

        if len(self.tiles) == 0:
            log_utils.error("Must have at least 1 tile for .agp!")
            return

        self.transform = self.tiles[0].transform

        of += "\n#Scale\n"
        of += "TEXTURE_SCALE 4096 4096\n"
        of += "TEXTURE_WIDTH " + str(1 / (self.transform.x_ratio / 4096)) + "\n"
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
