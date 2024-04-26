import bpy
import os
import importlib.util
from bpy.app.handlers import persistent

bl_info = {
    "name": "Node Form",
    "blender": (4, 00, 0),
    "category": "Object",
    "description": "",
    "author": "Frank Dininno",
    "version": (1, 0),
    "location": "Node Editor",
}

current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the module you want to import
module_name_1 = "NodeGroups"  # Name of the module you want to import
module_file_1 = module_name_1 + ".py"
module_path_1 = os.path.join(current_dir, module_file_1)

# Load the module
spec_1 = importlib.util.spec_from_file_location(module_name_1, module_path_1)
ng = importlib.util.module_from_spec(spec_1)
spec_1.loader.exec_module(ng)


@persistent
def check_for_automator_object(dummy):
    if "Node Form" not in bpy.data.objects:
        # Create a new mesh data
        mesh = bpy.data.meshes.new("SingleVertex")
        mesh.from_pydata([(0,0,0)], [], [])
        mesh.update()
        
        # Create a new object based on the mesh data
        automator_object = bpy.data.objects.new("Node Form", mesh)
        bpy.context.collection.objects.link(automator_object)
        bpy.context.view_layer.objects.active = automator_object
        automator_object.select_set(True)
        automator_object.hide_viewport = True
        
        # Create a new Automator Node Tree and assign it to a new Geometry Nodes modifier
        node_tree = bpy.data.node_groups.new(name="Node Form", type='node_form.node_form_tree')
        mod = automator_object.modifiers.new(name="GeometryNodes", type='NODES')
        mod.node_group = node_tree
        
        # Add the custom node to the newly created node tree
        start_node = node_tree.nodes.new('node_form.start_node')
        start_node.location = (100, 100)

        print("Node Form object and custom node created.")
    else:
        print("Node Form object already exists.")

def register():
    ng.register_ng()
    bpy.app.handlers.load_post.append(check_for_automator_object)

def unregister():
    ng.unregister_ng()
    bpy.app.handlers.load_post.remove(check_for_automator_object)