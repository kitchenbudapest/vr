## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.2.029 (20150513)                        ##
##                              File: genenv.py                               ##
##                                                                            ##
##               For more information about the project, visit                ##
##                         <http://plastey.kibu.hu>.                          ##
##              Copyright (C) 2015 Peter Varo, Kitchen Budapest               ##
##                                                                            ##
##  This program is free software: you can redistribute it and/or modify it   ##
##   under the terms of the GNU General Public License as published by the    ##
##       Free Software Foundation, either version 3 of the License, or        ##
##                    (at your option) any later version.                     ##
##                                                                            ##
##    This program is distributed in the hope that it will be useful, but     ##
##         WITHOUT ANY WARRANTY; without even the implied warranty of         ##
##            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.            ##
##            See the GNU General Public License for more details.            ##
##                                                                            ##
##     You should have received a copy of the GNU General Public License      ##
##     along with this program, most likely a file in the root directory,     ##
##        called 'LICENSE'. If not, see <http://www.gnu.org/licenses>.        ##
##                                                                            ##
######################################################################## INFO ##

# Import python modules
from os.path      import join
from math         import radians
from colorsys     import hsv_to_rgb
from configparser import ConfigParser
from itertools    import repeat, count

# Import blender modules
import bpy
import bmesh

# Import plastey modules
import plane
import sphere

GEN_PLANE = False

#------------------------------------------------------------------------------#
# Read configuration
config = ConfigParser()
with open('config.ini', encoding='utf-8') as file:
    config.read_file(file)

