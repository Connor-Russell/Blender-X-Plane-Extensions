import shutil
import os
import sys

# Define paths
plugin_name = "io_scene_xplane_ext"
source_path = os.getcwd() + os.sep + plugin_name
target_paths = []
target_paths.append(r"C:\Users\cmrbu\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons")
target_paths.append(r"D:\Blender Versions\scripts\addons")

# Remove target directories if they exist
for dir in target_paths:
    target = dir + os.sep + plugin_name
    if os.path.exists(target):
        shutil.rmtree(target, ignore_errors=True)

# Copy source to targets
for dir in target_paths:
    if os.path.exists(dir):
        target = dir + os.sep + plugin_name
        shutil.copytree(source_path, target, dirs_exist_ok=True)
        print(f"Copied {plugin_name} to {target}")

print("Build complete.")
