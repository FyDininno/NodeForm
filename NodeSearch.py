import os
import importlib
import math
import bpy
import re
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the module you want to import
module_name = "NodeMechanics"  # Name of the module you want to import
module_file = module_name + ".py"
module_path = os.path.join(current_dir, module_file)

# Load the module
spec = importlib.util.spec_from_file_location(module_name, module_path)
nm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nm)

def update_replacement_dictionary():

    bpy.context.scene.replacement_dictionary.clear()
    bpy.context.scene.library_collection.clear()
    bpy.context.scene.filepath_collection.clear()

    replacement_dictionary = get_replacement_dictionary()

    for path in get_back_paths(get_start_node()):

        path_dictionary = {}

        for node in path:

            if node.automation_type =='DCT': 

                temporary_dicationary={}
                var_folder = node.variable_folder

                for i in range(len(var_folder)):

                    temporary_dicationary[var_folder[i].variable] = var_folder[i].replacement

                temporary_dicationary = substitute_keys_into_values(path_dictionary, temporary_dicationary)

                append_unique_keys(path_dictionary, temporary_dicationary)

            elif node.automation_type == 'LIB':

                var_folder = node.variable_folder

                for library in var_folder:
                    bpy.context.scene.library_collection.add().library_name = library.library_name
            
            elif node.automation_type == 'FIM':
                filepath_element = bpy.context.scene.filepath_collection.add()
                filepath_element.filepath_name = node.filepath_name
                filepath_element.module_name = node.module_name

            elif node.automation_type != 'SRT':
                print('Invalid Library or Dictionary Connection')

        replacement_dictionary = append_unique_keys(replacement_dictionary, path_dictionary)
        set_replacement_dictionary(replacement_dictionary)

def execute_node(node):

    if bpy.context.scene.replacement_dictionary_is_updated:
        update_replacement_dictionary()
        bpy.context.scene.replacement_dictionary_is_updated = False

    if hasattr(node, 'automation_type'):
        
        match getattr(node, 'automation_type'):
            
            case 'GAT':
                if not node.allowed_to_pass:
                    return 'BREAK'

            case 'SLT':
                match node.selection_mode:
                    case 'SAL':
                        nm.bpy_select_all()
                    case 'SBN':
                        nm.bpy_select_by_name(node.selection_name)
                    case 'DSAL':
                        nm.bpy_deselect_all()
                    case 'DSBN':
                        nm.bpy_deselect_by_name(node.selection_name)

            case 'DEL':
                if node.deletion_mode == 'DELETE':
                    nm.bpy_delete_selected_objects()
                elif node.deletion_mode == 'HIDE':
                    nm.bpy_hide_selected_objects()

            case 'GRD':
                evaluated_strings = nm.safe_evaluation(
                    substitute_keys_into_strings(get_replacement_dictionary(), [
                                        node.x_length,
                                        node.y_length,
                                        node.z_length,
                                        node.x_offset,
                                        node.y_offset,
                                        node.z_offset,
                                        node.cube_density_x,
                                        node.cube_density_y,
                                        node.cube_density_z,
                                    ]))
                
                lengths_vector = evaluated_strings[0:3]
                offset_vector = evaluated_strings[3:6]
                cube_density_vector = evaluated_strings[6:9]
                
                nm.grid(lengths_vector, offset_vector, cube_density_vector)
                
                if node.is_hollow:
                    nm.hollow_grid(offset_vector, lengths_vector, cube_density_vector)

            case 'TFM':
                
                variables = substitute_keys_into_strings(get_replacement_dictionary(),[
                    node.x_equation,
                    node.y_equation,
                    node.z_equation,
                ])

                evaluated_strings = nm.safe_evaluation(
                    substitute_keys_into_strings(get_replacement_dictionary(),[
                                        node.animation_run_time,
                                        node.frames_per_calculation,
                                        node.repeats,
                                    ]))
                
                equations_vector = variables[0:3]
                animation_run_time = evaluated_strings[0]
                frames_per_clculation = evaluated_strings[1]
                repeats = evaluated_strings[2]
                transformation_type = node.transformation_type
                keep_option = node.keep_option

                nm.transform(
                    equations_vector,
                    animation_run_time,
                    frames_per_clculation,
                    repeats,
                    transformation_type,
                    keep_option,
                )

            case 'EXE':
                final_execution_code = substitute_keys_into_strings(get_replacement_dictionary(), node.execution_code)
                exec(final_execution_code)

