import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set render settings for IG Reels (portrait video)
scene = bpy.context.scene
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 200
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.filepath = "//ig_reel_output.mp4"

# Helper functions
def create_cylinder(name, location):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def create_sphere(name, location):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=location)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def create_cube(name, location):
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=location)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def create_text(name, text, location, size=0.5):
    bpy.ops.object.text_add(location=location)
    txt = bpy.context.active_object
    txt.name = name
    txt.data.body = text
    txt.scale = (size, size, size)
    return txt

def animate_location(obj, frame_start, frame_end, start_loc, end_loc):
    obj.location = start_loc
    obj.keyframe_insert(data_path="location", frame=frame_start)
    obj.location = end_loc
    obj.keyframe_insert(data_path="location", frame=frame_end)

def scale_animation_speed(obj, start_frame, speed_factor):
    if not obj.animation_data or not obj.animation_data.action:
        return
    for fcurve in obj.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            old_frame = keyframe.co.x
            # Scale frame timing
            keyframe.co.x = (old_frame - start_frame) * speed_factor + start_frame
            keyframe.handle_left.x = (keyframe.handle_left.x - start_frame) * speed_factor + start_frame
            keyframe.handle_right.x = (keyframe.handle_right.x - start_frame) * speed_factor + start_frame

# Create vertical layout (bottom to top)
core_y = 6
thread_y = 3
task_y = 0

# Create Cores (top)
cores = []
for i in range(4):
    x = i * 1.5 - 2.25
    core = create_cylinder(f"Core_{i+1}", location=(x, core_y, 0))
    create_text(f"CoreLabel_{i+1}", f"Core {i+1}", location=(x - 0.4, core_y + 0.7, 0), size=0.4)
    cores.append(core)

# Create Threads (middle)
threads = []
for i in range(8):
    x = (i % 4) * 1.5 - 2.25
    y = thread_y - (i // 4) * 1.2
    thread = create_sphere(f"Thread_{i+1}", location=(x, y, 0))
    create_text(f"ThreadLabel_{i+1}", f"Thread {i+1}", location=(x - 0.3, y + 0.5, 0.4), size=0.3)
    threads.append(thread)

# Create Tasks (bottom)
tasks = []
for i in range(10):
    x = (i % 5) * 1.2 - 2.4
    y = task_y - (i // 5) * 1.2
    task = create_cube(f"Task_{i+1}", location=(x, y, 0))
    create_text(f"TaskLabel_{i+1}", f"Task {i+1}", location=(x - 0.4, y + 0.4, 0), size=0.3)
    tasks.append(task)

# Animate threads (move up toward cores)
thread_gap = 10
for i, thread in enumerate(threads):
    start_frame = 1 + i * thread_gap
    end_frame = start_frame + 40
    start_loc = thread.location.copy()
    end_loc = start_loc.copy()
    end_loc.y = core_y - 1.2
    animate_location(thread, start_frame, end_frame, start_loc, end_loc)

# Animate tasks (move up to cores)
task_gap = 8
for i, task in enumerate(tasks):
    start_frame = 1 + i * task_gap
    end_frame = start_frame + 30
    core_target = cores[i % len(cores)].location.copy()
    core_target.z += 0.5  # hover above core
    animate_location(task, start_frame, end_frame, task.location.copy(), core_target)

# Add vertical camera view
bpy.ops.object.camera_add(location=(0, 1, 12), rotation=(math.radians(90), 0, 0))
cam = bpy.context.active_object
scene.camera = cam

# Add light
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
light = bpy.context.active_object
light.data.energy = 4

# --- SPEED CONTROL ---
speed_factor = 1  # Change this to 1, 2, or 4 for normal, half, or quarter speed

start_frame = scene.frame_start

# Apply speed scaling to all animated objects
for obj in threads + tasks:
    scale_animation_speed(obj, start_frame, speed_factor)

# Adjust scene frame end to accommodate slower animation durations
# Find max frame of all keyframes after scaling
max_frame = 0
for obj in threads + tasks:
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                if kp.co.x > max_frame:
                    max_frame = kp.co.x

scene.frame_end = int(max_frame) + 10  # add a bit of buffer
