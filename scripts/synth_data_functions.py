'''Functions for synthetic object-recognition training data generation in blender
Functions for:

1 - loading pre-made terrain objects
2 - placing target object at random location (with slope based constraints)
3 - placing camera so object is within FOV
4 -  rendering+saving image
'''

import bpy
import math
from random import uniform
from mathutils import Vector

def load_terrain(terrain_name):
    ...

def place_target(terrain, target, margin):
    '''
    Inputs:
    terrain - premade terrain object, blender object
    target - target object, blender object
    margin - integer: safety margin around edges to prevent target placement near terrain edge
    '''
    terrain_size = terrain.size()
    minloc = margin
    maxloc = terrain_size - margin
    xloc = uniform(minloc, maxloc)
    yloc = uniform(minloc, maxloc)
    for loc, axis in enumerate([xloc, yloc], "xy"):
        setattr(target.location, axis, loc)

    elevation = terrain
    #set z height
  

def place_camera(terrain, target):
    ...


def render_and_save(
    output_dir, 
    output_file_pattern_string = 'render%d.jpg'
):
    """
    Inputs
    output_dir: STRING directory to save resulting rendered image to
    output_file_pattern_string: STRING name of resulting rendered image
    """
    import os
    bpy.context.scene.render.filepath = os.path.join(output_dir, (output_file_pattern_string % step))
    bpy.ops.render.render(write_still = True)
  