def substitute_keys_into_values(target, modifier):
    # Result dictionary that will store updated key-value pairs
    result = {}
    
    # Iterate through each key and value in dic2
    for key, value in modifier.items():
        # Initialize the modified value as the original value
        modified_value = value
        
        # Check for each key in dic1 if it is a substring of the value in dic2
        for sub_key, sub_value in target.items():
            # Replace the occurrence of dic1's key in dic2's value
            modified_value = modified_value.replace(sub_key, sub_value)
        
        # Store the modified value in the result dictionary
        result[key] = modified_value
    
    return result

def execute_all_paths(start_node):
    def run_path(input_node):
        for node in list_output_nodes(input_node):
            return_value = execute_node(node) # An if statement node might break this loop
            if return_value != 'BREAK':
                run_path(node) # It will travel down 1111 then 1112 then 1121 ...
    run_path(start_node)

def get_forward_paths(start_node):
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

def get_back_paths(start_node):
    def visit(node, path):
        # If the node is already in the path, this path forms a loop. Return the path up to the current node.
        if node in path:
            return [path + [node]]

        # Extend the current path by including the current node at the beginning
        extended_path = [node] + path
        paths = []  # This will collect all paths leading to this node

        # Check if the current node has inputs and they are linked from other nodes
        inputs = [input for input in node.inputs if input.is_linked]
        
        if inputs:
            # If inputs exist, recurse for each linked node
            for input in inputs:
                for link in input.links:
                    linked_node = link.from_node
                    if node.automation_type == 'GAT':
                        if not node.allowed_to_pass:
                            break
                    paths.extend(visit(linked_node, extended_path))
        else:
            # If no inputs are linked, this is a starting node. Begin this path here.
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

def substitute_keys_into_strings(modifying_dictionary, strings):
    # Flag to check if the input was a single string
    single_string_input = False
    
    # Check if the input is a single string and convert it to a list if so
    if isinstance(strings, str):
        strings = [strings]
        single_string_input = True

    # List to store the modified strings
    modified_strings = []

    # Create a regular expression that matches any of the keys in the dictionary
    regex_pattern = re.compile("|".join(map(re.escape, modifying_dictionary.keys())))

    # Iterate over each string in the input list
    for s in strings:
        # Use re.sub to replace all matches at once
        modified_s = regex_pattern.sub(lambda match: modifying_dictionary[match.group(0)], s)
        
        # Add the modified string to the list
        modified_strings.append(modified_s)

    # Return the appropriate type based on the input
    if single_string_input:
        return modified_strings[0]
    else:
        return modified_strings

def get_node_form_tree():

    node_tree = None
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "node_form.node_form_tree":
            return tree

    if not node_tree:
        print('no node tree found')
        # self.report({'ERROR'}, "No Node Form Tree found")
        return None
    
def get_start_node():

    node_tree = get_node_form_tree()

    for node in node_tree.nodes:
        if hasattr(node, 'automation_type'):
            if node.automation_type == 'SRT':
                return node
        else:
            print('no start node found')
            return None

def append_unique_keys(target, appendage):
    
    for key, value in appendage.items():
        # Add to target only if key is not already in target
        if key not in target:
            target[key] = value
        else:
            print("WARNING: You have more than one definition for: \"" + key + "\"")
    return target

def get_replacement_dictionary():

    return_dictionary={}
    replacement_dictionary = bpy.context.scene.replacement_dictionary
    
    for i in range(len(replacement_dictionary)):
        variable = replacement_dictionary[i].variable
        replacement = replacement_dictionary[i].replacement
        return_dictionary[variable] = replacement

    return return_dictionary

def set_replacement_dictionary(dictionary):
    bpy.context.scene.replacement_dictionary.clear()
    i = 0
    for key in dictionary:
        bpy.context.scene.replacement_dictionary.add()
        bpy.context.scene.replacement_dictionary[i].variable = key
        bpy.context.scene.replacement_dictionary[i].replacement = dictionary[key]
        i += 1
