#Project: Blender-X-Plane-Extensions
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide utility functions to work with geometry (things like rotating a point, etc)

import collections
import math
import bpy #type: ignore
import bmesh #type: ignore
import mathutils #type: ignore
from . import misc_utils

#Simple container to hold an X-Plane Vertex
class xp_vertex:
    """
    Simple class that contains all the data for a vertex in X-Plane.
    """
    loc_x = 0
    loc_y = 0
    loc_z = 0

    normal_x = 0
    normal_y = 0
    normal_z = 0

    uv_x = 0
    uv_y = 0

    def __init__(self, loc_x, loc_y, loc_z, normal_x, normal_y, normal_z, uv_x, uv_y):
        self.loc_x = loc_x
        self.loc_y = loc_y
        self.loc_z = loc_z

        self.normal_x = normal_x
        self.normal_y = normal_y
        self.normal_z = normal_z

        self.uv_x = uv_x
        self.uv_y = uv_y

    def __eq__(self, other):
        return self.loc_x == other.loc_x and self.loc_y == other.loc_y and self.loc_z == other.loc_z and self.normal_x == other.normal_x and self.normal_y == other.normal_y and self.normal_z == other.normal_z and self.uv_x == other.uv_x and self.uv_y == other.uv_y

def create_obj_from_draw_call(vertices, indicies, name):
    """
    Create a Blender mesh and object from an X-Plane draw call.
    Args:
        vertices (list of xp_vertex): List of xp_vertex objects representing the vertices.
        indicies (list of int): List of indices to create faces with the vertices.
        name (str): Name for the new object.
    Returns:
        bpy.types.Object: The created Blender object.
    """
    #Create a new bmesh
    bm = bmesh.new()

    #Add all the vertices
    for vertex in vertices:
        v = bm.verts.new((vertex.loc_x, vertex.loc_y, vertex.loc_z))
        v.normal = (vertex.normal_x, vertex.normal_y, vertex.normal_z)


    # Update the bmesh to ensure the vertices are added
    bm.verts.ensure_lookup_table()

    #Create a uv layer
    uv_layer = bm.loops.layers.uv.new()

    #Iterate through the indicies, 3 at a time, and create a face with the vertices at specified indicies
    i = 0

    while i < len(indicies) - 2:
        #Get the vertices at the indicies
        v1 = bm.verts[indicies[i]]
        v2 = bm.verts[indicies[i + 1]]
        v3 = bm.verts[indicies[i + 2]]
        
        # Create a new face with the vertices
        face = bm.faces.new([v1, v2, v3])

        #Assign the UV coordinates to the face
        face.loops[0][uv_layer].uv = (vertices[indicies[i]].uv_x, vertices[indicies[i]].uv_y)
        face.loops[1][uv_layer].uv = (vertices[indicies[i + 1]].uv_x, vertices[indicies[i + 1]].uv_y)
        face.loops[2][uv_layer].uv = (vertices[indicies[i + 2]].uv_x, vertices[indicies[i + 2]].uv_y)

        # Update the bmesh to ensure the face is added
        bm.faces.ensure_lookup_table()

        i = i + 3

    # Finish up, write the bmesh back to the mesh
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    # Set the custom normals
    loop_normals = []
    for i in range(0, len(indicies), 3):
        nml1 = (vertices[indicies[i]].normal_x, vertices[indicies[i]].normal_y, vertices[indicies[i]].normal_z)
        nml2 = (vertices[indicies[i + 1]].normal_x, vertices[indicies[i + 1]].normal_y, vertices[indicies[i + 1]].normal_z)
        nml3 = (vertices[indicies[i + 2]].normal_x, vertices[indicies[i + 2]].normal_y, vertices[indicies[i + 2]].normal_z)
        nml1 = mathutils.Vector(nml1).normalized()
        nml2 = mathutils.Vector(nml2).normalized()
        nml3 = mathutils.Vector(nml3).normalized()
        loop_normals.append(nml1)
        loop_normals.append(nml2)
        loop_normals.append(nml3)

    mesh.normals_split_custom_set(loop_normals)
    if bpy.app.version < (4, 1, 0):
        mesh.use_auto_smooth = True  # Enable auto-smooth to use custom normals

    # Create an object with the mesh and link it to the scene
    obj = bpy.data.objects.new(name, mesh)

    return obj

