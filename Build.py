import shutil
import os
import sys

# Define paths
SourcePath = r"A:\Code\Blender-X-Plane-Extensions\io_scene_xplane_ext"
TargetPath = r"C:\Users\cmrbu\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\io_scene_xplane_ext"
TargetPath2 = r"D:\Blender Versions\scripts\addons\io_scene_xplane_ext"

# Remove target directories if they exist
for target in [TargetPath, TargetPath2]:
    if os.path.exists(target):
        shutil.rmtree(target, ignore_errors=True)

# Copy source to targets
for target in [TargetPath, TargetPath2]:
    shutil.copytree(SourcePath, target)

print("Build complete.")
