import os
import importlib.util
import bpy
from bpy.types import Node, GeometryNodeTree, Operator, Menu
from bpy.props import StringProperty, BoolProperty, EnumProperty

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
        self.outputs.new('NodeSocketColor', "")

    def draw_buttons(self, context, layout):
        layout.operator("node_form.start_button", text="Run All Paths")
        layout.menu('NODE_FORM_MT_start_node_menu', text='Add Node')
        layout.menu('NODE_FORM_MT_start_node_preset_menu', text='Choose Preset')

class NODE_FORM_NT_Merger_Node(Node):

    bl_idname = 'node_form.merger_node'
    bl_label = "Merger Node"

    automation_type: StringProperty(default='MRG')

    def init(self, context):
        self.outputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")

class NODE_FORM_NT_Selector_Node(Node):

    bl_idname = 'node_form.selector_node'
    bl_label = "Selector Node"

    automation_type: StringProperty(default='SLT')

    def init(self, context):
        self.outputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")

class NODE_FORM_NT_Deleter_Node(Node):

    bl_idname = 'node_form.deleter_node'
    bl_label = "Deleter Node"

    automation_type: StringProperty(default='DEL')

    def init(self, context):
        self.outputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")

class NODE_FORM_NT_Gridder_Node(Node):

    bl_idname = 'node_form.gridder_node'
    bl_label = "Gridder Node"

    automation_type: StringProperty(default='GRD')

    x_offset: StringProperty(default='0')
    y_offset: StringProperty(default='0')
    z_offset: StringProperty(default='0')
    x_length: StringProperty(default='1')
    y_length: StringProperty(default='1')
    z_length: StringProperty(default='1')
    cube_density: StringProperty(default='2')
    is_hollow: BoolProperty(default=False)

    def init(self, context):
        self.outputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.label(text='Offsets {x,y,z}')
        row.label(text='Lengths {x,y,z}')
        row = layout.row()
        row.prop(self, "x_offset", text='')
        row.prop(self, "x_length", text='')
        row = layout.row()
        row.prop(self, "y_offset", text='')
        row.prop(self, "y_length", text='')
        row = layout.row()
        row.prop(self, "z_offset", text='')
        row.prop(self, "z_length", text='')
        row = layout.row()
        row.label(text='Cube Density')
        row = layout.row()
        row.prop(self, 'cube_density', text='')
        row.prop(self, 'is_hollow', text='Hollow')

class NODE_FORM_NT_Transformer_Node(Node):

    bl_idname = 'node_form.transformer_node'
    bl_label = "Transformer Node"

    automation_type: StringProperty(default='TFM')

    x_variable: StringProperty(default='α')
    y_variable: StringProperty(default='β')
    z_variable: StringProperty(default='γ')
    x_equation: StringProperty(default='α = x')
    y_equation: StringProperty(default='β = y')
    z_equation: StringProperty(default='γ = z')
    
    animation_run_time: StringProperty(default='5')
    frames_per_calculation: StringProperty(default='2')
    repeats: StringProperty(default='0')

    transformation_type: EnumProperty(
            name="Tranformation Type",
            description="Choose an option",
            items=[
                ('REGULAR', "Regular Transformation", "Spatial coordinates will be transformed immediately (use if time, 't', is in your function)"),
                ('SMOOTH', "Smooth Tranformation", "Spatial coordinates will be smoothly interpolated (do not use for variables with negative exponents)"),
                ('LINEAR', "Linear Transformation", "Spatial coordinates will be linearly interpolated")
            ],
            default='REGULAR'
        )
    
    keep_option: EnumProperty(
            name="Keep Option",
            description="Choose an option",
            items=[
                ('HIDE', "Keep and Hide Original", "The original object will be kept but hidden"),
                ('KEEP', "Keep Original", "The original object will be kept and visible"),
                ('DELETE', "Delete Original", "The original object will be deleted")
            ],
            default='HIDE'
        )
    
    def init(self, context):
        self.outputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")
    
    def draw_buttons(self, context, layout):
        row = layout.row()
        row.label(text='Variables {x,y,z}new')
        row.label(text='Equations {x,y,z,t,T}')
        row = layout.row()
        row.prop(self, "x_variable", text='')
        row.prop(self, "x_equation", text='')
        row = layout.row()
        row.prop(self, "y_variable", text='')
        row.prop(self, "y_equation", text='')
        row = layout.row()
        row.prop(self, "z_variable", text='')
        row.prop(self, "z_equation", text='')
        row = layout.row()
        row.label(text='Run Time')
        row.label(text='Frame Density')
        row.label(text='Repetitions')
        row = layout.row()
        row.prop(self, "animation_run_time", text='')
        row.prop(self, "frames_per_calculation", text='')
        row.prop(self, "repeats", text='')
        row = layout.row()
        row.prop(self, "keep_option", text='')
        row.prop(self, "transformation_type", text='')

