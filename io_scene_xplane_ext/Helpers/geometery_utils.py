#Project: BlenderFacadeExporter
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

    def to_string(self):
        return "VERTEX\t" + misc_utils.ftos(self.loc_x, 8) + "\t" + misc_utils.ftos(self.loc_z, 8) + "\t" + misc_utils.ftos(self.loc_y, 8) + "\t" + misc_utils.ftos(self.normal_x, 8) + "\t" + misc_utils.ftos(self.normal_z, 8) + "\t" + misc_utils.ftos(self.normal_y, 8) + "\t" + misc_utils.ftos(self.uv_x, 8) + "\t" + misc_utils.ftos(self.uv_y, 8)

#Rotate a vertex around an axis ("x", "y", or "z"). Angle must be in degrees. Returns the new vertex as a tuple of x y z in that order.
def rotate_vertex_on_axis(vertex, angle, axis):
    # Convert the angle to radians
    angle = math.radians(angle)

    # Get the sin and cos of the angle
    sin = math.sin(angle)
    cos = math.cos(angle)

    # Get the axis
    axis = axis.lower()

    # Rotate the vertex
    if axis == "x":
        new_x = vertex[0]
        new_y = vertex[1] * cos - vertex[2] * sin
        new_z = vertex[1] * sin + vertex[2] * cos
    elif axis == "y":
        new_x = vertex[0] * cos + vertex[2] * sin
        new_y = vertex[1]
        new_z = -vertex[0] * sin + vertex[2] * cos
    elif axis == "z":
        new_x = vertex[0] * cos - vertex[1] * sin
        new_y = vertex[0] * sin + vertex[1] * cos
        new_z = vertex[2]
    else:
        raise ValueError("Invalid axis. Must be 'x', 'y', or 'z'")

    return (new_x, new_y, new_z)

#Creates a Blender mesh and object from an X-Plane draw call
def create_obj_from_draw_call(verticies, indicies, name):
    #Create a new bmesh
    bm = bmesh.new()

    #Add all the verticies
    for vertex in verticies:
        bm.verts.new((vertex.loc_x, vertex.loc_y, vertex.loc_z))

    # Update the bmesh to ensure the vertices are added
    bm.verts.ensure_lookup_table()

    #Create a uv layer
    uv_layer = bm.loops.layers.uv.new()

    #Iterate through the indicies, 3 at a time, and create a face with the verticies at specified indicies
    i = 0

    while i < len(indicies) - 2:
        # Add vertices to the bmesh
        v1 = verticies[indicies[i]]
        v2 = verticies[indicies[i + 1]]
        v3 = verticies[indicies[i + 2]]

        #Create new vertices in the bmesh for each vertex
        v1 = bm.verts.new((v1.loc_x, v1.loc_y, v1.loc_z))
        v2 = bm.verts.new((v2.loc_x, v2.loc_y, v2.loc_z))
        v3 = bm.verts.new((v3.loc_x, v3.loc_y, v3.loc_z))
        
        #Set the normals for the vertices
        v1.normal = (verticies[indicies[i]].normal_x, verticies[indicies[i]].normal_y, verticies[indicies[i]].normal_z)
        v2.normal = (verticies[indicies[i + 1]].normal_x, verticies[indicies[i + 1]].normal_y, verticies[indicies[i + 1]].normal_z)
        v3.normal = (verticies[indicies[i + 2]].normal_x, verticies[indicies[i + 2]].normal_y, verticies[indicies[i + 2]].normal_z)

        # Update the bmesh to ensure the vertices are added
        bm.verts.ensure_lookup_table()

        # Create a new face with the vertices
        face = bm.faces.new([v1, v2, v3])

        #Assign the UV coordinates to the face
        face.loops[0][uv_layer].uv = (verticies[indicies[i]].uv_x, verticies[indicies[i]].uv_y)
        face.loops[1][uv_layer].uv = (verticies[indicies[i + 1]].uv_x, verticies[indicies[i + 1]].uv_y)
        face.loops[2][uv_layer].uv = (verticies[indicies[i + 2]].uv_x, verticies[indicies[i + 2]].uv_y)

        # Update the bmesh to ensure the face is added
        bm.faces.ensure_lookup_table()

        i = i + 3

    # Finish up, write the bmesh back to the mesh
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    # Create an object with the mesh and link it to the scene
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    return obj

