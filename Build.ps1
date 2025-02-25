#Define paths
$SourcePath = "A:\Code\Blender-X-Plane-Lin-Exporter\io_scene_xplane_ext"
$TargetPath = "C:\Users\cmrbu\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\io_scene_xplane_ext"

#Copy the source path to the target path, creating dirs if needed
Copy-Item -Path $SourcePath -Destination $TargetPath -Recurse -Force
