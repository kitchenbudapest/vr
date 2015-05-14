## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.2.103 (20150514)                        ##
##                              File: loadenv.py                              ##
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
from sys          import path
from os.path      import join
from configparser import ConfigParser

# Import blender modules
import bpy

# Import plastey modules
path.insert(0, '.')
from utils import load_from_file, name_of_vertex
from const import INT_PERMANENT_FOLDER, OBJ_GEOMETRY

#------------------------------------------------------------------------------#
FILE_NAME = '.bz2'
SURF_TYPE = 0 # plane=0, sphere=1


#------------------------------------------------------------------------------#
coords = load_from_file(join(INT_PERMANENT_FOLDER, FILE_NAME))
try:
    # Adjust locations of the dots
    for i, coord in enumerate(zip(*(iter(coords),)*3)):
        bpy.data.objects[name_of_vertex(i)].location = coord

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')
    # Get and surface object
    surface = bpy.data.objects[OBJ_GEOMETRY]
    surface.select = True
    bpy.context.scene.objects.active = surface

    # If surface is a plane
    if not SURF_TYPE:
        modifier = surface.modifiers.new('Solidify', 'SOLIDIFY')
        modifier.thickness = 1.2
        modifier.use_quality_normals = True

    # Apply modifiers
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Armature")
    if not SURF_TYPE:
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")

    # Switch to edit-mode adn select all vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.vertices_smooth(factor=1)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add subsurface modifier
    modifier = surface.modifiers.new('Subsurf', 'SUBSURF')
    modifier.levels = 2 if SURF_TYPE else 3
except KeyError:
    print('[FAIL] Serialised data does not match environment')
