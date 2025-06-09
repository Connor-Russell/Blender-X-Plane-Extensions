#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      2/23/2025
#Module:    Import
#Purpose:   Provide a single file containing functions for importing

import bpy #type: ignore

from .Helpers import line_utils
from .Types import xp_lin
from .Types import xp_fac
from .Types import xp_obj
from .Types import xp_pol
from .Types import xp_agp
import os

def import_lin(in_path):
    #Define just the file name from the path
    in_name = in_path
    in_name = in_path.split(os.sep)[-1]

    #Read it
    lin = xp_lin.line()
    lin.read(in_path)
    lin.to_collection(in_name)

def import_pol(in_path):
    #Define just the file name from the path
    in_name = in_path
    in_name = in_path.split(os.sep)[-1]

    #Read it
    pol = xp_pol.polygon()
    print(f"Importing {in_name}...")
    pol.read(in_path)
    pol.to_scene()

def import_fac(in_path):
    #Define just the file name from the path
    in_name = in_path
    in_name = in_path.split(os.sep)[-1]

    #Read it
    fac = xp_fac.facade()
    print(f"Importing {in_name}...")
    fac.read(in_path)
    fac.to_scene()

def import_obj(in_path):
    #Define just the file name from the path
    in_name = in_path
    in_name = in_path.split(os.sep)[-1]

    #Read it
    obj = xp_obj.object()
    print(f"Importing {in_name}...")
    obj.read(in_path)
    obj.to_scene()
    
def import_agp(in_path):
    #Define just the file name from the path
    in_name = in_path
    in_name = in_path.split(os.sep)[-1]

    #Read it
    agp = xp_agp.agp()
    print(f"Importing {in_name}...")
    agp.read(in_path)
    agp.to_collection()