#Get the geometry from an object. Returns a tuple of XPVertex and integer indicies that represent the faces.
def get_draw_call_from_obj(obj):
    # Ensure the object is a mesh
    if obj.type != 'MESH':
        raise TypeError("Object must be a mesh")

    #Get our mesh data
    mesh = obj.data

    #Calculate split normals if this mesh has them
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

    #Now we iterate through teh loop triangles to populate our array of XPTriangles
    for tri in loop_triangles:

        #Define our UV and normal data beforehand. The struct is immutable so we can't change it after the fact
        xp_triangle_uvs = ((0, 0), (0, 0), (0, 0))
        if uv_layer != None:
            xp_triangle_uvs = (uv_layer.data[tri.loops[0]].uv, uv_layer.data[tri.loops[1]].uv, uv_layer.data[tri.loops[2]].uv)

        xp_triangles_normals = (tri.split_normals[0], tri.split_normals[1], tri.split_normals[2])
        if not tri.use_smooth:
            xp_triangles_normals = (tri.normal, tri.normal, tri.normal)


        #Define a temporary face with the data from the loop triangle. UVs default to none so we can add them IF we do have a uv layer
        tmp_face = XPTriangle(
            vertex_pos = (mesh.vertices[tri.vertices[0]].co, mesh.vertices[tri.vertices[1]].co, mesh.vertices[tri.vertices[2]].co),
            vertex_nrm = xp_triangles_normals,
            uvs = xp_triangle_uvs
        )

        #Append the face to the array
        xp_triangles.append(tmp_face)

    #Now that we have the faces stored, we need to actually turn them into verticies and indicies.
    #This is a bit more complicated. We have to iterate through every face. Then we need to check if *any* of it's 3 verticies already exist - if they do, we will use the existing one instead
    #Once we know the indicies of each vertex because it's either been added, or already exists, we can do the index output array, which would be in the order of last vertex, middle, first. 

    #Define our output arrays
    out_verts = []  #Array of XPVertex
    out_inds = []   #Ints

    for t in xp_triangles:
        #Define verticies for each triangle. Then see if they exist, if they don't, add them.
        v1 = xp_vertex(t.vertex_pos[0][0], t.vertex_pos[0][1], t.vertex_pos[0][2], t.vertex_nrm[0][0], t.vertex_nrm[0][1], t.vertex_nrm[0][2], t.uvs[0][0], t.uvs[0][1])
        v2 = xp_vertex(t.vertex_pos[1][0], t.vertex_pos[1][1], t.vertex_pos[1][2], t.vertex_nrm[1][0], t.vertex_nrm[1][1], t.vertex_nrm[1][2], t.uvs[1][0], t.uvs[1][1])
        v3 = xp_vertex(t.vertex_pos[2][0], t.vertex_pos[2][1], t.vertex_pos[2][2], t.vertex_nrm[2][0], t.vertex_nrm[2][1], t.vertex_nrm[2][2], t.uvs[2][0], t.uvs[2][1])

        try_optomize = False

        if try_optomize:
            v1_index = MiscUtils.linear_search_list(out_verts, v1)
            v2_index = MiscUtils.linear_search_list(out_verts, v2)
            v3_index = MiscUtils.linear_search_list(out_verts, v3)

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

    #Now we loop through the verticies and apply the transform to each one
    for v in out_verts:
        #Get the local position as a vector
        local_position = mathutils.Vector((v.loc_x, v.loc_y, v.loc_z))
        normal = mathutils.Vector((v.normal_x, v.normal_y, v.normal_z))

        #Apply the full transformation
        transformed_position = transform @ local_position

        #Work to apply the transform to the normals
        normal_matrix = obj.matrix_world.inverted().transposed()
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

    #Return the verticies and indicies
    return (out_verts, out_inds)
