# script for blender animation showing GPU tensor core processing

import bpy
import math
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Render settings (Instagram portrait)
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1350
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 80
bpy.context.scene.render.fps = 24
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.filepath = "//gpu_tensor_render.mp4"  # Change if needed

# Parameters
grid_size = 4
core_spacing = 2.0
core_size = 0.5
tensor_block_size = 0.6

# Create GPU core grid (4x4)
gpu_cores = []
for x in range(grid_size):
    for y in range(grid_size):
        bpy.ops.mesh.primitive_cube_add(size=core_size, location=(x * core_spacing, y * core_spacing, 0))
        core = bpy.context.active_object
        core.name = f"GPU_Core_{x}_{y}"
        
        mat_core = bpy.data.materials.new(name=f"CoreMat_{x}_{y}")
        mat_core.use_nodes = False
        mat_core.diffuse_color = (0.1, 0.1, 0.1, 1)
        core.data.materials.append(mat_core)
        
        gpu_cores.append(core)

# Helper: Create a 2x2x2 tensor cube
def create_big_tensor(start_pos, base_color_list, name_prefix):
    blocks = []
    idx = 0
    for x in range(2):
        for y in range(2):
            for z in range(2):
                pos = start_pos + Vector((x * tensor_block_size, y * tensor_block_size, z * tensor_block_size))
                bpy.ops.mesh.primitive_cube_add(size=tensor_block_size, location=pos)
                block = bpy.context.active_object
                block.name = f"{name_prefix}_Block_{idx}"
                
                # Create node-based material
                mat = bpy.data.materials.new(name=f"{name_prefix}_Mat_{idx}")
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs['Base Color'].default_value = base_color_list[idx % len(base_color_list)]
                block.data.materials.append(mat)
                
                blocks.append(block)
                idx += 1
    return blocks

# Color palettes
colors_tensor1 = [
    (1.0, 0.0, 0.0, 1), (0.8, 0.1, 0.1, 1), (0.9, 0.3, 0.3, 1), (1.0, 0.2, 0.2, 1),
    (0.9, 0.1, 0.1, 1), (0.8, 0.2, 0.2, 1), (1.0, 0.3, 0.3, 1), (0.7, 0.0, 0.0, 1),
]
colors_tensor2 = [
    (0.0, 0.0, 1.0, 1), (0.1, 0.1, 0.9, 1), (0.3, 0.3, 1.0, 1), (0.2, 0.2, 0.8, 1),
    (0.1, 0.1, 0.7, 1), (0.2, 0.2, 0.9, 1), (0.3, 0.3, 0.8, 1), (0.0, 0.0, 0.7, 1),
]

# Create tensors
center_x = grid_size * core_spacing / 2
start_pos_tensor1 = Vector((center_x - 1.2, center_x - 1.2, 5))
start_pos_tensor2 = Vector((center_x + 1.2, center_x - 1.2, 5))

tensor1_blocks = create_big_tensor(start_pos_tensor1, colors_tensor1, "Tensor1")
tensor2_blocks = create_big_tensor(start_pos_tensor2, colors_tensor2, "Tensor2")
all_blocks = tensor1_blocks + tensor2_blocks

# Animation frames
frame_start = 1
frame_arrive = 40
frame_hold = 60
frame_return = 80

# Animate all blocks moving in parallel 
for i, block in enumerate(all_blocks):
    original_loc = block.location.copy()
    target_core = gpu_cores[i % len(gpu_cores)]
    core_pos = target_core.location + Vector((0, 0, 0.7))

    # Movement
    block.keyframe_insert(data_path="location", frame=frame_start)
    block.location = core_pos
    block.keyframe_insert(data_path="location", frame=frame_arrive)
    block.keyframe_insert(data_path="location", frame=frame_hold)
    block.location = original_loc
    block.keyframe_insert(data_path="location", frame=frame_return)

    # Color change
    mat = block.data.materials[0]
    if mat.use_nodes:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            orig_color = bsdf.inputs['Base Color'].default_value[:]
            bsdf.inputs['Base Color'].default_value = orig_color
            bsdf.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=frame_start)
            bsdf.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=frame_arrive)
            bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            bsdf.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=frame_hold)
            bsdf.inputs['Base Color'].default_value = orig_color
            bsdf.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=frame_return)

# Add camera
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)

# Position camera at an angle (stylish 3D look)
cam_obj.location = (center_x + 6, center_x - 10, 12)
cam_obj.rotation_euler = (1.1, 0, 0.9)  # tilt downward and angled
bpy.context.scene.camera = cam_obj

# Optional: Add sun light
light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_obj = bpy.data.objects.new(name="Sun", object_data=light_data)
light_obj.rotation_euler = (0.8, 0.2, 0.2)
light_obj.location = (center_x, center_x - 5, 10)
bpy.context.collection.objects.link(light_obj)

def smart_camera_setup():
    # Get all mesh objects in the scene
    objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    if not objects:
        print("No objects to frame.")
        return

    # Compute bounding box center and size
    min_corner = Vector((float('inf'), float('inf'), float('inf')))
    max_corner = Vector((float('-inf'), float('-inf'), float('-inf')))
    for obj in objects:
        for vertex in obj.bound_box:
            v_world = obj.matrix_world @ Vector(vertex)
            min_corner = Vector((min(min_corner[i], v_world[i]) for i in range(3)))
            max_corner = Vector((max(max_corner[i], v_world[i]) for i in range(3)))

    center = (min_corner + max_corner) / 2
    size = max_corner - min_corner
    max_dim = max(size.x, size.y, size.z)

    # Create camera if it doesn't exist
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        cam_data = bpy.data.cameras.new("Camera")
        cam = bpy.data.objects.new("Camera", cam_data)
        bpy.context.collection.objects.link(cam)
        bpy.context.scene.camera = cam

    # Position the camera at an angle, scaled by scene size
    distance = max_dim * 2.0
    cam.location = center + Vector((distance, -distance * 1.2, distance * 1.2))
    cam.rotation_euler = (math.radians(60), 0, math.radians(45))

    # Look at the scene center using a track-to constraint
    if "CameraTrack" not in bpy.data.objects:
        empty = bpy.data.objects.new("CameraTrack", None)
        empty.location = center
        bpy.context.collection.objects.link(empty)
    else:
        empty = bpy.data.objects["CameraTrack"]
        empty.location = center

    if not any(c for c in cam.constraints if c.type == 'TRACK_TO'):
        constraint = cam.constraints.new(type='TRACK_TO')
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

    # Set camera as active
    bpy.context.scene.camera = cam

# Call the function
smart_camera_setup()

# Set light green background color
bpy.context.scene.world.use_nodes = True
bg_tree = bpy.context.scene.world.node_tree
bg_node = bg_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs[0].default_value = (0.7, 1.0, 0.7, 1)  # RGBA: Light green
