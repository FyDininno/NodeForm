import os
import importlib.util
import bpy
from bpy.types import Node, GeometryNodeTree, Operator, Menu, PropertyGroup, Scene
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty

current_dir = os.path.dirname(os.path.abspath(__file__))

module_name = "NodeSearch"  # Name of the module you want to import
module_file = module_name + ".py"
module_path = os.path.join(current_dir, module_file)

# Load the module
spec = importlib.util.spec_from_file_location(module_name, module_path)
ns = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ns)

class NODE_FORM_PG_Dictionary_Property_Group(PropertyGroup):
    variable: StringProperty()
    replacement: StringProperty()

class NODE_FORM_PG_Library_Property_Group(PropertyGroup):
    library_name: StringProperty()    

class NODE_FORM_PG_Filepath_Property_Group(PropertyGroup):
    filepath_name: StringProperty()
    module_name: StringProperty()

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
    bl_label = "Start"
    bl_icon = 'PLAY'

    automation_type: StringProperty(default='SRT')

    def init(self, context):
        self.outputs.new('NodeSocketVirtual', "Any")
        self.inputs.new('NodeSocketVirtual', "Library/Dictionary")

    def draw_buttons(self, context, layout):
        layout.operator("node_form.start_button", text="Run All Paths")
        layout.menu('NODE_FORM_MT_start_node_menu', text='Add Node')
        layout.menu('NODE_FORM_MT_start_node_preset_menu', text='Choose Preset')

class NODE_FORM_NT_Select_Node(Node):

    bl_idname = 'node_form.select_node'
    bl_label = "Select"

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
        self.outputs.new('NodeSocketVirtual', "")
        self.inputs.new('NodeSocketVirtual', "")

    def draw_buttons(self, context, layout):
        layout.prop(self, "selection_mode", text='')
        if self.selection_mode in ['SBN','DSBN']:
            layout.prop(self, 'selection_name', text='')

class NODE_FORM_NT_Delete_Node(Node):

    bl_idname = 'node_form.delete_node'
    bl_label = "Delete"

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
        self.outputs.new('NodeSocketVirtual', "")
        self.inputs.new('NodeSocketVirtual', "")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "deletion_mode", text='')

class NODE_FORM_NT_Grid_Create_Node(Node):

    bl_idname = 'node_form.grid_create_node'
    bl_label = "Grid Create"

    automation_type: StringProperty(default='GRD')

    x_offset: StringProperty(default='0')
    y_offset: StringProperty(default='0')
    z_offset: StringProperty(default='0')
    x_length: StringProperty(default='1')
    y_length: StringProperty(default='1')
    z_length: StringProperty(default='1')
    cube_density_x: StringProperty(default='2')
    cube_density_y: StringProperty(default='2')
    cube_density_z: StringProperty(default='2')

    is_hollow: BoolProperty(default=False)

    def init(self, context):
        self.outputs.new('NodeSocketVirtual', "")
        self.inputs.new('NodeSocketVirtual', "")

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
        row.label(text='Cube Density (x,y,z)')
        row = layout.row()
        row.prop(self, 'cube_density_x', text='')
        row.prop(self, 'cube_density_y', text='')
        row.prop(self, 'cube_density_z', text='')
        row=layout.row()
        row.prop(self, 'is_hollow', text='Hollow')

class NODE_FORM_NT_Transform_Node(Node):

    bl_idname = 'node_form.transform_node'
    bl_label = "Transform"

    automation_type: StringProperty(default='TFM')

    name: StringProperty()

    x_equation: StringProperty(default='x')
    y_equation: StringProperty(default='y')
    z_equation: StringProperty(default='z')
    
    animation_run_time: StringProperty(default='0')
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
            default='DELETE'
        )
    
    def init(self, context):
        self.outputs.new('NodeSocketVirtual', "")
        self.inputs.new('NodeSocketVirtual', "")
    
    def draw_buttons(self, context, layout):
        row = layout.row()
        row.prop(self, 'name', text="Operation Name")
        row = layout.row()
        row.prop(self, "x_equation", text='X(x,y,z,t,T) = ')
        row = layout.row()
        row.prop(self, "y_equation", text='Y(x,y,z,t,T) = ')
        row = layout.row()
        row.prop(self, "z_equation", text='Z(x,y,z,t,T) = ')
        row = layout.row()
        row.label(text='Run Time')
        row.label(text='Frame Sparseness')
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
    bl_label = "Dictionary"

    automation_type: StringProperty(default='DCT')
    variable_folder: CollectionProperty(type=NODE_FORM_PG_Dictionary_Property_Group)

    def init(self, context):
        self.inputs.new('NodeSocketVirtual', "Dictionary/Library")
        self.outputs.new('NodeSocketVirtual', "Start/Dictionary")

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
    bl_label = "Library Import"

    automation_type: StringProperty(default='LIB')
    variable_folder: CollectionProperty(type=NODE_FORM_PG_Library_Property_Group)

    def init(self, context):
        self.outputs.new('NodeSocketVirtual', "Start/Dictionary")
    
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

