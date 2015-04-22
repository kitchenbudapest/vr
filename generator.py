## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.3.520 (20150422)                        ##
##                             File: generator.py                             ##
##                                                                            ##
##               For more information about the project, visit                ##
##                            <http://vr.kibu.hu>.                            ##
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
from math         import radians
from colorsys     import hsv_to_rgb
from configparser import ConfigParser
from itertools    import repeat, count

# Import blender modules
import bpy
import bmesh


#------------------------------------------------------------------------------#
def float_range(*args):
    try:
        start, stop, step, *rest = args
    except ValueError:
        step = 1
        try:
            start, stop = args
        except ValueError:
            start = 0
            stop = args[0]
    while start < stop:
        yield start
        start += step


#------------------------------------------------------------------------------#
# Read configuration
config = ConfigParser()
with open('config.ini', encoding='utf-8') as file:
    config.read_file(file)

# Modul level constants from user's config
VR_MESH_WIRE_WIDTH     = float(config['Dimensions']['mesh_wire_width'])
VR_MESH_FACE_WIDTH     = float(config['Dimensions']['mesh_face_width'])
VR_MESH_FACE_HEIGHT    = float(config['Dimensions']['mesh_face_height'])
VR_REGION_COUNT_X      = float(config['Dimensions']['region_count_x'])
VR_REGION_COUNT_Y      = float(config['Dimensions']['region_count_y'])
VR_VERTEX_RADIUS       = float(config['Dimensions']['vertex_radius'])
VR_SUBDIVISION_LEVEL_X = float(config['Dimensions']['subdivision_level_x'])
VR_SUBDIVISION_LEVEL_Y = float(config['Dimensions']['subdivision_level_y'])
VR_FACE_COLOR          = hsv_to_rgb(*eval(config['Colors']['face_color']))
VR_EDGE_COLOR          = hsv_to_rgb(*eval(config['Colors']['edge_color']))
VR_DOT_COLOR           = hsv_to_rgb(*eval(config['Colors']['dot_color']))
VR_LOGIC_OBJECT        = config['Names']['logic']
VR_SCENE               = config['Names']['scene']
VR_CAMERA_OBJECT       = config['Names']['camera_object']
VR_CAMERA_DATA         = config['Names']['camera_data']
VR_GEOMETRY_OBJECT     = config['Names']['geometry_object']
VR_GEOMETRY_MESH       = config['Names']['geometry_mesh']
VR_ARMATURE_CONTROL    = config['Names']['armature_control']
VR_ARMATURE_ARMATURE   = config['Names']['armature_armature']
VR_ARMATURE_OBJECT     = config['Names']['armature_object']
VR_ARMATURE_BONE       = config['Names']['armature_bone']
VR_DOT_OBJECT          = config['Names']['dot_object']
VR_DOT_MESH            = config['Names']['dot_mesh']
VR_MATERIAL_GEOMETRY   = config['Names']['material_geometry']
VR_MATERIAL_WIRE       = config['Names']['material_wire']
VR_MATERIAL_DOT        = config['Names']['material_dot']


#------------------------------------------------------------------------------#
# Module level constants
VAR_SCREEN_WIDTH  = 'screen_width'
VAR_SCREEN_HEIGHT = 'screen_height'

#lamps     = bpy.data.lamps

#------------------------------------------------------------------------------#
# Reset cursor location
bpy.context.scene.cursor_location = 0, 0, 0

# Create new scene, object and mesh
scene      = bpy.data.scenes.new(VR_SCENE)
camera     = bpy.data.cameras.new(VR_CAMERA_DATA)
mesh       = bpy.data.meshes.new(VR_GEOMETRY_MESH)
armature   = bpy.data.armatures.new(VR_ARMATURE_ARMATURE)
log_object = bpy.data.objects.new(VR_LOGIC_OBJECT, None)
cam_object = bpy.data.objects.new(VR_CAMERA_OBJECT, camera)
geo_object = bpy.data.objects.new(VR_GEOMETRY_OBJECT, mesh)
ctl_object = bpy.data.objects.new(VR_ARMATURE_CONTROL, None)
arm_object = bpy.data.objects.new(VR_ARMATURE_OBJECT, armature)
scene.objects.link(cam_object)
scene.objects.link(geo_object)
scene.objects.link(ctl_object)
scene.objects.link(arm_object)

# Make scene active
bpy.context.screen.scene = scene
scene.render.engine      = 'BLENDER_GAME'

# Set camera
cam_object.location       = 0, -20, 8
cam_object.rotation_mode  = 'XYZ'
cam_object.rotation_euler = radians(66), 0, 0

# Set face and wire material for mesh
for material_name, material_color in ((VR_MATERIAL_GEOMETRY, VR_FACE_COLOR),
                                      (VR_MATERIAL_WIRE    , VR_EDGE_COLOR)):
    material = bpy.data.materials.new(material_name)
    material.diffuse_color           = material_color
    material.diffuse_intensity       = 0.5
    material.game_settings.physics   = False
    material.use_raytrace            = False
    material.use_mist                = True
    material.use_full_oversampling   = True
    material.use_shadows             = True
    material.use_transparent_shadows = True
    material.use_cast_shadows        = True
    material.use_cast_buffer_shadows = True
    mesh.materials.append(material)

