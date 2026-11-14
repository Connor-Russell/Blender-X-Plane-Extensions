
from bpy.app.handlers import persistent # type: ignore
import bpy


@persistent
def update_data_structures(unusued, unused):

    lsv_major = bpy.context.scene.xp_ext.last_save_plugin_version_major
    lsv_minor = bpy.context.scene.xp_ext.last_save_plugin_version_minor
    lsv_patch = bpy.context.scene.xp_ext.last_save_plugin_version_patch
    
    #1.0.1 update
    if (lsv_major <= 1 and lsv_minor <= 0 and lsv_patch < 1):
        #Get rid of old preview objects:
        old_attached_objs_to_remove = []
        for obj in bpy.data.objects:
            if "xp_ext_preview_object" in obj:
                old_attached_objs_to_remove.append(obj)
        for obj in old_attached_objs_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
