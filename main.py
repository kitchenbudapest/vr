## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.0.201 (20150403)                        ##
##                               File: main.py                                ##
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
from math import sqrt
from sys import path as sys_path

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

# Import oculus modules
import oculus

# Import blender modules
import bge
from mathutils import Quaternion, Euler

# Import user modules
from surface import Surface
from hand import Hand

# TODO: make build-script work :)
# Import cutils modules => versioning
#import build


# Module level constants
#------------------------------------------------------------------------------#
PROTOTYPE_FINGER  = 'Prototype_Finger'
PROTOTYPE_SURFACE = 'Prototype_Surface'
GLOBAL_OBJECT     = 'Origo'
HEAD     = 0
DESK     = 1
MINIFIER = 0.1


# Helper functions
#------------------------------------------------------------------------------#
def distance(position1, position2):
    return sqrt(pow(position2[0] - position1[0], 2) +
                pow(position2[1] - position1[1], 2) +
                pow(position2[2] - position1[2], 2))



#------------------------------------------------------------------------------#
class Sculptomat:


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, mounted_on):
        # Create a new instance of the leap-motion controller
        self._leap_controller = Leap.Controller()
        # Create a new instance of the oculus-rift controller
        self._rift_controller = oculus.OculusRiftDK2(device_index=0)
        # Create a reference to the blender scene
        self._blender_scene = blender_scene = bge.logic.getCurrentScene()

        # Make references to blender objects
        self._camera  = self._blender_scene.active_camera

        # Create finger blender objects from prototypes and
        # store their references inside Hand instances
        finger_creator = self._prototype_creator(PROTOTYPE_FINGER)
        self._left_hand  = Hand(finger_creator)
        self._right_hand = Hand(finger_creator)

        # Create surface blender object from prototype and
        # store its reference inside a Surface instance
        #self._surface = Surface(self._prototype_creator(PROTOTYPE_SURFACE))
        self._srf_f = Surface(self._prototype_creator('Prototype_Surface_face'))
        self._srf_w = Surface(self._prototype_creator('Prototype_Surface_wire'))

        def pointed_with_index(object):
            position = object.localPosition
            for vertex in self._srf_f:
                print(position, vertex.XYZ)
                if distance(position, vertex.getXYZ()) < 2:
                    print('yeah')
                    vertex.y += 0.5

        self._right_hand.index.append_callback('position', pointed_with_index)

        # Set position setter
        # If DESK
        if mounted_on:
            self._hands = self._right_hand, self._left_hand
            self._positioner = self._positioner_on_desk
        # If HEAD
        else:
            self._hands = self._left_hand, self._right_hand
            self._positioner = self._positioner_on_head


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __call__(self):
        # Get current values of oculus-rift
        rift_frame = self._rift_controller.frame()
        # Get current values of the leap-motion
        leap_frame = self._leap_controller.frame()

        # Set camera position
        XXX = 50
        self._camera.localPosition = (  0 + rift_frame.position[0]*XXX,
                                      -25 - rift_frame.position[2]*XXX,
                                       15 + rift_frame.position[1]*XXX)

        # If leap was unable to get a proper frame
        if not leap_frame.is_valid:
            return print('(leap) Invalid frame')

        # If leap was able to get the frame set finger positions
        positioner = self._positioner
        for leap_hand in leap_frame.hands:
            hand = self._hands[int(leap_hand.is_right)]
            for finger in leap_hand.fingers:
                # TODO: positioner(*finger.tip_position) => leaking memory and never returns
                hand.do_finger(finger.type(), set_position=positioner(finger.tip_position))

        ## Set surface
        #for vertex in self._surface:
        #    # If so, color that vertex to 'red'
        #    if (distance(FINGERS[Leap.Finger.TYPE_THUMB].localPosition, vertex.getXYZ()) < 1.5 and
        #        distance(FINGERS[Leap.Finger.TYPE_INDEX].localPosition, vertex.getXYZ()) < 1.5):
        #            vertex.color = 1.0, 0.0, 0.0, 1.0  # red
        #    # If not change the color back 'white'
        #    else:
        #        vertex.color = 1.0, 1.0, 1.0, 1.0  # white


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _positioner_on_head(self, position):
        # The USB cable is on the right side and
        # the indicator light is on the top
        return (position[0] * -MINIFIER,
                position[1] *  MINIFIER - 10,
                position[2] * -MINIFIER + 10)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _positioner_on_desk(self, position):
        # The USB cable is on the right side and
        # the indicator light is at the back
        return (position[0] *  MINIFIER,
                position[2] * -MINIFIER,
                position[1] *  MINIFIER - 10)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _prototype_creator(self, prototype):
        def creator(**preferences):
            object = self._blender_scene.addObject(prototype, GLOBAL_OBJECT)
            for preference, value in preferences.items():
                setattr(object, preference, value)
            return object
        return creator


#------------------------------------------------------------------------------#
# Create a new game instance
sculptomat = Sculptomat(mounted_on=DESK)
