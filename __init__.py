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

import bpy
import bmesh
from mathutils import Vector, Matrix

class AlignEdgesOperator(bpy.types.Operator):
    bl_idname = "object.align_edges"
    bl_label = "Align Active Edge to X and Cross Vector to Z"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()

        if len(bm.select_history) != 2 or not all(isinstance(e, bmesh.types.BMEdge) for e in bm.select_history):
            self.report({'ERROR'}, "Please select exactly two edges")
            return {'CANCELLED'}

        # Identify the active edge and the other selected edge
        active_edge = bm.select_history.active if isinstance(bm.select_history.active, bmesh.types.BMEdge) else None
        other_edge = next((e for e in bm.select_history if e != active_edge), None)

        if not active_edge or not other_edge:
            self.report({'ERROR'}, "Could not determine the active and another selected edge correctly")
            return {'CANCELLED'}

        # Calculate vectors in world space
        mw = obj.matrix_world
        active_edge_vec = mw @ active_edge.verts[1].co - mw @ active_edge.verts[0].co
        other_edge_vec = mw @ other_edge.verts[1].co - mw @ other_edge.verts[0].co

        # Find the closest points between the two edges
        closest_pair = self.find_closest_points(active_edge.verts, other_edge.verts, mw)
        pivot_point = (closest_pair[0] + closest_pair[1]) / 2

        # Normalize vectors
        active_edge_vec.normalize()
        other_edge_vec.normalize()

        # Calculate the cross vector
        cross_vec = active_edge_vec.cross(other_edge_vec).normalized()

        # First, align cross vector to Z axis
        rot_to_z = cross_vec.rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4()

        # Move pivot to origin, apply rotation, and move back
        to_origin = Matrix.Translation(-pivot_point)
        from_origin = Matrix.Translation(pivot_point)
        obj.matrix_world = from_origin @ rot_to_z @ to_origin @ obj.matrix_world

        # Recalculate the active edge vector after the initial rotation
        updated_active_vec = rot_to_z @ active_edge_vec.normalized()

        # Second, align active edge vector to X axis
        rot_to_x = updated_active_vec.rotation_difference(Vector((1, 0, 0))).to_matrix().to_4x4()
        obj.matrix_world = from_origin @ rot_to_x @ to_origin @ obj.matrix_world

        return {'FINISHED'}

    def find_closest_points(self, verts1, verts2, world_matrix):
        min_distance = float('inf')
        closest_pair = (world_matrix @ verts1[0].co, world_matrix @ verts2[0].co)
        for v1 in verts1:
            for v2 in verts2:
                v1_world = world_matrix @ v1.co
                v2_world = world_matrix @ v2.co
                distance = (v1_world - v2_world).length
                if distance < min_distance:
                    min_distance = distance
                    closest_pair = (v1_world, v2_world)
        return closest_pair

    
if __name__ == "__main__":
    register()


def draw_menu(self, context):
    layout = self.layout
    layout.operator("object.store_transform")
    layout.operator("object.load_transform")

def register():
    bpy.utils.register_class(StoreTransform)
    bpy.utils.register_class(LoadTransform)
    bpy.utils.register_class(AlignEdgesOperator)
    bpy.types.VIEW3D_MT_object.append(draw_menu)
    bpy.types.Object.transform_storage = bpy.props.StringProperty()

def unregister():
    bpy.utils.unregister_class(StoreTransform)
    bpy.utils.unregister_class(LoadTransform)
    bpy.utils.unregister_class(AlignEdgesOperator)
    bpy.types.VIEW3D_MT_object.remove(draw_menu)
    del bpy.types.Object.transform_storage

if __name__ == "__main__":
    register()