class NODE_FORM_NT_File_Import_Node(Node):
    bl_idname = 'node_form.file_import_node'
    bl_label = "File Import"

    automation_type: StringProperty(default='FIM')

    filepath_name: StringProperty()
    module_name: StringProperty()

    def init(self, context):
        self.outputs.new('NodeSocketVirtual', "")
        self.inputs.new('NodeSocketVirtual', "")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'filepath_name', text="File Path")
        layout.prop(self, 'module_name', text="Module Name")

class NODE_FORM_NT_Gate_Node(Node):
    
    bl_idname = 'node_form.gate_node'
    bl_label = "Gate"

    automation_type: StringProperty(default='GAT')

    allowed_to_pass: BoolProperty()
    
    def init(self, context):
        self.outputs.new('NodeSocketVirtual', "")
        self.inputs.new('NodeSocketVirtual', "")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'allowed_to_pass', text='Continue')

class NODE_FORM_NT_Execute_Node(Node):
    bl_idname = 'node_form.execute_node'
    bl_label = "Execute"

    automation_type: StringProperty(default='EXE')

    execution_code: StringProperty()

    def init(self, context):
        self.outputs.new('NodeSocketVirtual', "")
        self.inputs.new('NodeSocketVirtual', "")

    def draw_buttons(self, context, layout):
        layout.label(text = "Execute Code, Import Files, or Define Functions")
        row=layout.row()
        row.prop(self, 'execution_code', text="")