# Modul level constants from user's config
INT_BLENDER_COUNTER      = config['Internal']['blender_counter']
VR_MESH_WIRE_WIDTH       = float(config['Dimensions']['mesh_wire_width'])
VR_MESH_FACE_WIDTH       = float(config['Dimensions']['mesh_face_width'])
VR_MESH_FACE_HEIGHT      = float(config['Dimensions']['mesh_face_height'])
VR_REGION_COUNT_X        = float(config['Dimensions']['region_count_x'])
VR_REGION_COUNT_Y        = float(config['Dimensions']['region_count_y'])
VR_SUBDIVISION_LEVEL_X   = float(config['Dimensions']['subdivision_level_x'])
VR_SUBDIVISION_LEVEL_Y   = float(config['Dimensions']['subdivision_level_y'])
VR_VERTEX_RADIUS         = float(config['Dimensions']['vertex_radius'])
VR_FINGER_RADIUS         = float(config['Dimensions']['finger_radius'])
VR_RESOLUTION_X          = int(config['Render']['resolution_x'])
VR_RESOLUTION_Y          = int(config['Render']['resolution_y'])
VR_REFRESH_RATE          = int(config['Render']['refresh_rate'])
VR_FACE_COLOR            = hsv_to_rgb(*eval(config['Colors']['face_color']))
VR_EDGE_COLOR            = hsv_to_rgb(*eval(config['Colors']['edge_color']))
VR_WORLD_COLOR           = hsv_to_rgb(*eval(config['Colors']['world_color']))
VR_DOT_COLOR             = hsv_to_rgb(*eval(config['Colors']['dot_color']))
VR_TEXT_FIRST_COLOR      = hsv_to_rgb(*eval(config['Colors']['text_color_first']))
VR_TEXT_FIRST_ALPHA      = float(config['Colors']['text_alpha_first'])
VR_TEXT_OTHER_COLOR      = hsv_to_rgb(*eval(config['Colors']['text_color_other']))
VR_TEXT_OTHER_ALPHA      = float(config['Colors']['text_alpha_other'])
VR_LAMP_TOP_SIZE         = float(config['Lamps']['lamp_top_size'])
VR_LAMP_TOP_DISTANCE     = float(config['Lamps']['lamp_top_distance'])
VR_LAMP_BOTTOM_SIZE      = float(config['Lamps']['lamp_bottom_size'])
VR_LAMP_BOTTOM_DISTANCE  = float(config['Lamps']['lamp_bottom_distance'])
VR_LOGIC_OBJECT          = config['Names']['logic']
VR_SCENE                 = config['Names']['scene']
VR_HUD_SCENE             = config['Names']['hud_scene']
VR_WORLD                 = config['Names']['world']
VR_CAMERA_OBJECT         = config['Names']['camera_object']
VR_CAMERA_DATA           = config['Names']['camera_data']
VR_CAMERA_HUD_OBJECT     = config['Names']['camera_hud_object']
VR_CAMERA_HUD_DATA       = config['Names']['camera_hud_data']
VR_TEXT_FIRST_OBJECT     = config['Names']['text_first_object']
VR_TEXT_FIRST_DATA       = config['Names']['text_first_data']
VR_TEXT_OTHER_OBJECT     = config['Names']['text_other_object']
VR_TEXT_OTHER_DATA       = config['Names']['text_other_data']
VR_MIST_START            = float(config['World']['mist_falloff_start'])
VR_MIST_DEPTH            = float(config['World']['mist_falloff_depth'])
VR_LAMP_TOP              = config['Names']['lamp_top']
VR_LAMP_BOTTOM           = config['Names']['lamp_bottom']
VR_LAMP_TOP_OBJECT       = config['Names']['lamp_top_object']
VR_LAMP_BOTTOM_OBJECT    = config['Names']['lamp_bottom_object']
VR_GEOMETRY_OBJECT       = config['Names']['geometry_object']
VR_GEOMETRY_MESH         = config['Names']['geometry_mesh']
VR_ARMATURE_CONTROL      = config['Names']['armature_control']
VR_ARMATURE_ARMATURE     = config['Names']['armature_armature']
VR_ARMATURE_OBJECT       = config['Names']['armature_object']
VR_ARMATURE_BONE         = config['Names']['armature_bone'] + INT_BLENDER_COUNTER
VR_DOT_OBJECT            = config['Names']['dot_object'] + INT_BLENDER_COUNTER
VR_DOT_MESH              = config['Names']['dot_mesh'] + INT_BLENDER_COUNTER
VR_MATERIAL_GEOMETRY     = config['Names']['material_geometry']
VR_MATERIAL_WIRE         = config['Names']['material_wire']
VR_MATERIAL_DOT          = config['Names']['material_dot']
VR_FINGER_OBJECT         = config['Names']['finger_object']
VR_FINGER_MESH           = config['Names']['finger_mesh']
VR_DISTORTION_SHADER     = config['Scripts']['distortion_shader']
VR_GAME_LOGIC            = config['Scripts']['game_logic']
VR_FONT_PATH             = '//' + join(*eval(config['Fonts']['path']))
VR_FONT_EXTENSION        = '.'  + config['Fonts']['extension']
VR_FONT_REGULAR_FILE     = config['Fonts']['regular']
VR_FONT_BOLD_FILE        = config['Fonts']['bold']
VR_FONT_ITALIC_FILE      = config['Fonts']['italic']
VR_FONT_BOLD_ITALIC_FILE = config['Fonts']['bold_italic']
VR_VAR_TEXT_TIMER        = config['Scripts']['var_text_time']


#------------------------------------------------------------------------------#
# Module level constants
VAR_SCREEN_WIDTH  = 'screen_width'
VAR_SCREEN_HEIGHT = 'screen_height'


#------------------------------------------------------------------------------#
# Reset cursor location
bpy.context.scene.cursor_location = 0, 0, 0


#------------------------------------------------------------------------------#
# Create blender data
scene          = bpy.data.scenes.new(VR_SCENE)
hud_scene      = bpy.data.scenes.new(VR_HUD_SCENE)
camera         = bpy.data.cameras.new(VR_CAMERA_DATA)
hud_camera     = bpy.data.cameras.new(VR_CAMERA_HUD_DATA)
text_1st       = bpy.data.curves.new(VR_TEXT_FIRST_DATA, 'FONT')
text_nth       = bpy.data.curves.new(VR_TEXT_OTHER_DATA, 'FONT')
mesh           = bpy.data.meshes.new(VR_GEOMETRY_MESH)
armature       = bpy.data.armatures.new(VR_ARMATURE_ARMATURE)
world          = bpy.data.worlds.new(VR_WORLD)
lamp_1         = bpy.data.lamps.new(VR_LAMP_TOP, 'SPOT')
lamp_2         = bpy.data.lamps.new(VR_LAMP_BOTTOM, 'SPOT')
fng_mesh       = bpy.data.meshes.new(VR_FINGER_MESH)

