# © 2025 Frank Dininno
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This add-on is built upon Blender's open-source codebase. Special thanks to
# the [Blender Foundation](https://www.blender.org/).

import bpy
import bmesh
import mathutils
import math
import importlib

# is_vector_field : destroy all but vertices, 
# add three evaluations, 
# add vectors at those points
# make a normalized check box 
# (and remove hollow)
def grid(lengths_vector, offset_vector, density_vector): 
    # Store current selection
    current_selection = [obj for obj in bpy.context.selected_objects]

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.translate(bm, verts=list(bm.verts), vec=math_return_vector(1 / 2, 1 / 2, 1 / 2))
    math_flatten_bmesh(bm, lengths_vector)
    xCuts = math.floor(density_vector[0] * abs(lengths_vector[0]))
    yCuts = math.floor(density_vector[1] * abs(lengths_vector[1]))
    zCuts = math.floor(density_vector[2] * abs(lengths_vector[2]))
    xScale = abs(1 / xCuts if xCuts != 0 else 0)
    yScale = abs(1 / yCuts if yCuts != 0 else 0)
    zScale = abs(1 / zCuts if zCuts != 0 else 0)
    iterationsVector = mathutils.Vector((xCuts, yCuts, zCuts))
    scaleVector = mathutils.Vector((xScale, yScale, zScale))
    math_flatten_bmesh(bm, scaleVector)
    math_translate_bmesh(bm, offset_vector)
    bm_now = bm
    created_objects = []  # New array to store created objects
    for d in range(3):
        for i in range(int(iterationsVector[d]) - 1):
            bm_temp = bm_now.copy()
            bm_copy = bm_now.copy()
            obj = bmesh_embody_mesh(bm_temp)
            created_objects.append(obj)  # Add created object to the array
            translater = mathutils.Vector((0, 0, 0))
            translater[d] = lengths_vector[d] * scaleVector[d]
            math_translate_bmesh(bm_copy, translater)
            bm_now = bm_copy
        obj = bmesh_embody_mesh(bm_now)
        created_objects.append(obj)  # Add created object to the array
        bpy_join_all(created_objects)  # Pass the array to the joinAll function
        created_objects.clear()  # Clear the array after joinAll function
        bm_now = bmesh_selection_to_bmesh(bpy.context.active_object)

    # Restore original selection
    for obj in current_selection:
        obj.select_set(True)

def hollow_grid(offset, dimension, density_vector):
    dimension_vector = math_return_vector(dimension[0], dimension[1], dimension[2])
    offset_vector = math_return_vector(offset[0], offset[1], offset[2])
    obj = bpy.context.active_object
    bm = bmesh_selection_to_bmesh(obj)

    # Summing the densities multiplied by the dimensions gauruntees that it is smaller than one cube, multiplying it by 1/2 makes sure that it is before the center of the inside face
    nudgeVector = math_scale_vector(dimension, 0.5 / (1 + (density_vector[0] + density_vector[1] + density_vector[2]) * (dimension[0] + dimension[1] + dimension[2])))

    bmesh_select_geometry(bm, offset_vector + nudgeVector, dimension_vector + offset_vector - nudgeVector)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.select], context='FACES')
    bm.to_mesh(obj.data)
    bm.free()

