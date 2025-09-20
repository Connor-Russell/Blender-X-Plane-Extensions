#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      6/3/2025
#Module:    Log Utils
#Purpose:   Provide easy to use function calls for different levels of warnings

import bpy
from datetime import datetime

warning_count = 0
error_count = 0

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

    print(msg)  # Print to console for immediate feedback

    log.write(msg)

def warning(message):
    """
    Log a warning message to the Blender internal log text block, with a timestamp.
    Args:
        message (str): The warning message to log.
    """
    global warning_count
    warning_count += 1
    log = get_log_file()

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    msg = current_time + " [WARNING] " + message + "\n"

    print(msg)  # Print to console for immediate feedback

    log.write(msg)

def error(message):
    """
    Log an error message to the Blender internal log text block, with a timestamp.
    Args:
        message (str): The error message to log.
    """
    global error_count
    error_count += 1
    log = get_log_file()

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    msg = current_time + " [ERROR] " + message + "\n"

    print(msg)  # Print to console for immediate feedback

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

    msg = current_time + " " + sides + " " + name + " " + sides + "\n"

    print(msg)  # Print to console for immediate feedback

    log.write(msg)

def display_messages():
    """
    Display a popup message in Blender if there are any warnings or errors logged.
    This function is typically called after logging operations to inform the user.
    """
    global warning_count
    global error_count
    if warning_count > 0 or error_count > 0:
        message = f"{warning_count} warnings and {error_count} errors occured. Please check the \"X-Plane Extensions Log.txt\" in the text editor for details\n\n"

        def draw(self, context):
            self.layout.label(text=message)

        try:
            if not bpy.app.background and bpy.context.window is not None and bpy.context.area is not None:
                bpy.context.window_manager.popup_menu(draw, title = "Warnings/Errors Occured:", icon='ERROR')
            else:
                print("Popup not displayed: Blender is running in background mode or no active window/area. Message is: " + message)
        except Exception as e:
            print(f"Error displaying popup: {e}")
    
    warning_count = 0
    error_count = 0