# Create blender objects
lmp_object1    = bpy.data.objects.new(VR_LAMP_TOP, lamp_1)
lmp_object2    = bpy.data.objects.new(VR_LAMP_BOTTOM, lamp_2)
log_object     = bpy.data.objects.new(VR_LOGIC_OBJECT, None)
cam_object     = bpy.data.objects.new(VR_CAMERA_OBJECT, camera)
cam_hud_object = bpy.data.objects.new(VR_CAMERA_HUD_OBJECT, hud_camera)
txt_1st_object = bpy.data.objects.new(VR_TEXT_FIRST_OBJECT, text_1st)
txt_nth_object = bpy.data.objects.new(VR_TEXT_OTHER_OBJECT, text_nth)
geo_object     = bpy.data.objects.new(VR_GEOMETRY_OBJECT, mesh)
ctl_object     = bpy.data.objects.new(VR_ARMATURE_CONTROL, None)
arm_object     = bpy.data.objects.new(VR_ARMATURE_OBJECT, armature)
fng_object     = bpy.data.objects.new(VR_FINGER_OBJECT, fng_mesh)


#------------------------------------------------------------------------------#
# Import and set fonts
for font_name, property in ((VR_FONT_REGULAR_FILE    , 'font'),
                            (VR_FONT_BOLD_FILE       , 'font_bold'),
                            (VR_FONT_ITALIC_FILE     , 'font_italic'),
                            (VR_FONT_BOLD_ITALIC_FILE, 'font_bold_italic')):
    bpy.ops.font.open(filepath=join(VR_FONT_PATH, font_name + VR_FONT_EXTENSION),
                      relative_path=True)
    setattr(text_1st, property, bpy.data.fonts[font_name])
    setattr(text_nth, property, bpy.data.fonts[font_name])


#------------------------------------------------------------------------------#
# TODO: this is not working as it should be:
# Set context and toggle to camera view
bpy.context.screen.scene = hud_scene
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].region_3d.view_perspective = 'CAMERA'

# Bind objects to the hud-scene
hud_scene.objects.link(cam_hud_object)
hud_scene.objects.link(txt_1st_object)
hud_scene.objects.link(txt_nth_object)

# Set hud-scene's objects
hud_scene.render.engine               = 'BLENDER_GAME'
hud_scene.render.resolution_x         = int(VR_RESOLUTION_X/2)
hud_scene.render.resolution_y         = VR_RESOLUTION_Y
hud_scene.game_settings.material_mode = 'GLSL'
hud_scene.game_settings.resolution_x  = VR_RESOLUTION_X
hud_scene.game_settings.resolution_y  = VR_RESOLUTION_Y
hud_scene.game_settings.samples       = 'SAMPLES_8'
hud_camera.type                       = 'ORTHO'
cam_hud_object.location               = 0, -10, 0
cam_hud_object.rotation_mode          = 'XYZ'
cam_hud_object.rotation_euler         = radians(90), 0, 0
text_1st.body  = text_nth.body        = ''
text_1st.align = text_nth.align       = 'LEFT'
text_1st.size  = text_nth.size        = 0.2
txt_1st_object.location               = -2, 0, 0
txt_1st_object.rotation_mode          = 'XYZ'
txt_1st_object.rotation_euler         = radians(90), 0, 0
txt_nth_object.location               = -2, 0, -0.2
txt_nth_object.rotation_mode          = 'XYZ'
txt_nth_object.rotation_euler         = radians(90), 0, 0
# Because text does not support materials in BGE
txt_1st_object.color                  = VR_TEXT_FIRST_COLOR + (VR_TEXT_FIRST_ALPHA,)
txt_nth_object.color                  = VR_TEXT_OTHER_COLOR + (VR_TEXT_OTHER_ALPHA,)


