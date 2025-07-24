# script that shows how data travels from DRAM to CPU core in blender animation

import bpy
import mathutils

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create black material
def create_black_material(name="BlackMat"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = False
    mat.diffuse_color = (0, 0, 0, 1)
    return mat

black_mat = create_black_material()

# Create Memory block (cube)
bpy.ops.mesh.primitive_cube_add(size=2, location=(-5, 0, 0))
memory = bpy.context.object
memory.name = "Memory"
memory.data.materials.append(black_mat)

# Create CPU core (as a black cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(5, 0, 0))
cpu_core = bpy.context.object
cpu_core.name = "CPU_Core"
cpu_core.data.materials.append(black_mat)

# Create Data packet (blue sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(-5, 0, 1.5))
packet = bpy.context.object
packet.name = "Data_Packet"

mat_packet = bpy.data.materials.new(name="PacketMat")
mat_packet.diffuse_color = (0, 0, 1, 1)
packet.data.materials.append(mat_packet)

# Add Labels 
def create_label(text, location, color=(0, 0, 1, 1)):
    bpy.ops.object.text_add(location=location)
    txt_obj = bpy.context.object
    txt_obj.data.body = text
    txt_obj.data.align_x = 'CENTER'
    txt_obj.data.size = 0.7
    txt_obj.data.extrude = 0.05
    txt_obj.rotation_euler = (1.5708, 0, 0.7854)
    mat = bpy.data.materials.new(name=f"Mat_{text}")
    mat.diffuse_color = color
    txt_obj.data.materials.append(mat)
    return txt_obj

create_label("Memory", (-5, 0, 2.5))
create_label("CPU Core", (5, 0, 2.5))

# Animate Data Packet 
start_frame = 1
end_frame = 100

packet.location = mathutils.Vector((-5, 0, 1.5))
packet.keyframe_insert(data_path="location", frame=start_frame)

packet.location = mathutils.Vector((5, 0, 1.5))
packet.keyframe_insert(data_path="location", frame=end_frame - 20)

# Processing pulse effect
process_start = end_frame - 20
process_end = end_frame

mat_packet.diffuse_color = (0, 0, 1, 1)
mat_packet.keyframe_insert(data_path="diffuse_color", frame=process_start)

mat_packet.diffuse_color = (1, 0, 0, 1)
mat_packet.keyframe_insert(data_path="diffuse_color", frame=process_start + 10)

mat_packet.diffuse_color = (0, 0, 1, 1)
mat_packet.keyframe_insert(data_path="diffuse_color", frame=process_end)

# Camera 
cam_data = bpy.data.cameras.new("Camera")
camera = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(camera)

camera.location = (10, -10, 6)
camera.rotation_euler = mathutils.Euler((1.1, 0, 0.8), 'XYZ')
bpy.context.scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(0, -10, 10))
sun = bpy.context.object
sun.data.energy = 3

bpy.ops.object.light_add(type='AREA', location=(0, 10, 5))
area = bpy.context.object
area.data.energy = 1000
area.data.size = 10

# Background color (light blue) 
bpy.context.scene.world.use_nodes = False
bpy.context.scene.world.color = (0.7, 0.85, 1.0)

# Instagram render resolution 
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.frame_end = end_frame

# Set output path and format for MP4 video 
output_path = "//data_packet_animation.mp4"  # Use '//' for relative to .blend file
scene = bpy.context.scene

scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'  # Or use 'MEDIUM', 'LOSSLESS'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'  # Encoding speed
scene.render.filepath = output_path

print("🎬 Export settings applied. To render to MP4, go to Render > Render Animation or press Ctrl+F12.")
