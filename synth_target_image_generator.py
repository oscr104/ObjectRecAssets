'''Script for synthetic object-recognition training data generation in blender
'''

import bpy
import math
from random import uniform
from mathutils import Vector, Matrix

def print(*data):
    """
    For debugging - by default pythons print function outputs to system console, doesnt show up in blender console 
    this function will print to blender console
    
    Input: data - string or multiple strings
    """
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.console.scrollback_append(override, text=str(" ".join([str(x) for x in data])), type="OUTPUT")   
    return

def clean_project():
    """
    Deletes all objects & any orphan data in the current scene
    """
    deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
                     'ARMATURE', 'LATTICE', 'EMPTY', 'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER']

    # Select all objects in the scene to be deleted:

    for o in bpy.context.scene.objects:
        for i in deleteListObjects:
            if o.type == i:
                o.select_set(False)
            else:
                o.select_set(True)
                
    # Deletes all selected objects in the scene:
    bpy.ops.object.delete() 
    
    #Deletes any orphan data still present
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)
    
    
    
    return


def world_setup(view_render):
    """
    Sets viewports to render (if desired) & sets up viewport camera to avoid clipping with large terrain meshes
    
    inputs
    view_render - boolean - whether to render fully in viewport, for developing via GUI, will be False when running for real
    """
    
    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    space = next(space for space in area.spaces if space.type == 'VIEW_3D')
    if view_render:
        space.shading.type = 'RENDERED' 
    else:
        space.shading.type = 'SOLID' 
    space.clip_end = 10000


