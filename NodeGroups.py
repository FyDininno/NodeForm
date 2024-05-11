import os
import importlib.util
import bpy
from bpy.types import Node, GeometryNodeTree, Operator, Menu, PropertyGroup, Scene
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty

current_dir = os.path.dirname(os.path.abspath(__file__))

module_name_1 = "NodeSearch"  # Name of the module you want to import
module_file_1 = module_name_1 + ".py"
module_path_1 = os.path.join(current_dir, module_file_1)

# Load the module
spec_1 = importlib.util.spec_from_file_location(module_name_1, module_path_1)
ns = importlib.util.module_from_spec(spec_1)
spec_1.loader.exec_module(ns)

class NODE_FORM_PG_Dictionary_Property_Group(PropertyGroup):
    variable: StringProperty()
    replacement: StringProperty()

class NODE_FORM_PG_Library_Property_Group(PropertyGroup):
    library_name: StringProperty()    

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

    automation_type: StringProperty(default='SRT')

    def init(self, context):
        self.outputs.new('NodeSocketColor', "Any")
        self.inputs.new('NodeSocketFloat', "Library/Dictionary")

    def draw_buttons(self, context, layout):
        layout.operator("node_form.start_button", text="Run All Paths")
        layout.menu('NODE_FORM_MT_start_node_menu', text='Add Node')
        layout.menu('NODE_FORM_MT_start_node_preset_menu', text='Choose Preset')

class NODE_FORM_NT_Selector_Node(Node):

    bl_idname = 'node_form.selector_node'
    bl_label = "Selector Node"

    automation_type: StringProperty(default='SLT')

    selection_mode: EnumProperty(
            name="Selection Mode",
            description="Choose an option",
            items=[
                ('SAL', "Select All", "All objects in the scene will be selected"),
                ('SBN', "Select By Name", "The object in the scene with the name will be selected"),
                ('DSAL', "Deselect All", "All objects in the scene will be deselected"),
                ('DSBN', "Deselect By Name", "The object in the scene with the name will be deselected"),
            ],
            default='SAL'
        )
    
    selection_name: StringProperty()

    def init(self, context):
        self.outputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")

    def draw_buttons(self, context, layout):
        layout.prop(self, "selection_mode", text='')
        if self.selection_mode in ['SBN','DSBN']:
            layout.prop(self, 'selection_name', text='')