class NODE_FORM_OT_Create_Select_Node(Operator):
    
    bl_label = "Create Select Node"
    bl_idname = "node_form.create_select_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.select_node')
            node.location = (300, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Delete_Node(Operator):
    # Add an option to rename instead of delete or hide
    bl_label = "Create Delete Node"
    bl_idname = "node_form.create_delete_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.delete_node')
            node.location = (300, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Grid_Create_Node(Operator):
    
    bl_label = "Create Grid Create Node"
    bl_idname = "node_form.create_grid_create_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.grid_create_node')
            node.location = (300, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Transform_Node(Operator):
    
    bl_label = "Create Transform Node"
    bl_idname = "node_form.create_transform_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.transform_node')
            node.location = (300, 100)
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
            node.location = (300, 100)
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
            node.location = (300, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_File_Import_Node(Operator):
    bl_label = "Create File Import Node"
    bl_idname = "node_form.create_file_import_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.file_import_node')
            node.location = (300, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}



class NODE_FORM_OT_Create_Gate_Node(Operator):
    bl_label = "Create Gate Node"
    bl_idname = "node_form.create_gate_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.gate_node')
            node.location = (300, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}

class NODE_FORM_OT_Create_Execute_Node(Operator):
    bl_label = "Create Execute Node"
    bl_idname = "node_form.create_execute_node"

    def execute(self, context):
        node_tree = ns.get_node_form_tree()
        if node_tree:
            node = node_tree.nodes.new('node_form.execute_node')
            node.location = (300, 100)
            return{'FINISHED'}
        else:
            return{'ERROR'}


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

        start_node = next((node for node in node_tree.nodes if node.name == 'Start'), None)

        if start_node is None:
            print("Node 'Start Node' not found in 'Node Form'.")
            return {'CANCELLED'}

        ns.execute_all_paths(start_node)

        node_form_object.hide_viewport = True
        bpy.context.view_layer.objects.active = node_form_object

        return {'FINISHED'}

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
            
            grid_create_node = node_tree.nodes.new('node_form.grid_create_node')
            grid_create_node.location = (300, 100)
            grid_create_node.x_length = '1'
            grid_create_node.y_length = '2*[pi]'
            grid_create_node.z_length = '[pi]'

            transform_node = node_tree.nodes.new('node_form.transform_node')
            transform_node.location = (300, 100)
            transform_node.x_equation = "r*cos(φ)*sin(θ)"
            transform_node.y_equation = "r*sin(φ)*sin(θ)"
            transform_node.z_equation = "r*cos(θ)"

            node_tree.links.new(grid_create_node.outputs[0], transform_node.inputs[0])
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
            
            grid_create_node = node_tree.nodes.new('node_form.grid_create_node')
            grid_create_node.location = (300, 100)
            grid_create_node.x_length = '1'
            grid_create_node.y_length = '2*[pi]'
            grid_create_node.y_offset = '-[pi]'
            grid_create_node.z_length = '[pi]'
            grid_create_node.z_offset = '-[pi]/2'

            transform_node = node_tree.nodes.new('node_form.transform_node')
            transform_node.location = (300, 100)
            transform_node.x_equation = "r*cos(φ)*cos(θ)"
            transform_node.y_equation = "r*sin(φ)*cos(θ)"
            transform_node.z_equation = "r*sin(θ)"
            transform_node.transformation_type = 'SMOOTH'
            transform_node.animation_runtime = '2'

            node_tree.links.new(grid_create_node.outputs[0], transform_node.inputs[0])
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
            
            grid_create_node = node_tree.nodes.new('node_form.grid_create_node')
            grid_create_node.location = (300, 100)
            grid_create_node.x_length = '1'
            grid_create_node.y_length = '2*[pi]'
            grid_create_node.y_offset = '-[pi]'
            grid_create_node.z_length = '1'

            transform_node = node_tree.nodes.new('node_form.transform_node')
            transform_node.location = (300, 100)
            transform_node.x_equation = "r*cos(θ)"
            transform_node.y_equation = "r*sin(θ)"
            transform_node.z_equation = "z"

            node_tree.links.new(grid_create_node.outputs[0], transform_node.inputs[0])
            node_tree.links.new(dictionary_node.outputs[0], start_node.inputs[0])

            return{'FINISHED'}
        else:
            return{'ERROR'}


class NODE_FORM_MT_Start_Node_Menu(Menu):

    bl_label = "Start Node Menu"
    bl_idname = "NODE_FORM_MT_start_node_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('node_form.create_select_node', text="Create Select Node")
        layout.operator('node_form.create_delete_node', text="Create Delete Node")
        layout.operator('node_form.create_grid_create_node', text="Create Grid Node")
        layout.operator('node_form.create_transform_node', text="Create Transform Node")
        layout.operator('node_form.create_dictionary_node', text="Create Dictionary Node")
        layout.operator('node_form.create_library_import_node', text="Create Library Import Node")
        layout.operator('node_form.create_file_import_node', text="Create File Import Node")
        layout.operator('node_form.create_gate_node', text="Create Gate Node")
        layout.operator('node_form.create_execute_node', text="Create Execute Node")

class NODE_FORM_MT_Start_Node_Preset_Menu(Menu):
    bl_label = "Preset Menu"
    bl_idname = "NODE_FORM_MT_start_node_preset_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('node_form.create_spherical_preset', text="Create Spherical Parameterization")
        layout.operator('node_form.create_smooth_spherical_preset', text="Create Smooth Spherical Parameterization")
        layout.operator('node_form.create_cylindrical_preset', text="Create Cylindrical Parameterization")


registrars = [
    NODE_FORM_PG_Dictionary_Property_Group,
    NODE_FORM_PG_Library_Property_Group,
    NODE_FORM_PG_Filepath_Property_Group,
    NODE_FORM_GNT_Node_Form_Tree, 

    NODE_FORM_NT_Start_Node, 
    NODE_FORM_NT_Select_Node, 
    NODE_FORM_NT_Delete_Node, 
    NODE_FORM_NT_Grid_Create_Node,
    NODE_FORM_NT_Transform_Node,
    NODE_FORM_NT_Dictionary_Node,
    NODE_FORM_NT_Library_Import_Node,
    NODE_FORM_NT_Execute_Node,
    NODE_FORM_NT_File_Import_Node,
    NODE_FORM_NT_Gate_Node,

    NODE_FORM_OT_Create_Select_Node, 
    NODE_FORM_OT_Create_Delete_Node, 
    NODE_FORM_OT_Create_Grid_Create_Node,
    NODE_FORM_OT_Create_Transform_Node,
    NODE_FORM_OT_Create_Dictionary_Node,
    NODE_FORM_OT_Create_Library_Import_Node,
    NODE_FORM_OT_Create_Execute_Node,
    NODE_FORM_OT_Create_File_Import_Node,
    NODE_FORM_OT_Create_Gate_Node,

    NODE_FORM_OT_Create_Spherical_Preset,
    NODE_FORM_OT_Create_Smooth_Spherical_Preset,
    NODE_FORM_OT_Create_Cylindrical_Preset,

    NODE_FORM_OT_Start_Button,
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
    Scene.filepath_collection = CollectionProperty(type=NODE_FORM_PG_Filepath_Property_Group)

def unregister_ng():
    for nodeclass in registrars:
        bpy.utils.unregister_class(nodeclass)
    del Scene.replacement_dictionary
    del Scene.replacement_dictionary_is_updated
    del Scene.library_collection
    del Scene.filepath_collection