def transform(equations_vector, animation_run_time, frames_per_calculation, repeats, transformation_type, keep_option):

    print(equations_vector)

    for _ in range(int(repeats)+1):

        for obj in bpy.context.selected_objects:
            
            if obj and obj.type == 'MESH':

                mesh = obj.data
                
                if len(mesh.vertices) > 0:

                    startframe = 0.0
                    smoothing_constant = 0.0
                    is_instantaneous = False if animation_run_time > 0 else True
                    framesPerSecond = 24
                    frameDivisor = frames_per_calculation
                    upperRange = int(math.floor(animation_run_time * framesPerSecond / frameDivisor))

                    match transformation_type:
                        case 'REGULAR':
                            is_instantaneous = True
                        case 'SMOOTH':
                            smoothing_constant = 1.0
                        case 'LINEAR':
                            pass

                    bpy.context.view_layer.objects.active = obj
                    bpy.context.scene.frame_start = 0
                    bpy.context.preferences.edit.use_global_undo = False
                    original_object = bpy.context.active_object
                    basisKey = 'Basis'

                    if has_shape_key(original_object, 'Basis'):
                        startframe = get_last_keyframe(original_object)
                        basisKey = 'Key ' + str(startframe)
                    else:
                        obj.shape_key_add(name="Basis")

                    bpy.ops.object.duplicate()
                    activeObj = bpy.context.active_object

                    if startframe!=0:
                        activeObj.active_shape_key_index = activeObj.data.shape_keys.key_blocks.keys().index('Key ' + str(startframe))
                        bpy.ops.object.shape_key_remove()

                    for f in range(upperRange+1):
                        frameIndex = f
                        trueframe = frameIndex + startframe
                        keyString = 'Key ' + str(float(startframe + (frameIndex) * frameDivisor))
                        activeObj.shape_key_add(name=keyString)

                        for i, v in enumerate(original_object.data.shape_keys.key_blocks[basisKey].data):
                            
                            remainder = 0

                            if not is_instantaneous:
                                remainder = (upperRange - frameIndex) / (upperRange)

                            x0, y0, z0 = v.co.x, v.co.y, v.co.z
                            xr, yr, zr = x0 * remainder * smoothing_constant, y0 * remainder * smoothing_constant, z0 * remainder * smoothing_constant
                            x, y, z = x0 * (1 - remainder), y0 * (1 - remainder), z0 * (1 - remainder)
                            t = ((frameIndex) * frameDivisor) / (framesPerSecond)
                            T = ((upperRange) * frameDivisor) / (framesPerSecond)
                            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.x = safe_evaluation(equations_vector[0],x,y,z,t,T) + xr
                            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.y = safe_evaluation(equations_vector[1],x,y,z,t,T) + yr
                            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.z = safe_evaluation(equations_vector[2],x,y,z,t,T) + zr

                        if ((frameIndex == 0) and (startframe != 0)):
                            activeObj.data.shape_keys.key_blocks["Key " + str(startframe)].value = 0.0
                            activeObj.data.shape_keys.key_blocks["Key " + str(startframe)].keyframe_insert("value", frame=(frameDivisor + startframe))

                        if frameIndex != 0 or startframe != 0:
                            activeObj.data.shape_keys.key_blocks[keyString].value = 0.0
                            activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=((frameIndex - 1) * frameDivisor + startframe))

                        activeObj.data.shape_keys.key_blocks[keyString].value = 1.0
                        activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=((frameIndex) * frameDivisor + startframe))

                        if frameIndex < upperRange:
                            activeObj.data.shape_keys.key_blocks[keyString].value = 0.0
                            activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=((frameIndex + 1) * frameDivisor + startframe))
                    
                    match keep_option:
                        case 'KEEP':
                            pass
                        case 'HIDE':
                            original_object.hide_set(True)
                        case 'DELETE':
                            bpy.data.objects.remove(original_object, do_unlink=True)

                    bpy.context.preferences.edit.use_global_undo = True
                    bpy.context.scene.frame_end = int(upperRange*frameDivisor + startframe)

def bpy_select_all():
    bpy.ops.object.select_all(action='SELECT')
    try:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
    except IndexError:
        bpy.context.view_layer.objects.active = None
    return

def bpy_select_by_name(object_name):
    obj = bpy.data.objects.get(object_name)

    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

def bpy_deselect_all():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None

def bpy_deselect_by_name(object_name):

    obj = bpy.data.objects.get(object_name)

    if obj:
        obj.select_set(False)

def bpy_delete_selected_objects():
    # Check if there are selected objects
    if bpy.context.selected_objects:
        # Set the mode to object mode to avoid context errors
        bpy.ops.object.mode_set(mode='OBJECT')
        # Delete all selected objects
        bpy.ops.object.delete()
    else:
        bpy.context.view_layer.objects.active = None

def bpy_hide_selected_objects():
    # Check if there are selected objects
    if bpy.context.selected_objects:
        # Set the mode to object mode to avoid context errors
        bpy.ops.object.mode_set(mode='OBJECT')
        # Delete all selected objects
        bpy.ops.object.hide_set(True)
    else:
        bpy.context.view_layer.objects.active = None

def bpy_join_all(objects):
    bpy.context.view_layer.objects.active = objects[0]
    for obj in objects:  # Select only the objects in the array
        obj.select_set(True)
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')

