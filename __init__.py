bl_info = {
    "name": "Transform Storage",
    "author": "tanitta",
    "blender": (4, 2, 0),
    "category": "Object",
}

def register():
    bpy.utils.register_class(StoreTransform)
    bpy.utils.register_class(LoadTransform)
    bpy.types.Object.transform_storage = bpy.props.StringProperty()

def unregister():
    bpy.utils.unregister_class(StoreTransform)
    bpy.utils.unregister_class(LoadTransform)
    del bpy.types.Object.transform_storage

if __name__ == "__main__":
    register()

import bpy
import json

class StoreTransform(bpy.types.Operator):
    """Store the current transform of all selected objects"""
    bl_idname = "object.store_transform"
    bl_label = "Store Transform"

    def execute(self, context):
        for obj in context.selected_objects:
            transform = {
                "location": list(obj.location),
                "rotation": list(obj.rotation_euler),
                "scale": list(obj.scale)
            }
            obj["transform_storage"] = json.dumps(transform)
        self.report({'INFO'}, "Transforms stored for {} objects".format(len(context.selected_objects)))
        return {'FINISHED'}

class LoadTransform(bpy.types.Operator):
    """Load the transforms from the custom properties of all selected objects"""
    bl_idname = "object.load_transform"
    bl_label = "Load Transform"

    def execute(self, context):
        for obj in context.selected_objects:
            if "transform_storage" in obj:
                transform = json.loads(obj["transform_storage"])
                obj.location = transform["location"]
                obj.rotation_euler = transform["rotation"]
                obj.scale = transform["scale"]
        self.report({'INFO'}, "Transforms loaded for {} objects".format(len(context.selected_objects)))
        return {'FINISHED'}

def draw_menu(self, context):
    layout = self.layout
    layout.operator("object.store_transform")
    layout.operator("object.load_transform")

def register():
    bpy.utils.register_class(StoreTransform)
    bpy.utils.register_class(LoadTransform)
    bpy.types.VIEW3D_MT_object.append(draw_menu)
    bpy.types.Object.transform_storage = bpy.props.StringProperty()

def unregister():
    bpy.utils.unregister_class(StoreTransform)
    bpy.utils.unregister_class(LoadTransform)
    bpy.types.VIEW3D_MT_object.remove(draw_menu)
    del bpy.types.Object.transform_storage

if __name__ == "__main__":
    register()
