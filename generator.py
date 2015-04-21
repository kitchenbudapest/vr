## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.3.488 (20150421)                        ##
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
from itertools import repeat, count

# Import blender modules
import bpy
import bmesh
from mathutils import Vector, Matrix


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
# Modul level constants for configuration
VR_MESH_WIRE_WIDTH     = 0.1
VR_MESH_FACE_WIDTH     = 5
VR_MESH_FACE_HEIGHT    = 5
VR_REGION_COUNT_X      = 10
VR_REGION_COUNT_Y      = 10
VR_SUBDIVISION_LEVEL_X = 5
VR_SUBDIVISION_LEVEL_Y = 5
VR_VERTEX_RADIUS       = 0.5


#------------------------------------------------------------------------------#
# Module level constants
VR_SCENE             = 'vr_scene'
VR_GEOMETRY_OBJECT   = 'vr_geo_obj'
VR_GEOMETRY_MESH     = 'vr_geo_mesh'
VR_ARMATURE_CONTROL  = 'vr_arm_ctl_obj'
VR_ARMATURE_ARMATURE = 'vr_arm_arm'
VR_ARMATURE_OBJECT   = 'vr_arm_obj'
VR_ARMATURE_BONE     = 'vr_arm_bone.{:0>3}'
VR_DOT_OBJECT        = 'vr_dot_obj.{:0>3}'
VR_DOT_MESH          = 'vr_dot_mesh.{:0>3}'


# Data structures
#lamps     = bpy.data.lamps
#scenes    = bpy.data.scenes
#meshes    = bpy.data.meshes
#objects   = bpy.data.objects
#cameras   = bpy.data.cameras
#materials = bpy.data.materials
#armatures = bpy.data.armatures


#------------------------------------------------------------------------------#
# Create new scene, object and mesh
scene      = bpy.data.scenes.new(VR_SCENE)
mesh       = bpy.data.meshes.new(VR_GEOMETRY_MESH)
armature   = bpy.data.armatures.new(VR_ARMATURE_ARMATURE)
geo_object = bpy.data.objects.new(VR_GEOMETRY_OBJECT, mesh)
ctl_object = bpy.data.objects.new(VR_ARMATURE_CONTROL, None)
arm_object = bpy.data.objects.new(VR_ARMATURE_OBJECT, armature)
scene.objects.link(geo_object)
scene.objects.link(ctl_object)
scene.objects.link(arm_object)

# Make scene active
bpy.context.screen.scene = scene

# Make armature active
bpy.context.scene.objects.active = arm_object
bpy.ops.object.mode_set(mode='EDIT')

# Create mesh
geometry = bmesh.new()

# Calculate values for the loops
step_x   = VR_MESH_FACE_WIDTH/VR_SUBDIVISION_LEVEL_X
step_y   = VR_MESH_FACE_HEIGHT/VR_SUBDIVISION_LEVEL_Y
range_x  = VR_REGION_COUNT_X*VR_MESH_FACE_WIDTH + step_x
range_y  = VR_REGION_COUNT_Y*VR_MESH_FACE_HEIGHT + step_y
start_x  = -VR_REGION_COUNT_X/2*VR_MESH_FACE_WIDTH
start_y  = -VR_REGION_COUNT_Y/2*VR_MESH_FACE_HEIGHT

# Set vertex coordinates and create faces
vertices = []
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
        if col_i and row_i:
            geometry.faces.new((prev_row[col_i - 1], prev_row[col_i], curr_vert, prev_vert))
        prev_vert = curr_vert
        curr_row.append(curr_vert)
    prev_row = curr_row
    vertices.append(curr_row)

#wire_faces = bmesh.ops.bevel(geometry, ..., VR_MESH_WIRE_WIDTH, )

# Write bmesh to mesh-object and prevent further access
geometry.to_mesh(mesh)
geometry.free()

# Close editing bones
bpy.ops.object.mode_set(mode='OBJECT')

# Add constraints to bones
constraint_types = 'COPY_ROTATION', 'COPY_SCALE'
for i, bone in enumerate(arm_object.pose.bones):
    dot_mesh   = bpy.data.meshes.new(VR_DOT_MESH.format(i))
    dot_object = bpy.data.objects.new(VR_DOT_OBJECT.format(i), dot_mesh)
    scene.objects.link(dot_object)
    geometry = bmesh.new()
    bmesh.ops.create_cube(geometry,
                          size=VR_VERTEX_RADIUS,
                          matrix=Matrix.Translation(bone.head))

    geometry.to_mesh(dot_mesh)
    geometry.free()

    # Add constraints
    constraint = bone.constraints.new('COPY_LOCATION')
    constraint.target = dot_object

    constraint = bone.constraints.new('COPY_ROTATION')
    constraint.target = ctl_object

    constraint = bone.constraints.new('COPY_SCALE')
    constraint.target = ctl_object
