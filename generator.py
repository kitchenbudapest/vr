## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.2.338 (20150414)                        ##
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
from itertools import repeat

# Import blender modules
import bpy

scenes = bpy.data.scenes
meshes = bpy.data.meshes

## Remove all objects from all scenes
## and remove all scenes as well
#for scene in scenes:
#    for object in scene.objects:
#        meshes.remove(object)
#    scenes.remove(scene)
## check: http://blenderscripting.blogspot.hu/2012/03/deleting-objects-from-scene.html

# Create a new scene
bpy.ops.scene.new(type='EMPTY')
scene = scenes[-1]
print(scene)


#------------------------------------------------------------------------------#
def _add_constraint_to_bones(armature_name, constraint_type, target_names, details):
    for bone, target_name in zip(bpy.data.objects[armature_name].pose.bones, target_names):
        constraint = bone.constraints.new(constraint_type)
        constraint.target = bpy.data.objects[target_name]
        for key, value in details.items():
            setattr(constraint, key, value)


#------------------------------------------------------------------------------#
# Convenient wrapper
def add_rotation_constraint_to_bones(armature_name, target_names, **details):
    _add_constraint_to_bones(armature_name, 'COPY_ROTATION', target_names, details)


#------------------------------------------------------------------------------#
# Convenient wrapper
def add_location_constraint_to_bones(armature_name, target_names, **details):
    _add_constraint_to_bones(armature_name, 'COPY_LOCATION', target_names, details)


#------------------------------------------------------------------------------#
# Calling 'adder' function
add_rotation_constraint_to_bones('Prototype_Surface_all',
                                 repeat('Prototype_VertexSpheres'),
                                 use_x=False,
                                 use_y=False)
