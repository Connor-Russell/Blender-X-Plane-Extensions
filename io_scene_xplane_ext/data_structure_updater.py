
from bpy.app.handlers import persistent # type: ignore
from .Helpers import log_utils
from .__init__ import bl_info
import bpy


@persistent
def update_data_structures(unusued, unused):

    log_utils.new_section("Data Structure Update")

    lsv_major = bpy.context.scene.xp_ext.last_save_plugin_version_major
    lsv_minor = bpy.context.scene.xp_ext.last_save_plugin_version_minor
    lsv_patch = bpy.context.scene.xp_ext.last_save_plugin_version_patch

    cv_major = bl_info["version"][0]
    cv_minor = bl_info["version"][1]
    cv_patch = bl_info["version"][2]
    
    #1.0.1 update
    if (lsv_major <= 1 and lsv_minor <= 0 and lsv_patch < 1):
        log_utils.info(f"Updating from version {lsv_major}.{lsv_minor}.{lsv_patch} to {cv_major}.{cv_minor}.{cv_patch}")
        #Get rid of old preview objects:
        old_attached_objs_to_remove = []
        for obj in bpy.data.objects:
            if "xp_ext_preview_object" in obj:
                old_attached_objs_to_remove.append(obj)
        for obj in old_attached_objs_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
