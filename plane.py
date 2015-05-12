## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.2.048 (20150513)                        ##
##                               File: plane.py                               ##
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
from itertools import count

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
    # Make armature active
    bpy.context.scene.objects.active = arm_object
    bpy.ops.object.mode_set(mode='EDIT')

    # Create mesh
    geometry = bmesh.new()

    # Calculate values for the loops
    step_x  = mesh_face_width/subdivision_level_x
    step_y  = mesh_face_height/subdivision_level_y
    range_x = region_count_x*mesh_face_width + step_x
    range_y = region_count_y*mesh_face_height + step_y
    start_x = -region_count_x/2*mesh_face_width
    start_y = -region_count_y/2*mesh_face_height

    # Set vertex coordinates and create faces
    # TODO: it is very likely that the vertices list is not needed!
    vertices = []
    bevel_vertices = []
    counter  = count()
    for row_i, y in enumerate(float_range(start_y, start_y + range_y, step_y)):
        curr_row = []
        for col_i, x in enumerate(float_range(start_x, start_x + range_x, step_x)):
            curr_vert = geometry.verts.new((x, y, 0))

            # Select dot vertices
            if (not col_i%subdivision_level_x and
                not row_i%subdivision_level_y):
                    bone = arm_data.edit_bones.new(bone_name.format(next(counter)))
                    bone.head = x, y, 0
                    bone.tail = x, y, 1
                    curr_vert.select = True
            # Select 'edge' vertices between two dots
            elif (not col_i%subdivision_level_x or
                  not row_i%subdivision_level_y):
                    curr_vert.select = True

            # Create faces
            if col_i and row_i:
                geometry.faces.new((prev_row[col_i - 1],
                                    prev_row[col_i],
                                    curr_vert,
                                    prev_vert))

            prev_vert = curr_vert
            curr_row.append(curr_vert)
        prev_row = curr_row
        vertices.append(curr_row)

    # Write bmesh to mesh-object and prevent further access
    geometry.to_mesh(geo_data)
    geometry.free()

    # Close editing bones
    bpy.ops.object.mode_set(mode='OBJECT')
    # Open editing geometry
    bpy.context.scene.objects.active = geo_object
    bpy.ops.object.mode_set(mode='EDIT')

    # 'Draw' wires as bevels
    bpy.ops.mesh.bevel(offset=edge_width, vertex_only=False)
    # Assign materials to selection
    bpy.context.object.active_material_index = 1
    bpy.ops.object.material_slot_assign()

    # Close editing geometry
    bpy.ops.object.mode_set(mode='OBJECT')
    # Switch back to armature
    bpy.context.scene.objects.active = arm_object

    # Add constraints to bones
    for i, bone in enumerate(arm_object.pose.bones):
        # Edit rotation mode of bone
        bone.rotation_mode = 'XYZ'

        # Create dot-objects
        dot_data   = bpy.data.meshes.new(dot_data_name.format(i))
        dot_object = bpy.data.objects.new(dot_object_name.format(i), dot_data)
        scene.objects.link(dot_object)

        # Assign material
        dot_data.materials.append(dot_material)

        # Create mesh-geometry
        geometry = bmesh.new()
        bmesh.ops.create_cube(geometry, size=dot_radius)
        geometry.to_mesh(dot_data)
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

        #constraint = bone.constraints.new('COPY_ROTATION')
        #constraint.target = ctl_object
        #constraint.use_offset = True
        #constraint.owner_space = 'LOCAL_WITH_PARENT'

        constraint = bone.constraints.new('COPY_SCALE')
        constraint.target = ctl_object

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Set auto-weighted armature-parent to the geometry
    geo_object.select = True
    arm_object.select = True
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