class NODE_FORM_MT_Start_Node_Menu(Menu):

    bl_label = "Start Node Menu"
    bl_idname = "NODE_FORM_MT_start_node_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('node_form.create_selector_node', text="Create Selector Node")
        layout.operator('node_form.create_merger_node', text="Create Merger Node")
        layout.operator('node_form.create_deleter_node', text="Create Deleter Node")
        layout.operator('node_form.create_gridder_node', text="Create Gridder Node")
        layout.operator('node_form.create_transformer_node', text="Create Transformer Node")

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
            node = node_tree.nodes.new('node_form.selector_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Merger_Node(Operator):
    
    bl_label = "Create Merger Node"
    bl_idname = "node_form.create_merger_node"

    def execute(self, context):
        node_tree = find_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.merger_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Deleter_Node(Operator):
    
    bl_label = "Create Deleter Node"
    bl_idname = "node_form.create_deleter_node"

    def execute(self, context):
        node_tree = find_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.deleter_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Gridder_Node(Operator):
    
    bl_label = "Create Gridder Node"
    bl_idname = "node_form.create_gridder_node"

    def execute(self, context):
        node_tree = find_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.gridder_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Transformer_Node(Operator):
    
    bl_label = "Create Transformer Node"
    bl_idname = "node_form.create_transformer_node"

    def execute(self, context):
        node_tree = find_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.transformer_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_MT_Start_Node_Preset_Menu(Menu):
    bl_label = "Preset Menu"
    bl_idname = "NODE_FORM_MT_start_node_preset_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('node_form.create_spherical_preset', text="Create Spherical Parameterization")


class NODE_FORM_OT_Create_Spherical_Preset(Operator):
    bl_label = "Create Spherical Parameterization"
    bl_idname = "node_form.create_spherical_preset"

    def execute(self, context):
        node_tree = find_node_form_tree()
        if node_tree:
            
            gridder_node = node_tree.nodes.new('node_form.gridder_node')
            gridder_node.location = (100, 100)

            transformer_node = node_tree.nodes.new('node_form.transformer_node')
            transformer_node.location = (300, 100)

            link = node_tree.links.new(gridder_node.outputs[0], transformer_node.inputs[0])

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
    
registrars = [
    NODE_FORM_GNT_Node_Form_Tree, 
    NODE_FORM_NT_Start_Node, 
    NODE_FORM_NT_Merger_Node,
    NODE_FORM_NT_Selector_Node, 
    NODE_FORM_NT_Deleter_Node, 
    NODE_FORM_NT_Gridder_Node,
    NODE_FORM_NT_Transformer_Node,
    NODE_FORM_MT_Start_Node_Menu,
    NODE_FORM_OT_Start_Button, 
    NODE_FORM_OT_Create_Selector_Node, 
    NODE_FORM_OT_Create_Merger_Node,
    NODE_FORM_OT_Create_Deleter_Node, 
    NODE_FORM_OT_Create_Gridder_Node,
    NODE_FORM_OT_Create_Transformer_Node,
    NODE_FORM_MT_Start_Node_Preset_Menu,
    NODE_FORM_OT_Create_Spherical_Preset,
    ]

def register_ng():
    for nodeclass in registrars:
        bpy.utils.register_class(nodeclass)

def unregister_ng():
    for nodeclass in registrars:
        bpy.utils.unregister_class(nodeclass)