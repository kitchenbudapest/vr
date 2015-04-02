## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.0.146 (20150402)                        ##
##                               File: hand.py                                ##
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
from sys import path as sys_path
from collections import OrderedDict

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

FINGER_CONSTS = [('thumb' , {'leap_type'    : Leap.Finger.TYPE_THUMB,
                             'scale_factor' : 1.00}),
                 ('index' , {'leap_type'    : Leap.Finger.TYPE_INDEX,
                             'scale_factor' : 0.60}),
                 ('middle', {'leap_type'    : Leap.Finger.TYPE_MIDDLE,
                             'scale_factor' : 0.70}),
                 ('ring'  , {'leap_type'    : Leap.Finger.TYPE_RING,
                             'scale_factor' : 0.60}),
                 ('pinky' , {'leap_type'    : Leap.Finger.TYPE_PINKY,
                             'scale_factor' : 0.55})]

#------------------------------------------------------------------------------#
class Hand:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self,
                 blender_scene,
                 finger_prototype_name,
                 default_origin_name):

        self._fingers = fingers = OrderedDict()
        for finger, details in FINGER_CONSTS:
            # Create blender object from prototype
            obj = blender_scene.addObject(finger_prototype_name,
                                          default_origin_name)
            obj.localScale = (details['scale_factor'],)*3

            # Make finger accessible through this hand as a member
            setattr(self, finger, obj)

            # Store fingers to be accessible via leap-types
            fingers[details['leap_type']] = obj


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __repr__(self):
        return ('Hand(thumb={}, index={}, middle={}, '
                'ring={}, pinky={})').format(*self._fingers.values())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_finger(self, finger_leap_type, position):
        self._fingers[finger_leap_type].localPosition = position