#------------------------------------------------------------------------------#
# TODO: this is not working as it should be:
# Set context and toggle
bpy.context.screen.scene = scene
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].region_3d.view_perspective = 'CAMERA'

# Bind objects to the scene
scene.world = world
scene.objects.link(log_object)
scene.objects.link(cam_object)
scene.objects.link(lmp_object1)
scene.objects.link(lmp_object2)
scene.objects.link(geo_object)
scene.objects.link(ctl_object)
scene.objects.link(arm_object)
scene.objects.link(fng_object)

# Set scene properties
scene.render.engine                 = 'BLENDER_GAME'
scene.render.resolution_x           = int(VR_RESOLUTION_X/2)
scene.render.resolution_y           = VR_RESOLUTION_Y
scene.game_settings.material_mode   = 'GLSL'
scene.game_settings.show_mouse      = True
scene.game_settings.stereo          = 'STEREO'
scene.game_settings.stereo_mode     = 'SIDEBYSIDE'
scene.game_settings.frequency       = VR_REFRESH_RATE
scene.game_settings.samples         = 'SAMPLES_8'
scene.game_settings.resolution_x    = VR_RESOLUTION_X
scene.game_settings.resolution_y    = VR_RESOLUTION_Y
scene.game_settings.exit_key        = 'NONE'
scene.game_settings.physics_engine  = 'NONE'
scene.game_settings.show_fullscreen = False
scene.game_settings.raster_storage  = 'VERTEX_ARRAY'

# Set world properties
world.horizon_color          = VR_WORLD_COLOR
world.mist_settings.use_mist = True
world.mist_settings.start    = VR_MIST_START
world.mist_settings.depth    = VR_MIST_DEPTH

# Set camera
cam_object.location       = 0, -20, 8
cam_object.rotation_mode  = 'XYZ'
cam_object.rotation_euler = radians(66), 0, 0
camera.lens               = 20
camera.clip_start         = 0.1
camera.clip_end           = 100

# Set lamps
# TODO: figure out how to set values, when falloff_type='CUSTOM_CURVE'
lmp_object1.location         = 0, 0, 20
lamp_1.energy                = 10
lamp_1.falloff_type          = 'INVERSE_SQUARE'
lamp_1.use_sphere            = True
lamp_1.use_square            = True
lamp_1.ge_shadow_buffer_type = 'VARIANCE'
lamp_1.shadow_buffer_size    = 1024
lamp_1.spot_size             = radians(VR_LAMP_TOP_SIZE)
lamp_1.distance              = VR_LAMP_TOP_DISTANCE

lmp_object2.location         = 0, 0, -20
lmp_object2.rotation_mode    = 'XYZ'
lmp_object2.rotation_euler   = radians(180), 0, 0
lamp_2.energy                = 7
lamp_2.falloff_type          = 'INVERSE_SQUARE'
lamp_2.use_sphere            = True
lamp_2.use_square            = True
lamp_2.ge_shadow_buffer_type = 'VARIANCE'
lamp_2.shadow_buffer_size    = 1024
lamp_2.spot_size             = radians(VR_LAMP_BOTTOM_SIZE)
lamp_2.distance              = VR_LAMP_BOTTOM_DISTANCE


#------------------------------------------------------------------------------#
# Set face and wire material for mesh
for material_name, material_color in ((VR_MATERIAL_GEOMETRY, VR_FACE_COLOR),
                                      (VR_MATERIAL_WIRE    , VR_EDGE_COLOR)):
    material = bpy.data.materials.new(material_name)
    material.diffuse_color                      = material_color
    material.diffuse_intensity                  = 0.5
    material.game_settings.physics              = False
    material.use_raytrace                       = False
    material.use_mist                           = True
    material.use_full_oversampling              = True
    material.use_shadows                        = True
    material.use_transparent_shadows            = True
    material.use_cast_shadows                   = True
    material.use_cast_buffer_shadows            = True
    material.game_settings.use_backface_culling = False
    mesh.materials.append(material)


