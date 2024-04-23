import bpy
from bpy.app.handlers import persistent
from bpy.types import NodeTree, Node, NodeSocket

bl_info = {
    "name": "Custom Geometry Node Automator",
    "blender": (2, 93, 0),
    "category": "Object",
    "description": "Automatically creates a custom node and a single vertex object for custom nodes",
    "author": "Your Name",
    "version": (1, 0),
    "location": "Node Editor",
}

class GenericNode(Node):
    """A custom node for user input."""
    bl_idname = 'GenericNodeType'
    bl_label = "Generic Node"
    bl_icon = 'SOUND'
    
    text_input: bpy.props.StringProperty(name="Input Text")

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Output Value")

    def draw_buttons(self, context, layout):
        layout.prop(self, "text_input", text="")

    def update(self):
        # Calculate something with self.text_input and set outputs
        self.outputs['Output Value'].default_value = len(self.text_input)

class GenericNodeTree(NodeTree):
    """A container for handling custom nodes."""
    bl_idname = 'GenericNodeTreeType'
    bl_label = "Custom Node Tree"
    bl_icon = 'NODETREE'

    @classmethod
    def poll(cls, ntree):
        return hasattr(ntree, 'bl_idname') and ntree.bl_idname == 'GeometryNodeTree'

@persistent
def check_for_automator_object(dummy):
    if "Automator" not in bpy.data.objects:
        # Create a new mesh data
        mesh = bpy.data.meshes.new("SingleVertex")
        mesh.from_pydata([(0,0,0)], [], [])
        mesh.update()
        
        # Create a new object based on the mesh data
        automator_object = bpy.data.objects.new("Automator", mesh)
        bpy.context.collection.objects.link(automator_object)
        bpy.context.view_layer.objects.active = automator_object
        automator_object.select_set(True)
        
        # Create a new Geometry Node tree and assign it to a new Geometry Nodes modifier
        node_tree = bpy.data.node_groups.new(name="AutomatorNodeTree", type='GeometryNodeTree')
        mod = automator_object.modifiers.new(name="GeometryNodes", type='NODES')
        mod.node_group = node_tree
        
        # Add the custom node to the newly created node tree
        generic_node = node_tree.nodes.new('GenericNodeType')
        generic_node.location = (100, 100)
        
        print("Automator object and custom node created.")
    else:
        print("Automator object already exists.")

def register():
    bpy.utils.register_class(GenericNode)
    bpy.utils.register_class(GenericNodeTree)
    bpy.app.handlers.load_post.append(check_for_automator_object)

def unregister():
    bpy.utils.unregister_class(GenericNode)
    bpy.utils.unregister_class(GenericNodeTree)
    bpy.app.handlers.load_post.remove(check_for_automator_object)

if __name__ == "__main__":
    register()
