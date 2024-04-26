import bpy
import bmesh
import mathutils
import math

def grid(axisVector, offsetVector, density):
    # Store current selection
    current_selection = [obj for obj in bpy.context.selected_objects]

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.translate(bm, verts=list(bm.verts), vec=math_return_vector(1 / 2, 1 / 2, 1 / 2))
    math_flatten_bmesh(bm, axisVector)
    xCuts, yCuts, zCuts = math.floor(density * axisVector[0]), math.floor(density * axisVector[1]), math.floor(
        density * axisVector[2])
    xScale = abs(1 / xCuts if xCuts != 0 else 0)
    yScale = abs(1 / yCuts if yCuts != 0 else 0)
    zScale = abs(1 / zCuts if zCuts != 0 else 0)
    iterationsVector = mathutils.Vector((xCuts, yCuts, zCuts))
    scaleVector = mathutils.Vector((xScale, yScale, zScale))
    math_flatten_bmesh(bm, scaleVector)
    math_translate_bmesh(bm, offsetVector)
    bm_now = bm
    created_objects = []  # New array to store created objects
    for d in range(3):
        for i in range(int(iterationsVector[d]) - 1):
            bm_temp = bm_now.copy()
            bm_copy = bm_now.copy()
            obj = bmesh_embody_mesh(bm_temp)
            created_objects.append(obj)  # Add created object to the array
            translater = mathutils.Vector((0, 0, 0))
            translater[d] = axisVector[d] * scaleVector[d]
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

def hollow_grid(dimension, offset, density):
    obj = bpy.context.active_object
    bm = bmesh_selection_to_bmesh(obj)
    nudgeVector = math_scale_vector(math_scale_vector(dimension, 1 / (1 + density * (dimension[0] + dimension[1] + dimension[2]))), 1 / 2)
    bmesh_select_geometry(bm, offset + nudgeVector, dimension + offset - nudgeVector)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.select], context='FACES')
    bm.to_mesh(obj.data)
    bm.free()

# Add two more for loops, one for repeat iterations and the other one to apply the transform to each selected element
def transform(localxvar, localyvar, localzvar, transformation, time_span, steps_per_frame, repetitions, fast_transformation, add_weighted_original, keepOg, hideOg):
    
    transformationX = (transformation[0]) #The expressionreplacement will now happen when the arguments are being passed in 
    transformationY = (transformation[1])
    transformationZ = (transformation[2])

    for _ in range(repetitions):

        for obj in bpy.context.selected_objects:

            bpy.context.view_layer.objects.active = obj
            bpy.context.scene.frame_start = 0
            startframe = 0.0
            transitionConst = 0.0

            if add_weighted_original:
                transitionConst = 1.0

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

            framesPerSecond = 24
            frameDivisor = steps_per_frame
            upperRange = int(math.floor(time_span * framesPerSecond / frameDivisor))

            if time_span == 0:
                fast_transformation = True

            for f in range(upperRange+1):
                frameIndex = f
                trueframe = frameIndex + startframe
                keyString = 'Key ' + str(float(startframe + (frameIndex) * frameDivisor))
                activeObj.shape_key_add(name=keyString)

                for i, v in enumerate(original_object.data.shape_keys.key_blocks[basisKey].data):
                    
                    remainder = 0

                    if not fast_transformation:
                        remainder = (upperRange - frameIndex) / (upperRange)

                    x0, y0, z0 = v.co.x, v.co.y, v.co.z
                    xr, yr, zr = x0 * remainder * transitionConst, y0 * remainder * transitionConst, z0 * remainder * transitionConst
                    x, y, z = x0 * (1 - remainder), y0 * (1 - remainder), z0 * (1 - remainder)
                    t = ((frameIndex) * frameDivisor) / (framesPerSecond)
                    T = ((upperRange) * frameDivisor) / (framesPerSecond)
                    exec(transformationX); exec(transformationY); exec(transformationZ)
                    activeObj.data.shape_keys.key_blocks[keyString].data[i].co.x = locals()[localxvar] + xr
                    activeObj.data.shape_keys.key_blocks[keyString].data[i].co.y = locals()[localyvar] + yr
                    activeObj.data.shape_keys.key_blocks[keyString].data[i].co.z = locals()[localzvar] + zr

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

            if not keepOg:
                bpy.data.objects.remove(original_object, do_unlink=True)
            elif hideOg:
                original_object.hide_viewport = True

            bpy.context.preferences.edit.use_global_undo = True
            bpy.context.scene.frame_end = int(upperRange*frameDivisor + startframe)

def bpy_select_all():
    bpy.ops.object.select_all(action='SELECT')
    try:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
    except IndexError:
        bpy.context.view_layer.objects.active = None
    return

def bpy_deselect_all():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None
    
def bpy_delete_selected_objects():
    # Check if there are selected objects
    if bpy.context.selected_objects:
        # Set the mode to object mode to avoid context errors
        bpy.ops.object.mode_set(mode='OBJECT')
        # Delete all selected objects
        bpy.ops.object.delete()
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

def math_scale_vector(vector, scale):
    return vector(vector[0] * scale, vector[1] * scale, vector[2] * scale)

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
