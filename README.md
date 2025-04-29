# X-Plane Blender Extensions
This Blender Plugin provides additional functionality for X-Plane projects in Blender. It's primary features include:
- WYSIWYG X-Plane Materials
- Facade Exporter
- Facade Importer (basic)
- Line Exporter
- Line Importer
- Object Importer (basic)

Additional features planned include:
- Polygon Exporter
- Polygon Importer
- Autogen Point Exporter with auto-splitting of multiple material objects into different .objs

Releases can be found on the release page. Alternatively, to get the latest version, clone the repository, and copy "io_scene_xplane_ext" into your Blender script folder.

# [X-Plane Materials](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Materials)

# [Facades](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Facades)

# [Lines](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Line)

# [Object Importer](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Object-Importing)

# Known issues:
- Decals are not imported for any formats
- Material importing may be incomplete
- Smooth normals do not import correctly when importing .objs
- Verticies are not deduped when exporting facades, resulting in potentially slightly higher VRAM usage on facades due to a few extra verticies
