#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Export
#Purpose:   Provide a single file containing functions for exporting

import bpy #type: ignore
import os

from .Helpers import file_utils
from .Helpers import line_utils
from .Types import xp_lin
from .Types import xp_fac
from .Types import xp_pol

def export_fac(in_col):
    #Create an xp_fac, load it from the collection, and write it to a file
    output = xp_fac.facade()
    output.from_collection(in_col)

    export_path = ""
    if in_col.xp_fac.name != "":
        export_path = file_utils.rel_to_abs(in_col.xp_fac.name + ".fac")
    else:
        export_path = os.path.join(os.path.dirname(bpy.data.filepath), in_col.name + ".fac")

    if export_path.lower().endswith(".fac.fac"):
        export_path = export_path[:-4]

    #Write the file
    output.write(export_path)
    
def export_lin(in_col):
    #Create an xp_lin, load it from the collection, and write it to a file
    output = xp_lin.line()
    output.from_collection(in_col)

    export_path = ""
    if in_col.xp_lin.name != "":
        export_path = file_utils.rel_to_abs(in_col.xp_lin.name + ".lin")
    else:
        export_path = os.path.join(os.path.dirname(bpy.data.filepath), in_col.name + ".lin")

    if export_path.lower().endswith(".lin.lin"):
        export_path = export_path[:-4]

    #Write the file
    output.write(export_path)

def export_pol(in_col):
    # Create an xp_pol, load it from the collection, and write it to a file
    output = xp_pol.polygon()
    output.from_collection(in_col)

    export_path = ""
    if in_col.xp_pol.name != "":
        export_path = file_utils.rel_to_abs(in_col.xp_pol.name + ".pol")
    else:
        export_path = os.path.join(os.path.dirname(bpy.data.filepath), in_col.name + ".pol")

    if export_path.lower().endswith(".pol.pol"):
        export_path = export_path[:-4]

    # Write the file
    output.write(export_path)


