# X-Plane Blender Extensions
This Blender Plugin provides additional functionality for X-Plane projects in Blender. It's primary features include:
- WYSIWYG X-Plane Materials
- Facade Exporter
- Facade Importer (basic)
- Line Exporter
- Line Importer
- Object Importer (WIP, not all property data is imported, and animation hierarchy may be unexpected)

Additional features planned include:
- Autogen Point Exporter with auto-splitting of multiple material objects into different .objs

Releases can be found on the release page. To install, simply go to your Blender Settings, then addon, then choose install from file, and select "Blender X-Plane Extensions.zip".

# Documentation Quick Links:

### [X-Plane Materials](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Materials)

### [Facades](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Facades)

### [Lines](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Line)

### [Polygons](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Polygons)

### [Object Importer](https://github.com/Connor-Russell/Blender-X-Plane-Extensions/wiki/X%E2%80%90Plane-Object-Importing)

# Known issues:
- Decals are not imported for any formats
- Only the NORMAL_METALNESS material model is implemented. NORMAL_TRANSLUCENT and XP-10 style materials are not supported.
- Verticies are not deduped when exporting facades, resulting in potentially slightly higher VRAM usage on facades due to a few extra verticies
- Some object properties are not imported
