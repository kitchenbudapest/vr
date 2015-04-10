## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.0.262 (20150410)                        ##
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
from math import sqrt, radians
from sys import path as sys_path

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

# Import oculus modules
import oculus

# Import blender modules
import bge
from mathutils import Vector, Matrix, Euler, Quaternion

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
MOUNTED_ON_HEAD   = 0
MOUNTED_ON_DESK   = 1
MINIFIER = 0.1

PINCH_FINGERS_DISTANCE        = 2
PINCH_VERTEX_FINGERS_DISTANCE = 1


# Helper functions
#------------------------------------------------------------------------------#
def distance(position1, position2):
    return sqrt(pow(position2[0] - position1[0], 2) +
                pow(position2[1] - position1[1], 2) +
                pow(position2[2] - position1[2], 2))



#------------------------------------------------------------------------------#
class Sculptomat:

    # NOTE: local->global: http://blenderartists.org/forum/archive/index.php/t-180690.html


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, mounted_on_desk):
        # Create a new instance of the leap-motion controller
        self._leap_controller = Leap.Controller()
        # Create a new instance of the oculus-rift controller
        self._rift_controller = oculus.OculusRiftDK2(head_factor=10,    #  50
                                                     head_shift_y=-20,  # -20
                                                     head_shift_z=10)    #  10
        # Create a reference to the blender scene
        self._blender_scene = blender_scene = bge.logic.getCurrentScene()

        # Make references to blender objects
        self._camera = self._blender_scene.active_camera
        self._origo  = self._blender_scene.objects[GLOBAL_OBJECT]

        # Create finger blender objects from prototypes and
        # store their references inside Hand instances
        finger_creator = self._prototype_creator(PROTOTYPE_FINGER)
        self._left_hand  = Hand(finger_creator)
        self._right_hand = Hand(finger_creator)

        # Create surface blender object from prototype and
        # store its reference inside a Surface instance
        self._srf_f = Surface(self._prototype_creator('Prototype_Surface_face'))
        self._srf_w = Surface(self._prototype_creator('Prototype_Surface_wire'))


        self._left_hand.thumb_index_pinched_vertex  = None, None
        self._right_hand.thumb_index_pinched_vertex = None, None


        # TODO: pinches:
        #       - thumb + index  => move selected
        #       - thumb + middle => select
        #       - thumb + ring   => deselect
        #       - thumb + pinky  => deselect all


        # TODO: fake casted shadow with negative lamp:
        #       https://www.youtube.com/watch?v=iJUlqwKEdVQ


        def pinch(hand):
            # If user is pinching with thumb and index fingers
            if distance(hand.thumb.position,
                        hand.index.position) < PINCH_FINGERS_DISTANCE:

                try:
                    vertex_face, vertex_wire = hand.thumb_index_pinched_vertex
                    vertex_face.XYZ = vertex_wire.XYZ = hand.index.position
                    return
                except AttributeError:
                    pass

                hand.thumb.color = hand.index.color = 1.0, 0.0, 0.0, 1.0

                # Go through all vertices of surfaces
                srf_f = self._srf_f
                for i, vertex_wire in enumerate(self._srf_w):
                    # Check if pinching a vertex
                    if (distance(hand.thumb.position, vertex_wire.XYZ) < PINCH_VERTEX_FINGERS_DISTANCE or
                        distance(hand.index.position, vertex_wire.XYZ) < PINCH_VERTEX_FINGERS_DISTANCE):
                            # If so edit the vertex's position and stop iterating
                            # TODO: calculate the midpoint between index and thumb
                            hand.thumb.color = hand.index.color = 0.0, 1.0, 0.0, 0.5
                            vertex_wire.XYZ = hand.index.position
                            srf_f[i].XYZ
                            hand.thumb_index_pinched_vertex = vertex_face, vertex_wire
                            return
            else:
                hand.thumb_index_pinched_vertex = None, None
                hand.thumb.color = hand.index.color = 1.0, 1.0, 1.0, 1.0


        self._right_hand.append_callback('pinch', pinch)
        self._left_hand.append_callback('pinch', pinch)

        # Set position setter
        # If DESK
        if mounted_on_desk:
            #self._hands = self._right_hand, self._left_hand
            self._hands = self._left_hand, self._right_hand
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

        # Set camera position and orientation
        self._camera.worldPosition = rift_frame.position
        self._camera.worldOrientation = \
            Quaternion((1, 0, 0), radians(80))*Quaternion(rift_frame.orientation)

        # If leap was unable to get a proper frame
        if not leap_frame.is_valid:
            return print('(leap) Invalid frame')

        # If leap was able to get the frame set finger positions
        positioner = self._positioner
        for leap_hand in leap_frame.hands:
            hand = self._hands[int(leap_hand.is_right)]
            for finger in leap_hand.fingers:
                # TODO: positioner(*finger.tip_position) => leaking memory and never returns
                hand.do_finger(finger.type(), position=positioner(finger.tip_position))
            #
            hand.do_callbacks()


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
sculptomat = Sculptomat(MOUNTED_ON_DESK)