#------------------------------------------------------------------------------#
# Create dot material
dot_material = bpy.data.materials.new(VR_MATERIAL_GEOMETRY)
dot_material.diffuse_color           = VR_DOT_COLOR
dot_material.use_shadeless           = True
dot_material.use_raytrace            = False
dot_material.use_mist                = True
dot_material.use_full_oversampling   = True
dot_material.game_settings.physics   = False
dot_material.use_cast_shadows        = True
dot_material.use_cast_buffer_shadows = True
dot_material.use_object_color        = True


#------------------------------------------------------------------------------#
# Build base geometry
(plane.generate if GEN_PLANE else sphere.generate)(
    scene               = scene,
    geo_data            = mesh,
    geo_object          = geo_object,
    arm_data            = armature,
    arm_object          = arm_object,
    ctl_object          = ctl_object,
    dot_material        = dot_material,
    bone_name           = VR_ARMATURE_BONE,
    dot_data_name       = VR_DOT_MESH,
    dot_object_name     = VR_DOT_OBJECT,
    region_count_x      = VR_REGION_COUNT_X,
    region_count_y      = VR_REGION_COUNT_Y,
    subdivision_level_x = VR_SUBDIVISION_LEVEL_X,
    subdivision_level_y = VR_SUBDIVISION_LEVEL_Y,
    mesh_face_width     = VR_MESH_FACE_WIDTH,
    mesh_face_height    = VR_MESH_FACE_HEIGHT,
    edge_width          = VR_MESH_WIRE_WIDTH,
    dot_radius          = VR_VERTEX_RADIUS
)


#------------------------------------------------------------------------------#
# Create and move finger prototypes to layer
geometry = bmesh.new()
bmesh.ops.create_cube(geometry, size=VR_FINGER_RADIUS)
geometry.to_mesh(fng_mesh)
geometry.free()
fng_object.layers = (False, True) + (False,)*18
modifier = fng_object.modifiers.new('Subsurf', 'SUBSURF')
modifier.levels = 3

# Create finger material
fng_material = bpy.data.materials.new(VR_MATERIAL_GEOMETRY)
fng_material.diffuse_color           = VR_DOT_COLOR
fng_material.use_shadeless           = True
fng_material.use_raytrace            = False
fng_material.use_mist                = True
fng_material.use_full_oversampling   = True
fng_material.game_settings.physics   = False
fng_material.use_cast_shadows        = True
fng_material.use_cast_buffer_shadows = True
fng_material.use_object_color        = True
fng_mesh.materials.append(fng_material)


#------------------------------------------------------------------------------#
# Load text files
bpy.data.texts.load(VR_DISTORTION_SHADER)


#------------------------------------------------------------------------------#
# Make logic object active and selected
bpy.context.scene.objects.active = log_object
log_object.select = True

# Add game logic parts, and set their values
bpy.ops.logic.sensor_add(type='ALWAYS')
always_sensor = log_object.game.sensors[-1]
always_sensor.use_pulse_true_level = True

bpy.ops.logic.controller_add(type='LOGIC_AND')
and_controller = log_object.game.controllers[-1]
bpy.ops.logic.controller_add(type='PYTHON')
python_controller = log_object.game.controllers[-1]
python_controller.mode = 'MODULE'
python_controller.module = VR_GAME_LOGIC

bpy.ops.logic.actuator_add(type='FILTER_2D')
filter_actuator = log_object.game.actuators[-1]
filter_actuator.mode = 'CUSTOMFILTER'
filter_actuator.glsl_shader = bpy.data.texts[VR_DISTORTION_SHADER]

# Connect logic object
always_sensor.link(and_controller)
always_sensor.link(python_controller)
and_controller.link(actuator=filter_actuator)

# Add properties
bpy.ops.object.game_property_new(type='FLOAT', name=VAR_SCREEN_WIDTH)
bpy.ops.object.game_property_new(type='FLOAT', name=VAR_SCREEN_HEIGHT)
bpy.ops.object.game_property_new(type='TIMER', name=VR_VAR_TEXT_TIMER)
log_object.game.properties[VAR_SCREEN_WIDTH].value  = VR_RESOLUTION_X
log_object.game.properties[VAR_SCREEN_HEIGHT].value = VR_RESOLUTION_Y
log_object.game.properties[VR_VAR_TEXT_TIMER].value = 0.0