# Make armature active
bpy.context.scene.objects.active = arm_object
bpy.ops.object.mode_set(mode='EDIT')

# Create mesh
geometry = bmesh.new()

# Calculate values for the loops
step_x  = VR_MESH_FACE_WIDTH/VR_SUBDIVISION_LEVEL_X
step_y  = VR_MESH_FACE_HEIGHT/VR_SUBDIVISION_LEVEL_Y
range_x = VR_REGION_COUNT_X*VR_MESH_FACE_WIDTH + step_x
range_y = VR_REGION_COUNT_Y*VR_MESH_FACE_HEIGHT + step_y
start_x = -VR_REGION_COUNT_X/2*VR_MESH_FACE_WIDTH
start_y = -VR_REGION_COUNT_Y/2*VR_MESH_FACE_HEIGHT

# Set vertex coordinates and create faces
# TODO: it is very likely that the vertices list is not needed!
vertices = []
bevel_vertices = []
counter  = count()
for row_i, y in enumerate(float_range(start_y, start_y + range_y, step_y)):
    curr_row = []
    for col_i, x in enumerate(float_range(start_x, start_x + range_x, step_x)):
        curr_vert = geometry.verts.new((x, y, 0))

        if (not col_i%VR_SUBDIVISION_LEVEL_X and
            not row_i%VR_SUBDIVISION_LEVEL_Y):
                bone = armature.edit_bones.new(VR_ARMATURE_BONE.format(next(counter)))
                bone.head = x, y, 0
                bone.tail = x, y, 1
                curr_vert.select = True
        elif (not col_i%VR_SUBDIVISION_LEVEL_X or
              not row_i%VR_SUBDIVISION_LEVEL_Y):
                curr_vert.select = True

        if col_i and row_i:
            geometry.faces.new((prev_row[col_i - 1], prev_row[col_i], curr_vert, prev_vert))

        prev_vert = curr_vert
        curr_row.append(curr_vert)
    prev_row = curr_row
    vertices.append(curr_row)

# Write bmesh to mesh-object and prevent further access
geometry.to_mesh(mesh)
geometry.free()

# Close editing bones
bpy.ops.object.mode_set(mode='OBJECT')
# Open editing geometry
bpy.context.scene.objects.active = geo_object
bpy.ops.object.mode_set(mode='EDIT')

# 'Draw' wires as bevels
bpy.ops.mesh.bevel(offset=VR_MESH_WIRE_WIDTH, vertex_only=False)
# Assign materials to selection
bpy.context.object.active_material_index = 1
bpy.ops.object.material_slot_assign()

# Close editing geometry
bpy.ops.object.mode_set(mode='OBJECT')
# Switch back to armature
bpy.context.scene.objects.active = arm_object

# Create dot material
dot_material = bpy.data.materials.new(VR_MATERIAL_GEOMETRY)
dot_material.diffuse_color       = VR_DOT_COLOR
dot_material.use_shadeless       = True
material.use_raytrace            = False
material.use_mist                = True
material.use_full_oversampling   = True
material.game_settings.physics   = False
material.use_cast_shadows        = True
material.use_cast_buffer_shadows = True

# Add constraints to bones
for i, bone in enumerate(arm_object.pose.bones):
    dot_mesh   = bpy.data.meshes.new(VR_DOT_MESH.format(i))
    dot_object = bpy.data.objects.new(VR_DOT_OBJECT.format(i), dot_mesh)
    scene.objects.link(dot_object)

    dot_mesh.materials.append(dot_material)

    # Create mesh-geometry
    geometry = bmesh.new()
    bmesh.ops.create_cube(geometry,size=VR_VERTEX_RADIUS)
    geometry.to_mesh(dot_mesh)
    geometry.free()

    # Set object's parent and move it to place
    dot_object.parent   = ctl_object
    dot_object.location = bone.head

    # Add modifiers
    modifier = dot_object.modifiers.new('Subsurf', 'SUBSURF')
    modifier.levels = 3

    # Add constraints
    constraint = bone.constraints.new('COPY_LOCATION')
    constraint.target = dot_object

    constraint = bone.constraints.new('COPY_ROTATION')
    constraint.target = ctl_object
    constraint.use_offset = True

    constraint = bone.constraints.new('COPY_SCALE')
    constraint.target = ctl_object

# Set auto-weighted armature-parent to the geometry
geo_object.select = True
arm_object.select = True
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# Set up game properties
#for property_name, property_value in ((VAR_SCREEN_WIDTH, 960),
#                                      (VAR_SCREEN_HEIGHT, 540)):
#    game_property       = log_object.game_property_new(name=property_name)
#    game_property.type  = 'FLOAT'
#    game_property.value = property_value

# Add sensors


