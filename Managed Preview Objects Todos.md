#TODO:
# 1. On every attached preview object, set a property containing the relative path to the preview object
# 2. When updating a preview object, check the children for this property instead of hide_select and clear them, regardless of the current state of this object
# 3. When loading an object, instead of reloading it, check all other objects for this property, and just create a new obj and link obj data if we can find one
# 4. Every time we find or load an object, add it to a map of resource to uid and obj. Then we can lookup rapidly by resource, and validate the uid against existing objects
# 5. Make new file for depsgraph registration
# 6. Tie the auto update to prefs
# 7. Add a function to the update field of the resource/preview resource so changing that value triggers an update of the preview object