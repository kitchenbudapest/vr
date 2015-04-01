## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.0.141 (20150401)                        ##
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

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

TYPES = (Leap.Finger.TYPE_THUMB,
         Leap.Finger.TYPE_INDEX,
         Leap.Finger.TYPE_MIDDLE,
         Leap.Finger.TYPE_RING,
         Leap.Finger.TYPE_PINKY)


#------------------------------------------------------------------------------#
class Hand:

    TYPE = ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def index(self):
        return self._index
    @index.setter
    def index(self, value):
        self._index = value


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, blender_scene):

        ## Create fingers
        #self._thumb  = ...
        #self._index  = ...
        #self._middle = ...
        #self._ring   = ...
        #self._pinky  = ...

        #self._fingers = (self.thumb,
        #                 self.index,
        #                 self.middle,
        #                 self.ring,
        #                 self.pinky)

        #for finger in self._fingers:
        #    bpy.ops.mesh.primitive_uv_sphere_add(size=1,
        #                                         segments=16,
        #                                         ring_count=8,
        #                                         view_align=False,
        #                                         enter_editmode=False,
        #                                         location=ORIGO,
        #                                         layers=FIRST_LAYER)


        ##
        ##   THIS WON'T WORK!
        ##
        #for id, object in iter(TYPES, self._fingers):
        #    setattr(self, id, object)

        self._fingers = {
            Leap.Finger.TYPE_THUMB  : blender_scene.objects['finger_{}_thumb'.format(self.TYPE)],
            Leap.Finger.TYPE_INDEX  : blender_scene.objects['finger_{}_index'.format(self.TYPE)],
            Leap.Finger.TYPE_MIDDLE : blender_scene.objects['finger_{}_middle'.format(self.TYPE)],
            Leap.Finger.TYPE_RING   : blender_scene.objects['finger_{}_ring'.format(self.TYPE)],
            Leap.Finger.TYPE_PINKY  : blender_scene.objects['finger_{}_pinky'.format(self.TYPE)],
        }


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __iter__(self):
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __setitem__(self, finger, position):
        self._fingers[finger].localPosition = position


#------------------------------------------------------------------------------#
class LeftHand(Hand):

    TYPE = 'left'



#------------------------------------------------------------------------------#
class RightHand(Hand):

    TYPE = 'right'
