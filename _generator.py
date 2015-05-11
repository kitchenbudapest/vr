## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.1.012 (20150511)                        ##
##                            File: _generator.py                             ##
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
from math import radians

# Import blender modules
import bpy
import bmesh
from mathutils import Vector

# Create blender data/objects
scene           = bpy.data.scenes.new('sphere_scene')
sphere_data     = bpy.data.meshes.new('sphere_mesh')
sphere_object   = bpy.data.objects.new('sphere_object', sphere_data)
armature_data   = bpy.data.armatures.new('sphere_bones')
armature_object = bpy.data.objects.new('sphere_armature', armature_data)
control_object  = bpy.data.objects.new('sphere_aramture_control', None)

# Setup scene
scene.objects.link(sphere_object)
scene.objects.link(armature_object)
scene.objects.link(control_object)
bpy.context.screen.scene = scene
bpy.context.scene.objects.active = sphere_object

# Create cube
geometry = bmesh.new()
bmesh.ops.create_cube(geometry, size=6)
geometry.to_mesh(sphere_data)
geometry.free()

# Subdivide it, and make it sphere
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=6)
bpy.ops.transform.tosphere(value=1)

# Collect all vertices
positions = []
geometry = bmesh.from_edit_mesh(sphere_data)
for vertex in geometry.verts:
    head = vertex.co.copy()
    dist = head.copy()
    dist.normalize()
    tail = head + dist
    positions.append((head, tail))

# Update mesh-data
bmesh.update_edit_mesh(sphere_data)
# Create sub-division
bpy.ops.mesh.subdivide(number_cuts=5)

# Deselect all vertices and select only the "main" vertices
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.edges_select_sharp(sharpness=radians(1))
bpy.ops.mesh.bevel(offset=0.01, vertex_only=False)

# Switch back to object-mode
bpy.ops.object.mode_set(mode='OBJECT')

# Create armature
bpy.context.scene.objects.active = armature_object
bpy.ops.object.mode_set(mode='EDIT')
for i, (head, tail) in enumerate(positions):
    # Create bones
    bone = armature_data.edit_bones.new('sphere_bone.{:0>3}'.format(i))
    bone.head = head
    bone.tail = tail
bpy.ops.object.mode_set(mode='OBJECT')

# Create dot objects and set object hierarchy
for i, bone in enumerate(armature_object.pose.bones):
    # Create dot-objects
    dot_data   = bpy.data.meshes.new('sphere_dot_mesh.{:0>3}'.format(i))
    dot_object = bpy.data.objects.new('sphere_dot_object.{:0>3}'.format(i), dot_data)
    scene.objects.link(dot_object)

    # Set dot-object's parent and move it to its location
    dot_object.parent   = control_object
    dot_object.location = bone.head

    # Create dot geometry
    geometry = bmesh.new()
    bmesh.ops.create_cube(geometry, size=0.1)
    geometry.to_mesh(dot_data)
    geometry.free()

    # Add modifier to object
    modifier = dot_object.modifiers.new('Subsurf', 'SUBSURF')
    modifier.levels = 3

    # Add constraints
    constraint = bone.constraints.new('COPY_LOCATION')
    constraint.target = dot_object

    constraint = bone.constraints.new('COPY_ROTATION')
    constraint.target = control_object
    constraint.use_offset = True
    constraint.owner_space = 'LOCAL'

    constraint = bone.constraints.new('COPY_SCALE')
    constraint.target = control_object

# Deselect all objects
bpy.ops.object.select_all(action='DESELECT')
# Set auto-weighted armature-parent relation to the geometry
sphere_object.select   = True
armature_object.select = True
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
