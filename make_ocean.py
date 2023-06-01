import bpy
from random import uniform


def make_ocean(o_depth, o_size, w_scale, w_min, w_chop, wind_vel, w_align, wave_direct, foam_bool, foam_amount, foam_type):
    bpy.ops.mesh.primitive_plane_add(location = (0, 0 ,0))

    terrain = bpy.data.objects['Plane']

    # Add ocean modifier
    om = terrain.modifiers.new("om", 'OCEAN')

    # Ocean settings
    om.geometry_mode = 'GENERATE'
    om.resolution = 64
    om.depth = o_depth
    om.size = 1
    om.spatial_size = o_size
    om.random_seed = 1

    # Wave settings
    om.wave_scale = w_scale
    om.wave_scale_min = w_min
    om.choppiness = w_chop
    om.wind_velocity = wind_vel
    om.wave_alignment = w_align
    om.wave_direction = wave_direct

    # Foam settings
    om.use_foam = foam_bool
    om.foam_layer_name = "foam"
    om.foam_coverage = foam_amount
    om.spectrum = foam_type
    
    return terrain

def texture_ocean(ocean, ocean_colour, foam_colour):
    mat = bpy.data.materials.new(name='o_mat')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.get('Material Output')
    
    # principled bdsf for ocean
    o_shader = nodes.get('Principled BSDF')
    o_shader.inputs[0].default_value = ocean_colour
    o_shader.inputs[9].default_value = 0 # roughness
    o_shader.inputs[16].default_value = 1.333 #IOR
    o_shader.inputs[17].default_value = 1 # transmission
    
    #principled bdsf for foam
    f_shader = nodes.new(type='ShaderNodeBsdfPrincipled')
    f_shader.inputs[0].default_value = foam_colour
    
    #attribute 
    foam_attr = nodes.new(type='ShaderNodeAttribute')
    foam_attr.attribute_type = 'GEOMETRY'
    foam_attr.attribute_name = 'GEOMETRY'
    
    #math multiplier
    math_mult = nodes.new(type='ShaderNodeMath')
    math_mult.operation = 'MULTIPLY'
    
    #colour ramp
    colour_ramp = nodes.new(type='ShaderNodeValToRGB')
    colour_ramp.color_ramp.elements[0].position = 0.265
    colour_ramp.color_ramp.elements[1].position = 1
    
    # mix shader
    mix_shader = nodes.new('ShaderNodeMixShader')
    
    # Link up
    links.new(foam_attr.outputs[2], math_mult.inputs[0])
    links.new(math_mult.outputs[0], colour_ramp.inputs[0])
    links.new(colour_ramp.outputs[0], mix_shader.inputs[0])
    links.new(mix_shader.outputs[0], output.inputs[0])
    links.new(o_shader.outputs[0], mix_shader.inputs[1])
    links.new(f_shader.outputs[0], mix_shader.inputs[2])
    
    #math mult -> colour ramp -> mix shader -> output
    
    
    
def update_ocean(ocean):
    for mod in ocean.modifiers:
        if mod.type == 'OCEAN':
            mod.time = uniform(0,1)


o_colour = (0.009, 0.02, 0.028, 1)
foam_colour = (0.8, 0.8, 0.8, 1)
o_depth = 200
o_size = 5000
w_scale = 10
w_min = 0.1
w_chop = 1.5
wind_vel = 30
w_align = 0.5
wave_direct = 90
foam_bool = True
foam_amount = 0 #-inf to +inf
foam_type = 'PHILLIPS'

terrain = make_ocean(o_depth, o_size, w_scale, w_min, w_chop, wind_vel, w_align, wave_direct, foam_bool, foam_amount, foam_type)
texture_ocean(terrain, o_colour, foam_colour)
update_ocean(terrain)