def get_draw_call_from_obj(obj):
    """
    Get the geometry from a Blender object and return it as a tuple of xp_vertexs and integer indices.
    Args:
        obj (bpy.types.Object): Blender object to extract geometry from.
    """

    # Ensure the object is a mesh
    if obj.type != 'MESH':
        raise TypeError("Object must be a mesh")
    
    #Define our output arrays
    out_verts = []  #Array of xp_vertex
    out_inds = []   #Ints

    #Check if this object has modifiers. If it does, we'll duplicate it, and apply the modifiers to the duplicate.
    did_duplicate = False
    if len(obj.modifiers) > 0:
        #Make sure we are in object mode before we duplicate and apply the modifiers
        bpy.context.view_layer.objects.active = obj
        if bpy.context.active_object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        obj = obj.copy()
        obj.data = obj.data.copy()
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        did_duplicate = True

        for mod in obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=mod.name)

    try:
        #Get our mesh data
        mesh = obj.data

        #Calculate split normals if this mesh has them. Note used in 4.1+ but this property wouldn't exist there soo it should be fine
        if hasattr(mesh, "calc_normals_split"):
            mesh.calc_normals_split()

        #Triangulate the mesh and get the loop triangles
        mesh.calc_loop_triangles()
        loop_triangles = mesh.loop_triangles

        #Attempt to get the uv layer. We look for the first layer. 
        try:
            uv_layer = mesh.uv_layers[0]
        except (KeyError, TypeError) as e:
            uv_layer = None

        #Define a temporary data structure to hold our triangle faces.
        XPTriangle = collections.namedtuple(
                        "XPTriangle",
                        field_names=[
                            "vertex_pos",  # Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]] Tuple containing the positions for each vertex. Only used when smooth is true
                            "vertex_nrm",  # Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]] Tuple containing the normals for each vertex. Only used when smooth is true
                            "uvs",  # type: Tuple[[float, float], [float, float], [float, float]]
                        ],
                    )
        
        #Define an array to hold our faces
        xp_triangles = []

        #TODO: We need to warn the user if this is Blender 4.1+ and they have an autosmooth modifier on the object, as this does not get applied to the normals

        for tri in loop_triangles:

            #Define our UV and normal data beforehand. The struct is immutable so we can't change it after the fact
            xp_triangle_uvs = ((0, 0), (0, 0), (0, 0))
            if uv_layer != None:
                xp_triangle_uvs = (uv_layer.data[tri.loops[0]].uv, uv_layer.data[tri.loops[1]].uv, uv_layer.data[tri.loops[2]].uv)

            xp_triangles_normals = (tri.split_normals[0], tri.split_normals[1], tri.split_normals[2])


            #Define a temporary face with the data from the loop triangle. UVs default to none so we can add them IF we do have a uv layer
            tmp_face = XPTriangle(
                vertex_pos = (mesh.vertices[tri.vertices[0]].co, mesh.vertices[tri.vertices[1]].co, mesh.vertices[tri.vertices[2]].co),
                vertex_nrm = xp_triangles_normals,
                uvs = xp_triangle_uvs
            )

            #Append the face to the array
            xp_triangles.append(tmp_face)

        #Now that we have the faces stored, we need to actually turn them into vertices and indicies.
        #This is a bit more complicated. We have to iterate through every face. Then we need to check if *any* of it's 3 vertices already exist - if they do, we will use the existing one instead
        #Once we know the indicies of each vertex because it's either been added, or already exists, we can do the index output array, which would be in the order of last vertex, middle, first. 

        for t in xp_triangles:
            #Define vertices for each triangle. Then see if they exist, if they don't, add them.
            v1 = xp_vertex(t.vertex_pos[0][0], t.vertex_pos[0][1], t.vertex_pos[0][2], t.vertex_nrm[0][0], t.vertex_nrm[0][1], t.vertex_nrm[0][2], t.uvs[0][0], t.uvs[0][1])
            v2 = xp_vertex(t.vertex_pos[1][0], t.vertex_pos[1][1], t.vertex_pos[1][2], t.vertex_nrm[1][0], t.vertex_nrm[1][1], t.vertex_nrm[1][2], t.uvs[1][0], t.uvs[1][1])
            v3 = xp_vertex(t.vertex_pos[2][0], t.vertex_pos[2][1], t.vertex_pos[2][2], t.vertex_nrm[2][0], t.vertex_nrm[2][1], t.vertex_nrm[2][2], t.uvs[2][0], t.uvs[2][1])

            try_optomize = False

            if try_optomize:
                v1_index = misc_utils.linear_search_list(out_verts, v1)
                v2_index = misc_utils.linear_search_list(out_verts, v2)
                v3_index = misc_utils.linear_search_list(out_verts, v3)

                if v1_index == -1:
                    out_verts.append(v3)
                    v1_index = len(out_verts) - 1
                if v2_index == -1:
                    out_verts.append(v2)
                    v2_index = len(out_verts) - 1
                if v3_index == -1:
                    out_verts.append(v1)
                    v3_index = len(out_verts) - 1
            else:
                out_verts.append(v3)
                v1_index = len(out_verts) - 1
                out_verts.append(v2)
                v2_index = len(out_verts) - 1
                out_verts.append(v1)
                v3_index = len(out_verts) - 1

            #Now finally we add the indicies! These are in the order v3, v2, v1
            out_inds.append(v3_index)
            out_inds.append(v2_index)
            out_inds.append(v1_index)

        #Now we need to get the transform matrix for the object
        transform = obj.matrix_world

        #Now we loop through the vertices and apply the transform to each one
        for v in out_verts:
            #Get the local position as a vector
            local_position = mathutils.Vector((v.loc_x, v.loc_y, v.loc_z))
            normal = mathutils.Vector((v.normal_x, v.normal_y, v.normal_z))

            #Apply the full transformation
            transformed_position = transform @ local_position

            #Work to apply the transform to the normals
            normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
            transformed_normal = normal_matrix @ normal
            transformed_normal.normalize()

            #Set the new position and rotation
            v.loc_x = transformed_position.x
            v.loc_y = transformed_position.y
            v.loc_z = transformed_position.z

            #Set the new normal
            v.normal_x = transformed_normal.x
            v.normal_y = transformed_normal.y
            v.normal_z = transformed_normal.z

    finally:
        #If we made a duplicate object, delete it
        if did_duplicate and obj != None:
            bpy.data.objects.remove(obj, do_unlink=True)
            obj = None

        return (out_verts, out_inds)