def make_terrain(terrain_fpath,  light_type, light_energy, light_loc):
    """
    Loads pre-made terrain and sets up sun light source
    
    Inputs
    terrain_fpath - string, path to premade terrain
    light_type - string, which blender light type to use
    light_energy - scalar, strength for light source
    light_loc - xyz coordinates of light source
    """
    print("loading terrain")
    bpy.ops.import_scene.fbx(filepath=terrain_fpath)
    for object in bpy.data.objects:
        object.name = "Terrain"
    mats = bpy.data.materials
    for mat in mats:
        mat.blend_method = "OPAQUE"
    light_data = bpy.data.lights.new(name="LightSource", type=light_type)
    light_data.energy = light_energy
    light_object = bpy.data.objects.new(name="Lamp", object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = light_loc
    ...

def make_target(target_fpath):
    """
    Loads pre-made target object at world origin, and adds CopyLocation constraint to match Z-position of target & mesh  **Mesh name of imported object MUST be 'Target' (for now)
    
    Inputs
    target_fpath - string, path to premade target object
    """
    print("making target")
    bpy.ops.import_scene.fbx(filepath=target_fpath)

    mats = bpy.data.materials
    for mat in mats:
        mat.blend_method = "OPAQUE"
    
    scene = bpy.context.scene
    target = scene.objects["Target"]
    terrain = scene.objects["Terrain"]
    

    ...


def place_target(margin):
    '''
    Inputs:
    margin - float: safety margin around edges to prevent target placement near terrain edge
    '''
    #print("placing target")
    x_size = bpy.data.objects['Terrain'].dimensions.x
    y_size = bpy.data.objects['Terrain'].dimensions.y
    
    x_upper = (0 - ((x_size/2) - margin))
    x_lower = (x_size/2) - margin
    y_upper = (0 - ((y_size/2) - margin))
    y_lower = (y_size/2) - margin
    
    x, y = ((uniform(x_lower, x_upper)), (uniform(y_lower, y_upper)))
    #print(f"x = {x}, y={y}")
    raycast_origin = (x, y, 500)
    
    raycast_direction = (0, 0, -1)
    
    import bmesh
    context = bpy.context
    depsgraph = context.view_layer.depsgraph
    
    scene = bpy.context.scene
    
    target = scene.objects["Target"]
    terrain = scene.objects["Terrain"]
    me = target.data
    bm = bmesh.new()
    
    hit, loc, norm, idx, obj, mw = scene.ray_cast(depsgraph, raycast_origin, raycast_direction, distance = 1000) 
    
    if hit:
        print("PLACE TARGET AT")
        target.location = loc
        target.rotation_euler = (0, 0, math.radians(uniform(0, 360)))
    
    
    
    

def make_camera(focal_length, lens_angle):
    """
    Create camera object to use for rendering images
    
    Inputs:
    
    focal_length - float, in metres
    lens_angle - float, in radians
    
    """
    
    scn = bpy.context.scene
    cam = bpy.data.cameras.new("Camera")
    cam.lens = focal_length
    cam_obj = bpy.data.objects.new("Camera", cam)
    cam_obj.data.angle = lens_angle
    scn.collection.objects.link(cam_obj)

def add_jitter(base_value, jitter):
    """
    helper function to add random jitter to camera position
    """
    jittered_value = base_value+uniform(-jitter, jitter)
    return jittered_value

def place_camera(cam_height, xy_jitter, height_jitter):
    """
    place camera above terrain, looking straight down
    
    Inputs
    
    cam_height - float, in meters
    xy_jitter - float, in meters
    height_jitter - float,  in meters
    """
    
    scene = bpy.context.scene
    cam_obj = scene.objects["Camera"]
    target = scene.objects["Target"]
    height_jittered = add_jitter(cam_height, height_jitter)
    x_jittered = add_jitter(0, xy_jitter)
    y_jittered = add_jitter(0, xy_jitter)
    cam_location = target.location + Vector([x_jittered, y_jittered, height_jittered])
    cam_obj.location = cam_location
    cam_obj.rotation_euler = (0, 0, -1)
    ...


def render_and_save(
    output_dir, 
    output_file_pattern_string,
    resolution
):
    """
    Inputs
    output_dir: STRING directory to save resulting rendered image to
    output_file_pattern_string: STRING name of resulting rendered image
    resolution: integer, resolution for square output images
    """
    print("rendering & saving")
    import os
    scene = bpy.context.scene
    camera = scene.objects["Camera"]
    scene.camera = camera
    scene.render.filepath = os.path.join(output_dir, (output_file_pattern_string))
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    bpy.ops.render.render(write_still = True)
    ...


#Terrain variables
view_render = True
terrain_path = "E:/ObRec Assets/dolomites_test.fbx"
light_type = "SUN"
light_energy = 3
light_loc = (0, 0, 5000)

#Setup terrain
clean_project()
world_setup(view_render)
make_terrain(terrain_path, light_type, light_energy, light_loc)

#Camera variables
focal_length = 500 * 1000  # 500m in mm
lens_angle = math.radians(20)
make_camera(focal_length, lens_angle)


#Target data variables
target_path = "E:/ObRec Assets/target_t90.fbx"

make_target(target_path)




# Iterative image generation
cam_height = 500
xy_jitter = 50
height_jitter = 50
rotation_constraints = (0,0,0)
image_cycles = 10
margin = 100
resolution = 1080

output_dir = "E:/ObRec Assets/SyntheticData"


for count in range(image_cycles):
    #place_camera(xlim, ylim, cam_height, jitter, rotation_constraints)
    place_target(margin)
    place_camera(cam_height, xy_jitter, height_jitter)
    image_name = f"synth_data_{count}.jpg"
    print(image_name)
    render_and_save(output_dir, image_name, resolution)
    
    
    
    '''' More efficient raycasting?
    
from mathutils.bvhtree import BVHTree

C = bpy.context

# Build BVH once
bvh = BVHTree.FromObject(C.object, C.evaluated_depsgraph_get())

for i in range(999999):
    # Slower, this possibly builds BVH everytime
    # C.object.ray_cast((0, 0, 0), (0, 0, -1))

    # Faster
    bvh.ray_cast((0, 0, 0), (0, 0, -1))
'''