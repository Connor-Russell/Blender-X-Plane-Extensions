#Define paths
$SourcePath = "A:\Code\Blender-X-Plane-Extensions\io_scene_xplane_ext"
$TargetPath = "C:\Users\cmrbu\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\io_scene_xplane_ext"
$TargetPath2 = "D:\Blender Versions\scripts\addons\io_scene_xplane_ext"

#Copy the source path to the target path, creating dirs if needed
Remove-Item -Path $TargetPath -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path $SourcePath -Destination $TargetPath -Recurse -Force
Remove-Item -Path $TargetPath2 -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path $SourcePath -Destination $TargetPath2 -Recurse -Force