def bmesh_select_geometry(bm, lowerVector, upperVector): # select faces within difference of coordinates between two vectors

    for f in bm.faces:
        f.select = False
    for f in bm.faces:
        vector = f.calc_center_median()
        if lowerVector.x < vector[0] < upperVector.x and \
                lowerVector.y < vector[1] < upperVector.y and \
                lowerVector.z < vector[2] < upperVector.z:
            f.select = True

def bmesh_selection_to_bmesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    return bm

def bmesh_embody_mesh(bm):
    mesh = bpy.data.meshes.new("Mesh")
    obj = bpy.data.objects.new("Mesh", mesh)
    bpy.context.collection.objects.link(obj)
    bm.to_mesh(mesh)
    bm.free()
    return obj  # Return the created object

def math_return_vector(x, y, z):
    return mathutils.Vector((x, y, z))

def math_scale_vector(input_vector, scale):
    return math_return_vector(input_vector[0] * scale, input_vector[1] * scale, input_vector[2] * scale)

def math_flatten_bmesh(bm, scaleVector):
    for v in bm.verts:
        scale_Matrix = mathutils.Matrix.Diagonal(scaleVector).to_4x4()
        v.co = scale_Matrix @ v.co
    return

def math_translate_bmesh(bm, directionVector):
    for v in bm.verts:
        translation_Matrix = mathutils.Matrix.Translation(directionVector)
        v.co = translation_Matrix @ v.co
    return

def get_keyframes(obj):
    keyframes = []
    anim = obj.animation_data
    if anim is not None and anim.action is not None:
        for fcu in anim.action.fcurves:
            for keyframe in fcu.keyframe_points:
                x, y = keyframe.co
                if x not in keyframes:
                    keyframes.append(math.ceil(x))
    if not keyframes:
        return 0
    return int(keyframes[-1])

def get_secondlast_keyframe(ob):
    if hasattr(ob.data, "shape_keys") and ob.data.shape_keys:
        action = ob.data.shape_keys.animation_data.action
        last_frame = None
        second_last_frame = None
        for fcu in action.fcurves:
            for keyframe in fcu.keyframe_points:
                if last_frame is None or keyframe.co[0] > last_frame:
                    second_last_frame = last_frame
                    last_frame = keyframe.co[0]
        return int(second_last_frame) if second_last_frame else None
    else:
        return None

def get_last_keyframe(ob):
    if hasattr(ob.data, "shape_keys") and ob.data.shape_keys:
        action = ob.data.shape_keys.animation_data.action
        last_frame = None
        for fcu in action.fcurves:
            for keyframe in fcu.keyframe_points:
                if last_frame is None or keyframe.co[0] > last_frame:
                    last_frame = keyframe.co[0]
        return float(last_frame) if last_frame else 0.0 
    else:
        return 0.0 
    
def has_shape_key(ob, name):
    return bool(
        hasattr(ob.data, "shape_keys") and
        ob.data.shape_keys and
        ob.data.shape_keys.key_blocks.get(name)
    )

def safe_evaluation(input, trfx=None, trfy=None, trfz=None, trft=None, trfT=None):

    expressions = [input] if isinstance(input, str) else input

    library_collection = bpy.context.scene.library_collection
    filepath_collection = bpy.context.scene.filepath_collection

    allowed_libraries = {'__builtins__': __builtins__, '[x]':trfx,'[y]':trfy,'[z]':trfz,'[t]':trft,'[T]':trfT}
    
    for library_element in library_collection:
        try:
            allowed_libraries[library_element.library_name] = importlib.import_module(library_element.library_name)
        except ImportError:
            print('no library imported')
    
    for filepath_element in filepath_collection:

        file_path = filepath_element.filepath_name
        # Extract the module name from the file path
        module_name = file_path.split('/')[-1].replace('.py', '')
        # Create a module spec
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        # Create a new module based on the spec
        module = importlib.util.module_from_spec(spec)

        try:
            # Execute the module in its own namespace
            spec.loader.exec_module(module)
            # Add the loaded and executed module to your dictionary
            allowed_libraries[filepath_element.module_name] = module
        except Exception as e:  # Catch broader exceptions if the loading or executing fails
            print(f'Failed to import {module_name}: {str(e)}')

    return_list = []
    for item in expressions:
        try:
            return_list.append(eval(item, allowed_libraries))
            # print(eval(item, allowed_libraries))
        except TypeError:
            print('Expression is not evaluable')
    
    return return_list[0] if isinstance(input, str) else return_list
