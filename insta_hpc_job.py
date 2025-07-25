import bpy
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set scene frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 150

# Create the head node (master server)
def create_head_node():
    location = (0, 0, 10)
    bpy.ops.mesh.primitive_cube_add(size=2.5, location=location)
    head = bpy.context.active_object
    head.name = "Head_Node"
    
    # Create and apply black material
    mat = bpy.data.materials.new(name="Head_Black_Mat")
    mat.diffuse_color = (0, 0, 0, 1)  # RGBA (Black)
    head.data.materials.append(mat)
    
    return head

head_node = create_head_node()

# Create worker servers in a grid
def create_worker_servers(rows=3, cols=4, spacing=3):
    servers = []
    for i in range(rows):
        for j in range(cols):
            x = j * spacing - (cols - 1) * spacing / 2
            y = i * spacing - (rows - 1) * spacing / 2
            location = (x, y, 0)
            
            # Add cube and scale it flat
            bpy.ops.mesh.primitive_cube_add(size=2, location=location)
            server = bpy.context.active_object
            server.name = f"Worker_{i}_{j}"
            server.scale.z = 0.2  # Flatten vertically
            
            # Create black material
            mat = bpy.data.materials.new(name=f"Black_Mat_{i}_{j}")
            mat.diffuse_color = (0, 0, 0, 1)  # RGBA
            server.data.materials.append(mat)
            
            servers.append(server)
    return servers

worker_servers = create_worker_servers()

# Create and animate data packets
def create_packet(start_loc, name):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=start_loc)
    packet = bpy.context.active_object
    packet.name = name

    # Create and apply blue material
    mat = bpy.data.materials.new(name=f"{name}_Blue_Mat")
    mat.diffuse_color = (0, 0.2, 1, 1)  # RGBA (Bright Blue)
    packet.data.materials.append(mat)
    
    return packet

def animate_packet(packet, start_frame, end_frame, start_loc, end_loc):
    # Set initial location and blue color
    packet.location = start_loc
    packet.keyframe_insert(data_path="location", frame=start_frame)

    # Create animation arc (optional)
    mid_frame = (start_frame + end_frame) // 2
    mid_loc = end_loc.copy()
    mid_loc.z += 1.5
    packet.location = mid_loc
    packet.keyframe_insert(data_path="location", frame=mid_frame)

    # Final landing position
    packet.location = end_loc
    packet.keyframe_insert(data_path="location", frame=end_frame)

    # Animate color change: hold blue until just before landing
    mat = packet.data.materials[0]
    mat.diffuse_color = (0, 0.2, 1, 1)  # Blue
    mat.keyframe_insert(data_path="diffuse_color", frame=end_frame - 1)

    mat.diffuse_color = (0, 1, 0, 1)  # Green
    mat.keyframe_insert(data_path="diffuse_color", frame=end_frame)

# Distribute jobs from head node to workers
for i in range(12):
    start = head_node.location.copy()
    start.z -= 1.0  # Move slightly below head node

    worker = random.choice(worker_servers)
    end = worker.location.copy()
    end.z = 0.25  # Land right on top of the flattened server


    packet = create_packet(start_loc=start, name=f"Job_{i}")
    animate_packet(packet, start_frame=10 * i + 1, end_frame=10 * i + 20, start_loc=start, end_loc=end)

# Add camera
def setup_camera():
    bpy.ops.object.camera_add(location=(0, -20, 10), rotation=(1.2, 0, 0))
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

# Add light
def setup_light():
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 30))

bpy.context.scene.world.color = (0.05, 0.05, 0.05)

setup_camera()
setup_light()

scene = bpy.context.scene
scene.render.resolution_x = 1080
scene.render.resolution_y = 1080
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 150

scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = "/Users/bill/Desktop/hpc_instagram.mp4"
