import os
import importlib.util

current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the module you want to import
module_name_1 = "SceneProcesses"  # Name of the module you want to import
module_file_1 = module_name_1 + ".py"
module_path_1 = os.path.join(current_dir, module_file_1)

# Load the module
spec_1 = importlib.util.spec_from_file_location(module_name_1, module_path_1)
sp = importlib.util.module_from_spec(spec_1)
spec_1.loader.exec_module(sp)

def return_all_paths(start_node):
    def visit(node, path):
        # If the node is already in the path, this path forms a loop. Return the path up to the current node.
        if node in path:
            return [path + [node]]

        # Extend the current path by including the current node
        extended_path = path + [node]
        paths = []  # This will collect all paths originating from this node

        # Check if the current node has outputs and they are linked to other nodes
        outputs = [output for output in node.outputs if output.is_linked]
        
        if outputs:
            # If outputs exist, recurse for each linked node
            for output in outputs:
                for link in output.links:
                    linked_node = link.to_node
                    paths.extend(visit(linked_node, extended_path))
        else:
            # If no outputs are linked, this is a terminal node. End this path here.
            paths.append(extended_path)

        return paths

    # Start the recursive visitation from the start_node
    return visit(start_node, [])

def list_output_nodes(input_node):
    
    outputs = [output for output in input_node.outputs if output.is_linked] if hasattr(input_node,'outputs') else None
    output_nodes = []

    if outputs:
            for output in outputs:
                for link in output.links:
                    linked_node = link.to_node
                    output_nodes.append(linked_node)

    return output_nodes

def execute_node(node):
    if hasattr(node, 'automation_type'):
        match getattr(node, 'automation_type'):
            case 'SLT':
                sp.bpy_select_all()
            case 'DEL':
                sp.bpy_delete_selected_objects()

def execute_all_paths(start_node):
    def run_path(input_node):
        for node in list_output_nodes(input_node):
            execute_node(node) # An if statement node might break this loop
            run_path(node) # It will travel down 1111 then 1112 then 1121 ...
    run_path(start_node)