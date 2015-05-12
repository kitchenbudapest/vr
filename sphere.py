## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.2.048 (20150513)                        ##
##                              File: sphere.py                               ##
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

#------------------------------------------------------------------------------#
def generate(scene,
             geo_data,
             geo_object,
             arm_data,
             arm_object,
             ctl_object,
             dot_material,
             bone_name,
             dot_data_name,
             dot_object_name,
             region_count_x      = 2,
             region_count_y      = 2,
             subdivision_level_x = 2,
             subdivision_level_y = 2,
             mesh_face_width     = 1,
             mesh_face_height    = 1,
             edge_width          = 0.1,
             dot_radius          = 0.1):
    # Make object active
    bpy.context.scene.objects.active = geo_object

    # Create cube
    geometry = bmesh.new()
    # TODO: calculate size based on region_count and mesh_face_width
    bmesh.ops.create_cube(geometry, size=30)
    geometry.to_mesh(geo_data)
    geometry.free()

    # Subdivide it, and make it sphere
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=round(region_count_x/2))
    bpy.ops.transform.tosphere(value=1)

    # Collect all vertices
    positions = []
    geometry = bmesh.from_edit_mesh(geo_data)
    for vertex in geometry.verts:
        head = vertex.co.copy()
        dist = head.copy()
        dist.normalize()
        tail = head + dist
        positions.append((head, tail))

    # Update mesh-data
    bmesh.update_edit_mesh(geo_data)
    # Create sub-division
    bpy.ops.mesh.subdivide(number_cuts=subdivision_level_x)

    # Deselect all vertices and select only the "main" vertices
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.edges_select_sharp(sharpness=radians(1))
    bpy.ops.mesh.bevel(offset=edge_width, vertex_only=False)
    # Assign materials to selection
    bpy.context.object.active_material_index = 1
    bpy.ops.object.material_slot_assign()

    # Close editing geometry
    bpy.ops.object.mode_set(mode='OBJECT')
    # Switch back to armature
    bpy.context.scene.objects.active = arm_object

    # Create bones
    bpy.ops.object.mode_set(mode='EDIT')
    for i, (head, tail) in enumerate(positions):
        # Create bones
        bone = arm_data.edit_bones.new(bone_name.format(i))
        bone.head = head
        bone.tail = tail
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create dot objects and set object hierarchy
    for i, bone in enumerate(arm_object.pose.bones):
        # Edit rotation mode of bone
        bone.rotation_mode = 'XYZ'

        # Create dot-objects
        dot_data   = bpy.data.meshes.new(dot_data_name.format(i))
        dot_object = bpy.data.objects.new(dot_object_name.format(i), dot_data)
        scene.objects.link(dot_object)

        # Assign material
        dot_data.materials.append(dot_material)

        # Set dot-object's parent and move it to its location
        dot_object.parent   = ctl_object
        dot_object.location = bone.head

        # Create dot geometry
        geometry = bmesh.new()
        bmesh.ops.create_cube(geometry, size=dot_radius)
        geometry.to_mesh(dot_data)
        geometry.free()

        # Add modifier to object
        modifier = dot_object.modifiers.new('Subsurf', 'SUBSURF')
        modifier.levels = 3

        # Add constraints
        constraint = bone.constraints.new('COPY_LOCATION')
        constraint.target = dot_object

        #constraint = bone.constraints.new('COPY_ROTATION')
        #constraint.target = control_object
        #constraint.use_offset = True
        #constraint.owner_space = 'LOCAL_WITH_PARENT'

        constraint = bone.constraints.new('COPY_SCALE')
        constraint.target = ctl_object

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Set auto-weighted armature-parent relation to the geometry
    geo_object.select = True
    arm_object.select = True
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