class NODE_FORM_NT_Deleter_Node(Node):

    bl_idname = 'node_form.deleter_node'
    bl_label = "Deleter Node"

    automation_type: StringProperty(default='DEL')

    deletion_mode: EnumProperty(
            name="Deletion Mode",
            description="Choose an option",
            items=[
                ('DELETE', "Delete Selected", "The selected objects will be deleted"),
                ('HIDE', "Hide Selected", "The selected objects will be hidden"),
            ],
            default='DELETE'
        )

    def init(self, context):
        self.outputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "deletion_mode", text='')

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

    x_variable: StringProperty(default='X')
    y_variable: StringProperty(default='Y')
    z_variable: StringProperty(default='Z')
    x_equation: StringProperty(default='X = x')
    y_equation: StringProperty(default='Y = y')
    z_equation: StringProperty(default='Z = z')
    
    animation_run_time: StringProperty(default='5')
    frames_per_calculation: StringProperty(default='2')
    repeats: StringProperty(default='0')

    transformation_type: EnumProperty(
            name="Tranformation Type",
            description="Choose an option",
            items=[
                ('REGULAR', "Direct Parameterization", "Spatial coordinates will be transformed immediately (use if time, 't', is in your function)"),
                ('SMOOTH', "Delayed Coordinate Interpolation", "Spatial coordinates will be smoothly interpolated (do not use for variables with negative exponents)"),
                ('LINEAR', "Delayed Coordinate Slide", "Spatial coordinates will be linearly interpolated")
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
        row.label(text='Variables {x,y,z}(new)')
        row.label(text='Equations {x,y,z,t,T}(original)')
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

class NODE_FORM_NT_Dictionary_Node(Node):

    bl_idname = 'node_form.dictionary_node'
    bl_label = "Dictionary Node"

    automation_type: StringProperty(default='DCT')
    variable_folder: CollectionProperty(type=NODE_FORM_PG_Dictionary_Property_Group)

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Dictionary/Library")
        self.outputs.new('NodeSocketFloat', "Start/Dictionary")

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.operator('node_form.folder_node_add_button', icon='PLUS', text="Add New")
        row = layout.row()
        row.label(text="Variable")
        row.label(text="Replacement")
        for i, item in enumerate(self.variable_folder):
            row = layout.row()
            row.prop(item, "variable", text="")
            row.prop(item, "replacement", text="")
            down_button = row.operator("node_form.folder_node_down_button", icon="TRIA_DOWN", text="")
            up_button = row.operator("node_form.folder_node_up_button", icon="TRIA_UP", text="")
            delete_button = row.operator("node_form.folder_node_delete_button", icon="X", text="")
            down_button.index = i
            up_button.index = i
            delete_button.index = i

class NODE_FORM_NT_Library_Import_Node(Node):

    bl_idname = 'node_form.library_import_node'
    bl_label = "Library Import Node"

    automation_type: StringProperty(default='LIB')
    variable_folder: CollectionProperty(type=NODE_FORM_PG_Library_Property_Group)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Start/Dictionary")
    
    def draw_buttons(self, context, layout):
        row = layout.row()
        row.operator('node_form.folder_node_add_button', icon='PLUS', text="Add New")
        row = layout.row()
        row.label(text="Library Name")
        for i, item in enumerate(self.variable_folder):
            row = layout.row()
            row.prop(item, "library_name", text="")
            down_button = row.operator("node_form.folder_node_down_button", icon="TRIA_DOWN", text="")
            up_button = row.operator("node_form.folder_node_up_button", icon="TRIA_UP", text="")
            delete_button = row.operator("node_form.folder_node_delete_button", icon="X", text="")
            down_button.index = i
            up_button.index = i
            delete_button.index = i

class NODE_FORM_NT_Merger_Node(Node):

    bl_idname = 'node_form.merger_node'
    bl_label = "Merger Node"

    automation_type: StringProperty(default='MRG')

    def init(self, context):
        self.outputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")
        self.inputs.new('NodeSocketColor', "")


class NODE_FORM_OT_Start_Button(Operator):
    bl_idname = "node_form.start_button"
    bl_label = "Start Button"
    
    def execute(self, context):

        setattr(bpy.context.scene, 'replacement_dictionary_is_updated', True)

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
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.selector_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Deleter_Node(Operator):
    
    bl_label = "Create Deleter Node"
    bl_idname = "node_form.create_deleter_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
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
        node_tree = ns.get_node_form_tree()
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
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.transformer_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Dictionary_Node(Operator):
    bl_label = "Create Dictionary Node"
    bl_idname = "node_form.create_dictionary_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.dictionary_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Library_Import_Node(Operator):

    bl_label = "Create Library Import Node"
    bl_idname = "node_form.create_library_import_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.library_import_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Merger_Node(Operator):
    
    bl_label = "Create Merger Node"
    bl_idname = "node_form.create_merger_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.merger_node')
            node.location = (100, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}


class NODE_FORM_OT_Folder_Node_Down_Button(Operator):

    bl_label = "Dictionary Node Down Button"
    bl_idname = "node_form.folder_node_down_button"

    index: IntProperty()

    def execute(self, context):
        node = context.node
        try:
            node.variable_folder.move(self.index, self.index+1)
            return {'FINISHED'}
        except IndexError:
            return {'INDEX ERROR'}

class NODE_FORM_OT_Folder_Node_Up_Button(Operator):
    bl_label = "Dictionary Node Up Button"
    bl_idname = "node_form.folder_node_up_button"

    index: IntProperty()

    def execute(self, context):
        node = context.node
        node = context.node
        try:
            node.variable_folder.move(self.index, self.index-1)
            return {'FINISHED'}
        except IndexError:
            return {'INDEX ERROR'}

class NODE_FORM_OT_Folder_Node_Delete_Button(Operator):
    bl_label = "Dictionary Node Delete Button"
    bl_idname = "node_form.folder_node_delete_button"

    index: IntProperty()

    def execute(self, context):
        node = context.node
        try:
            node.variable_folder.remove(self.index)
            return {'FINISHED'}
        except IndexError:
            return {'INDEX ERROR'}

class NODE_FORM_OT_Folder_Node_Add_Button(Operator):
    bl_label = "Dictionary Node Add Button"
    bl_idname = "node_form.folder_node_add_button"

    def execute(self, context):
        node = context.node
        node.variable_folder.add()
        return {'FINISHED'}


class NODE_FORM_OT_Create_Spherical_Preset(Operator):
    bl_label = "Create Spherical Parameterization"
    bl_idname = "node_form.create_spherical_preset"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            start_node = ns.get_start_node()

            dictionary_node = node_tree.nodes.new('node_form.dictionary_node')
            dictionary_node.location = (-100, 100)
            radius = dictionary_node.variable_folder.add()
            radius.variable = 'r'
            radius.replacement = 'x'
            phi = dictionary_node.variable_folder.add()
            phi.variable = 'φ'
            phi.replacement = 'y'
            theta = dictionary_node.variable_folder.add()
            theta.variable = 'θ'
            theta.replacement = 'z'
            
            gridder_node = node_tree.nodes.new('node_form.gridder_node')
            gridder_node.location = (100, 100)
            gridder_node.x_length = '1'
            gridder_node.y_length = '2*pi'
            gridder_node.z_length = 'pi'

            transformer_node = node_tree.nodes.new('node_form.transformer_node')
            transformer_node.location = (300, 100)
            transformer_node.x_equation = "X = r*cos(φ)*sin(θ)"
            transformer_node.y_equation = "Y = r*sin(φ)*sin(θ)"
            transformer_node.z_equation = "Z = r*cos(θ)"

            node_tree.links.new(gridder_node.outputs[0], transformer_node.inputs[0])
            node_tree.links.new(dictionary_node.outputs[0], start_node.inputs[0])

            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Smooth_Spherical_Preset(Operator):
    bl_label = "Create Smooth Spherical Parameterization"
    bl_idname = "node_form.create_smooth_spherical_preset"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            start_node = ns.get_start_node()
            
            dictionary_node = node_tree.nodes.new('node_form.dictionary_node')
            dictionary_node.location = (-100, 100)
            radius = dictionary_node.variable_folder.add()
            radius.variable = 'r'
            radius.replacement = 'x'
            phi = dictionary_node.variable_folder.add()
            phi.variable = 'φ'
            phi.replacement = 'y'
            theta = dictionary_node.variable_folder.add()
            theta.variable = 'θ'
            theta.replacement = 'z'
            
            gridder_node = node_tree.nodes.new('node_form.gridder_node')
            gridder_node.location = (100, 100)
            gridder_node.x_length = '1'
            gridder_node.y_length = '2*pi'
            gridder_node.y_offset = '-pi'
            gridder_node.z_length = 'pi'
            gridder_node.z_offset = '-pi/2'

            transformer_node = node_tree.nodes.new('node_form.transformer_node')
            transformer_node.location = (300, 100)
            transformer_node.x_equation = "X = r*cos(φ)*cos(θ)"
            transformer_node.y_equation = "Y = r*sin(φ)*cos(θ)"
            transformer_node.z_equation = "Z = r*sin(θ)"
            transformer_node.transformation_type = 'SMOOTH'

            node_tree.links.new(gridder_node.outputs[0], transformer_node.inputs[0])
            node_tree.links.new(dictionary_node.outputs[0], start_node.inputs[0])

            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Cylindrical_Preset(Operator):
    bl_label = "Create Cylindrical Parameterization"
    bl_idname = "node_form.create_cylindrical_preset"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            start_node = ns.get_start_node()
            
            dictionary_node = node_tree.nodes.new('node_form.dictionary_node')
            dictionary_node.location = (-100, 100)
            radius = dictionary_node.variable_folder.add()
            radius.variable = 'r'
            radius.replacement = 'x'
            theta = dictionary_node.variable_folder.add()
            theta.variable = 'θ'
            theta.replacement = 'y'
            
            gridder_node = node_tree.nodes.new('node_form.gridder_node')
            gridder_node.location = (100, 100)
            gridder_node.x_length = '1'
            gridder_node.y_length = 'pi'
            gridder_node.y_offset = '-pi/2'
            gridder_node.z_length = '1'

            transformer_node = node_tree.nodes.new('node_form.transformer_node')
            transformer_node.location = (300, 100)
            transformer_node.x_equation = "X = r*cos(θ)"
            transformer_node.y_equation = "Y = r*sin(θ)"
            transformer_node.z_equation = "Z = z"

            node_tree.links.new(gridder_node.outputs[0], transformer_node.inputs[0])
            node_tree.links.new(dictionary_node.outputs[0], start_node.inputs[0])

            return{'FINISHED'}
        else:
            return{'ERROR'}


class NODE_FORM_MT_Start_Node_Menu(Menu):

    bl_label = "Start Node Menu"
    bl_idname = "NODE_FORM_MT_start_node_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('node_form.create_selector_node', text="Create Selector Node")
        layout.operator('node_form.create_deleter_node', text="Create Deleter Node")
        layout.operator('node_form.create_gridder_node', text="Create Gridder Node")
        layout.operator('node_form.create_transformer_node', text="Create Transformer Node")
        layout.operator('node_form.create_dictionary_node', text="Create Dictionary Node")
        layout.operator('node_form.create_library_import_node', text="Create Library Import Node")
        layout.operator('node_form.create_merger_node', text="Create Merger Node")

class NODE_FORM_MT_Start_Node_Preset_Menu(Menu):
    bl_label = "Preset Menu"
    bl_idname = "NODE_FORM_MT_start_node_preset_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('node_form.create_spherical_preset', text="Create Spherical Parameterization")
        layout.operator('node_form.create_smooth_spherical_preset', text="Create Smooth Spherical Parameterization")
        layout.operator('node_form.create_cylindrical_preset', text="Create Cylindrical Parameterization")


temp_variables = []

def delete_temporary_variables():
    for pg in temp_variables:
        del pg


registrars = [
    NODE_FORM_PG_Dictionary_Property_Group,
    NODE_FORM_PG_Library_Property_Group,
    NODE_FORM_GNT_Node_Form_Tree, 
    NODE_FORM_NT_Start_Node, 
    NODE_FORM_NT_Merger_Node,
    NODE_FORM_NT_Selector_Node, 
    NODE_FORM_NT_Deleter_Node, 
    NODE_FORM_NT_Gridder_Node,
    NODE_FORM_NT_Transformer_Node,
    NODE_FORM_NT_Dictionary_Node,
    NODE_FORM_NT_Library_Import_Node,
    NODE_FORM_OT_Start_Button, 
    NODE_FORM_OT_Create_Selector_Node, 
    NODE_FORM_OT_Create_Merger_Node,
    NODE_FORM_OT_Create_Deleter_Node, 
    NODE_FORM_OT_Create_Gridder_Node,
    NODE_FORM_OT_Create_Transformer_Node,
    NODE_FORM_OT_Create_Dictionary_Node,
    NODE_FORM_OT_Create_Library_Import_Node,
    NODE_FORM_OT_Create_Spherical_Preset,
    NODE_FORM_OT_Create_Smooth_Spherical_Preset,
    NODE_FORM_OT_Create_Cylindrical_Preset,
    NODE_FORM_OT_Folder_Node_Add_Button,
    NODE_FORM_OT_Folder_Node_Delete_Button,
    NODE_FORM_OT_Folder_Node_Up_Button,
    NODE_FORM_OT_Folder_Node_Down_Button,
    NODE_FORM_MT_Start_Node_Menu,
    NODE_FORM_MT_Start_Node_Preset_Menu,
    ]

def register_ng():
    for nodeclass in registrars:
        bpy.utils.register_class(nodeclass)
    Scene.replacement_dictionary = CollectionProperty(type=NODE_FORM_PG_Dictionary_Property_Group)
    Scene.replacement_dictionary_is_updated = BoolProperty(default=True) #This is the parent object. context.scene is the instance running in the blender folder
    Scene.library_collection = CollectionProperty(type=NODE_FORM_PG_Library_Property_Group)

def unregister_ng():
    for nodeclass in registrars:
        bpy.utils.unregister_class(nodeclass)
    del Scene.replacement_dictionary
    del Scene.replacement_dictionary_is_updated
    del Scene.library_collection

    delete_temporary_variables()