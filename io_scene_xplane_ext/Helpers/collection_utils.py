#Project:   Blender-X-Plane-Extensions
#Author:    Connor Russell
#Date:      3/10/2025
#Module:    collection_helpers.py
#Purpose:   Provides functions for working with collections

import bpy  # type: ignore

def get_all_collections_from_view_layer(view_layer: bpy.types.ViewLayer) -> list:
    """
    Returns a list of all collections in the given view layer
    Args:
        view_layer (bpy.types.ViewLayer): The view layer to get collections from.
    Returns:
        list: A list of all collections in the view layer.
    Notes:
        - This is an function for get_collection_is_visible. Don't use directly!
    """

    in_output_layers = []

    def get_children(in_collection):
        """
        Recursively gets all children of a collection
        """
        for child in in_collection.children:
            if child.collection:
                in_output_layers.append(child)
                get_children(child)

    #Iterate through the children
    for child in view_layer.layer_collection.children:
        #If the child is a collection
        if child.collection:
            #Append the collection to the list
            in_output_layers.append(child)
            #Recursively call this function on the child
            get_children(child)

    return in_output_layers

def get_collection_is_visible(in_collection):
    """
    Returns True if the collection is visible in the viewport, False otherwise
    Args:
        in_collection (bpy.types.Collection): The collection to check.
    Returns:
        bool: True if the collection is visible in the viewport, False otherwise.
    Notes:
        This function is horribly unoptomized. It really needs to be refactored and thought out better than *hey it works*
    """
    #Get all collections from the current view layer
    collections = get_all_collections_from_view_layer(bpy.context.view_layer)

    #Iterate through the collections, check if it's name matches the input collection
    for col in collections:
        if col.name == in_collection.name:
            return not col.hide_viewport
        
    return False

def get_parent_collection(in_object: bpy.types.Object):
    """
    Returns the name of the parent collection for a given object
    """
    # Objects may belong to multiple collections; use the first membership
    # reported by Blender rather than scanning all collections in the scene.
    collections = in_object.users_collection
    if collections:
        return collections[0].name
    return None

def move_obj_to_same_collection(in_target: bpy.types.Object, in_parent: bpy.types.Object):
    """
    Moves the target object so it is in the same collection as the parent object
    """
    if in_target is in_parent:
        return

    # Objects may belong to multiple collections; use the parent's first
    # collection, consistent with get_parent_collection().
    parent_collections = in_parent.users_collection
    if not parent_collections:
        return

    destination = parent_collections[0]
    target_collections = list(in_target.users_collection)

    # Link before unlinking so the target remains in a collection throughout.
    if destination not in target_collections:
        destination.objects.link(in_target)

    for collection in target_collections:
        if collection != destination:
            collection.objects.unlink(in_target)