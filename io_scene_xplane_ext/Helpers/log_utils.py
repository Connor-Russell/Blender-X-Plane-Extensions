#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      6/3/2025
#Module:    Log Utils
#Purpose:   Provide easy to use function calls for different levels of warnings

import bpy
from datetime import datetime

def get_log_file():
    """
    Retrieve the Blender internal text block used for logging. If it does not exist, create it.
    Returns:
        bpy.types.Text: The log text block.
    """
    log_file_name = "X-Plane Extensions Log.txt"

    log_text = bpy.data.texts.get(log_file_name)
    if log_text is None:
        log_text = bpy.data.texts.new(log_file_name)

    return log_text

def info(message):
    """
    Log an informational (verbose) message to the Blender internal log text block, with a timestamp.
    Args:
        message (str): The message to log.
    """
    log = get_log_file()

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    msg = current_time + " [VERBOSE] " + message + "\n"

    log.write(msg)

def warning(message):
    """
    Log a warning message to the Blender internal log text block, with a timestamp.
    Args:
        message (str): The warning message to log.
    """
    log = get_log_file()

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    msg = current_time + " [WARNING] " + message + "\n"

    log.write(msg)

def error(message):
    """
    Log an error message to the Blender internal log text block, with a timestamp.
    Args:
        message (str): The error message to log.
    """
    log = get_log_file()

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    msg = current_time + " [ERROR] " + message + "\n"

    log.write(msg)

def new_section(name):
    """
    Write a new section header to the Blender internal log text block, with a timestamp.
    Args:
        name (str): The name of the new log section.
    """
    log = get_log_file()

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    sides = "--------------------"

    msg = sides + " " + name + " On: " + current_time + " " + sides + "\n"

    log.write(msg)