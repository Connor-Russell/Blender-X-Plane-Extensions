#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/17/2025
#Module:    Export
#Purpose:   Provide a single file containing functions for exporting

import bpy #type: ignore
import os

from .Helpers import file_utils
from .Helpers import log_utils
from .Types import xp_lin
from .Types import xp_fac
from .Types import xp_pol
from .Types import xp_agp

def export_fac(in_col):
    #Create an xp_fac, load it from the collection, and write it to a file
    output = xp_fac.facade()
    output.from_collection(in_col)

    export_path = file_utils.resolve_file_export_path(in_col.xp_fac.name, in_col.name, ".fac")

    #Write the file
    output.write(export_path)

    log_utils.display_messages()
    
def export_lin(in_col):
    #Create an xp_lin, load it from the collection, and write it to a file
    output = xp_lin.line()
    output.from_collection(in_col)

    export_path = file_utils.resolve_file_export_path(in_col.xp_lin.name, in_col.name, ".lin")

    #Write the file
    output.write(export_path)

    log_utils.display_messages()

def export_pol(in_col):
    # Create an xp_pol, load it from the collection, and write it to a file
    output = xp_pol.polygon()
    output.from_collection(in_col)

    export_path = file_utils.resolve_file_export_path(in_col.xp_pol.name, in_col.name, ".pol")

    # Write the file
    output.write(export_path)

    log_utils.display_messages()

def export_agp(in_col):
    # Create an xp_agp, load it from the collection, and write it to a file
    output = xp_agp.agp()
    output.from_collection(in_col)

    export_path = ""
    if in_col.xp_agp.name != "":
        export_path = file_utils.resolve_file_export_path(in_col.xp_agp.name, in_col.name, ".agp")
        
        # Write the file
        output.write(export_path)

    log_utils.display_messages()
