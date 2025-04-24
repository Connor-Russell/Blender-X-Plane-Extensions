#Project:   Blender-X-Plane-Lin-Exporter
#Author:    Connor Russell
#Date:      2/23/2025
#Module:    Import
#Purpose:   Provide a single file containing functions for importing

import bpy #type: ignore

from .Helpers import line_utils
from .Types import xp_lin
from .Types import xp_fac

def import_lin(in_path):
    #Define just the file name from the path
    in_name = in_path
    in_name = in_path.split("\\")[-1]

    #Read it
    lin = xp_lin.line()
    lin.read(in_path)
    lin.to_collection(in_name)

def import_fac(in_path):
    #Define just the file name from the path
    in_name = in_path
    in_name = in_path.split("\\")[-1]

    #Read it
    fac = xp_fac.facade()
    print(f"Importing {in_name}...")
    fac.read(in_path)
    fac.to_scene()

    