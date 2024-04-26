import os
import importlib.util
import bpy
from bpy.types import Node, GeometryNodeTree, Operator, Menu
from bpy.props import StringProperty, FloatProperty

current_dir = os.path.dirname(os.path.abspath(__file__))

module_name_1 = "NodeSearch"  # Name of the module you want to import
module_file_1 = module_name_1 + ".py"
module_path_1 = os.path.join(current_dir, module_file_1)

# Load the module
spec_1 = importlib.util.spec_from_file_location(module_name_1, module_path_1)
ns = importlib.util.module_from_spec(spec_1)
spec_1.loader.exec_module(ns)

class NODE_FORM_GNT_Node_Form_Tree(GeometryNodeTree):

    """A container for handling custom nodes."""
    bl_idname = "node_form.node_form_tree"
    bl_label = "Node Form Tree"
    bl_icon = 'NODETREE'

    @classmethod
    def poll(cls, ntree):
        return hasattr(ntree, 'bl_idname') and ntree.bl_idname == "node_form.node_form_tree"

class NODE_FORM_NT_Start_Node(Node):
    bl_idname = 'node_form.start_node'
    bl_label = "Start Node"
    bl_icon = 'PLAY'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Sequence Start")

    def draw_buttons(self, context, layout):
        layout.operator("node_form.start_button", text="Run All Paths")
        layout.menu('node_form.start_node_menu', text='Add Node')

class NODE_FORM_NT_Selector_Node(Node):

    bl_idname = 'node_form.selector_node'
    bl_label = "Selector Node"

    automation_type: StringProperty(default='SLT')

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "") 
        self.inputs.new('NodeSocketFloat', "")

class NODE_FORM_NT_Deleter_Node(Node):

    bl_idname = 'node_form.deleter_node'
    bl_label = "Deleter Node"

    automation_type: StringProperty(default='DEL')

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "") 
        self.inputs.new('NodeSocketFloat', "")

class NODE_FORM_NT_Gridder_Node(Node):

    bl_idname = 'node_form.gridder_node'
    bl_label = "Gridder Node"

    automation_type: StringProperty(default='GRD')
    x_offset = FloatProperty(default=0)
    y_offset = FloatProperty(default=0)
    z_offset = FloatProperty(default=0)
    x_length = FloatProperty(default=1)
    y_length = FloatProperty(default=1)
    z_length = FloatProperty(default=1)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "") 
        self.inputs.new('NodeSocketFloat', "")

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self.x_offset)
        col.prop(self.y_offset)
        col.prop(self.z_offset)
        col = layout.column()
        col.prop(self.x_length)
        col.prop(self.y_length)
        col.prop(self.z_length)

class NODE_FORM_MT_Start_Node_Menu(Menu):

    bl_label = "Start Node Menu"
    bl_idname = "node_form.start_node_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('node_form.create_selector_node', text="Create Selector Node")
        layout.operator('node_form.create_deleter_node', text="Create Deleter Node")
        layout.operator('node_form.create_gridder_node', text="Create Gridder Node")

class NODE_FORM_OT_Start_Button(Operator):
    """Operator to find and display all downstream nodes from the selected node."""
    bl_idname = "node_form.start_button"
    bl_label = "Start Button"
    
    def execute(self, context):

        node_form_object = bpy.data.objects.get('Node Form')

        node_form_object.hide_viewport = True
        
        node_tree = bpy.data.node_groups.get('Node Form')
        
        if node_tree is None:
            print("Node tree 'Node Form' not found.")
            return {'CANCELLED'}

        start_node = next((node for node in node_tree.nodes if node.name == 'Start Node'), None)

        if start_node is None:
            print("Node 'Start Node' not found in 'Node Form'.")
            return {'CANCELLED'}

        ns.execute_all_paths(start_node)

        node_form_object.hide_viewport = True
        bpy.context.view_layer.objects.active = node_form_object

        return {'FINISHED'}

class NODE_FORM_OT_Create_Selector_Node(Operator):
    
    bl_label = "Create Selector Node"
    bl_idname = "node_form.create_selector_node"

    def execute(self, context):
        node_tree = find_node_form_tree()
        if node_tree:
            start_node = node_tree.nodes.new('node_form.selector_node')
            start_node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Deleter_Node(Operator):
    
    bl_label = "Create Deleter Node"
    bl_idname = "node_form.create_deleter_node"

    def execute(self, context):
        node_tree = find_node_form_tree()
        if node_tree:
            start_node = node_tree.nodes.new('node_form.deleter_node')
            start_node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Gridder_Node(Operator):
    
    bl_label = "Create Gridder Node"
    bl_idname = "node_form.create_gridder_node"

    def execute(self, context):
        node_tree = find_node_form_tree()
        if node_tree:
            start_node = node_tree.nodes.new('node_form.gridder_node')
            start_node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

def find_node_form_tree():

    node_tree = None
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "node_form.node_form_tree":
            return tree

    if not node_tree:
        self.report({'ERROR'}, "No Node Form Tree found")
        return None
    
registrars = [NODE_FORM_GNT_Node_Form_Tree,
              NODE_FORM_NT_Start_Node, NODE_FORM_NT_Selector_Node, NODE_FORM_NT_Deleter_Node,
              NODE_FORM_MT_Start_Node_Menu,
              NODE_FORM_OT_Start_Button, NODE_FORM_OT_Create_Selector_Node, NODE_FORM_OT_Create_Deleter_Node]

def register_ng():
    for nodeclass in registrars:
        bpy.utils.register_class(nodeclass)

def unregister_ng():
    for nodeclass in registrars:
        bpy.utils.unregister_class(nodeclass)