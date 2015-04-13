## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.1.290 (20150413)                        ##
##                               File: const.py                               ##
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
from math import radians

# Import blender modules
from mathutils import Quaternion

# Blender object names
OBJ_PROTOTYPE_FINGER     = 'Prototype_Finger'
OBJ_PROTOTYPE_SURFACE    = 'Prototype_Surface_all'
OBJ_PROTOTYPE_VERTEX_ALL = 'Prototype_VertexSpheres'
OBJ_GLOBAL               = 'Origo'

# Colors
COLOR_GEOMETRY_BASE      = 0.000, 0.448, 0.205, 1.000
COLOR_GEOMETRY_DARK      = 0.000, 0.073, 0.036, 1.000
COLOR_GEOMETRY_LITE      = 0.000, 1.000, 0.448, 1.000

COLOR_FINGER_BASE        = 1.000, 1.000, 1.000, 1.000
COLOR_GRAB_PINCH_BASE    = COLOR_FINGER_BASE
COLOR_GRAB_PINCH_OKAY    = 0.000, 1.000, 0.000, 0.350
COLOR_GRAB_PINCH_FAIL    = 1.000, 0.000, 0.000, 1.000

COLOR_ROTATE_PINCH_BASE  = COLOR_FINGER_BASE
COLOR_ROTATE_PINCH_OKAY  = 0.000, 0.000, 1.000, 1.000

# Sizes
SIZE_FINGER_THUMB        = 1.00
SIZE_FINGER_INDEX        = 0.60
SIZE_FINGER_MIDDLE       = 0.70
SIZE_FINGER_RING         = 0.60
SIZE_FINGER_PINKY        = 0.55

# Hardware fine-tuning
LEAP_MULTIPLIER          =  0.1
RIFT_MULTIPLIER          =  10
RIFT_POSITION_SHIFT_Y    = -20
RIFT_POSITION_SHIFT_Z    =  10
RIFT_ORIENTATION_SHIFT   = Quaternion((1, 0, 0), radians(80))
