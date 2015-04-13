## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.1.290 (20150413)                        ##
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
from sys import path as sys_path, stderr

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

# Import oculus modules
import oculus

# Import blender modules
import bge
from mathutils import Vector, Matrix, Euler, Quaternion

# Import user modules
from hand import Hands
from surface import Surface

# Import global level constants
from const import (OBJ_PROTOTYPE_FINGER,
                   OBJ_PROTOTYPE_SURFACE,
                   OBJ_PROTOTYPE_VERTEX_ALL,
                   OBJ_GLOBAL,
                   COLOR_GEOMETRY_BASE,
                   COLOR_GEOMETRY_DARK,
                   COLOR_GEOMETRY_LITE,
                   COLOR_GRAB_PINCH_BASE,
                   COLOR_GRAB_PINCH_OKAY,
                   COLOR_GRAB_PINCH_FAIL,
                   COLOR_ROTATE_PINCH_BASE,
                   COLOR_ROTATE_PINCH_OKAY,
                   LEAP_MULTIPLIER,
                   RIFT_MULTIPLIER,
                   RIFT_POSITION_SHIFT_Y,
                   RIFT_POSITION_SHIFT_Z,
                   RIFT_ORIENTATION_SHIFT)

# TODO: make build-script work :)
# Import cutils modules => versioning
#import build


# Module level constants
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
MOUNTED_ON_HEAD = 0
MOUNTED_ON_DESK = 1

PINCH_FINGERS_DISTANCE        = 2
PINCH_VERTEX_FINGERS_DISTANCE = 1

SPACE_KEY      = bge.events.SPACEKEY
JUST_ACTIVATED = bge.logic.KX_INPUT_JUST_ACTIVATED


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
        self._rift_controller = oculus.OculusRiftDK2(head_factor =RIFT_MULTIPLIER,
                                                     head_shift_y=RIFT_POSITION_SHIFT_Y,
                                                     head_shift_z=RIFT_POSITION_SHIFT_Z)
        # Create a reference to the blender scene
        self._blender_scene = blender_scene = bge.logic.getCurrentScene()

        # Make references to blender objects
        self._camera = self._blender_scene.active_camera
        self._origo  = self._blender_scene.objects[OBJ_GLOBAL]

        # Create hands,
        self._hands = Hands(self._prototype_creator(OBJ_PROTOTYPE_FINGER))



        self._left_hand  = Hand(finger_creator)
        self._right_hand = Hand(finger_creator)

        # Create surface blender object from prototype and
        # store its reference inside a Surface instance
        self._surface = Surface(self._blender_scene.objects[OBJ_PROTOTYPE_SURFACE],
                                self._blender_scene.objects[OBJ_PROTOTYPE_VERTEX_ALL],
                                COLOR_GEOMETRY_DARK)

        #self._surface = Surface(self._prototype_creator('Prototype_Surface_all'),
        #                        self._prototype_creator('Prototype_VertexSpheres'))

        #self._srf_f = Surface(self._prototype_creator('Prototype_Surface_face'))
        #self._srf_w = Surface(self._prototype_creator('Prototype_Surface_wire'))

        self._hands.left.set_states(thumb_index_pinched_vertex=None)
        self._hands.right.set_states(thumb_index_pinched_vertex=None)


        # TODO: pinches:
        #       - thumb + index  => move selected
        #       - thumb + middle => select
        #       - thumb + ring   => deselect
        #       - thumb + pinky  => deselect all


        # TODO: fake casted shadow with negative lamp:
        #       https://www.youtube.com/watch?v=iJUlqwKEdVQ

        # HACK: yuck.. this is getting out of hands now :(:(:(
        self._vertex_origo = self._blender_scene.objects[OBJ_PROTOTYPE_VERTEX_ALL]

        def pinch(states):
            # TODO: while pinching, make other fingers hidden

            if states['grabbed']:
                return

            hand = states['hand']

            # If user is pinching with thumb and index fingers
            if distance(hand.thumb.position,
                        hand.index.position) < PINCH_FINGERS_DISTANCE:

                surface = self._surface
                try:
                    vertex = hand.thumb_index_pinched_vertex
                    vertex.worldPosition = hand.index.position
                    surface.update()
                    return
                except AttributeError:
                    pass

                hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_FAIL

                # Go through all vertices of surfaces
                for i, vertex in enumerate(surface):
                    # Check if pinching a vertex
                    if (distance(hand.thumb.position, vertex.worldPosition) < PINCH_VERTEX_FINGERS_DISTANCE or
                        distance(hand.index.position, vertex.worldPosition) < PINCH_VERTEX_FINGERS_DISTANCE):
                            # If so edit the vertex's position and stop iterating
                            # TODO: calculate the midpoint between index and thumb
                            hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_OKAY
                            vertex.color = COLOR_GEOMETRY_LITE
                            vertex.worldPosition = hand.index.position
                            hand.thumb_index_pinched_vertex = vertex
                            surface.update()
                            return
            # If there is no pinch or pinch was released
            else:
                try:
                    hand.thumb_index_pinched_vertex.color = COLOR_GEOMETRY_DARK
                except AttributeError:
                    pass
                hand.thumb_index_pinched_vertex = None
                hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_BASE


        def grab(states):
            left_hand  = states['left_hand']
            right_hand = states['right_hand']

            # If both hands are pinching with middle fingers
            if (distance(left_hand.thumb.position,
                         left_hand.middle.position) < PINCH_FINGERS_DISTANCE and
                distance(right_hand.thumb.position,
                         right_hand.middle.position) < PINCH_FINGERS_DISTANCE):
                    left_hand.set_states(grabbed=True)
                    right_hand.set_states(grabbed=True)
                    left_hand.thumb.color  = left_hand.middle.color  = \
                    right_hand.thumb.color = right_hand.middle.color = COLOR_ROTATE_PINCH_OKAY
                    self._vertex_origo.applyRotation((0, 0, radians(2)))
                    self._surface.update()

            else:
                left_hand.middle.color = right_hand.middle.color = COLOR_ROTATE_PINCH_BASE
                left_hand.set_states(grabbed=False)
                right_hand.set_states(grabbed=False)




        # Set callbacks
        self._hands.append_callback('grab', grab)
        self._hands.right.append_callback('pinch', pinch)
        self._hands.left.append_callback('pinch', pinch)

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
        # If user pressed the space bar => restart game
        if bge.logic.keyboard.events[SPACE_KEY] == JUST_ACTIVATED:
            bge.logic.restartGame()
            return

        # Get current values of oculus-rift
        rift_frame = self._rift_controller.frame()
        # Get current values of the leap-motion
        leap_frame = self._leap_controller.frame()

        # Set camera position and orientation
        self._camera.worldPosition = rift_frame.position
        self._camera.worldOrientation = \
            RIFT_ORIENTATION_SHIFT*Quaternion(rift_frame.orientation)

        # If leap was unable to get a proper frame
        if not leap_frame.is_valid:
            return print('(leap) Invalid frame', file=stderr)

        # If leap was able to get the frame set finger positions
        positioner = self._positioner
        for leap_hand in leap_frame.hands:
            hand = self._hands.right if leap_hand.is_right else self._hands.left
            for finger in leap_hand.fingers:
                # TODO: positioner(*finger.tip_position) => leaking memory and never returns
                hand.execute_callbacks('finger-position')
                hand.do_finger(finger.type(),
                               position=positioner(finger.tip_position))
            #
            hand.execute_all_callbacks()
        #
        self._hands.execute_all_callbacks()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _positioner_on_head(self, position):
        # The USB cable is on the right side and
        # the indicator light is on the top
        return (position[0] * -LEAP_MULTIPLIER,
                position[1] *  LEAP_MULTIPLIER - 10,
                position[2] * -LEAP_MULTIPLIER + 10)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _positioner_on_desk(self, position):
        # The USB cable is on the right side and
        # the indicator light is at the back
        return (position[0] *  LEAP_MULTIPLIER,
                position[2] * -LEAP_MULTIPLIER,
                position[1] *  LEAP_MULTIPLIER - 10)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _prototype_creator(self, prototype):
        def creator(**preferences):
            object = self._blender_scene.addObject(prototype, OBJ_GLOBAL)
            for preference, value in preferences.items():
                setattr(object, preference, value)
            return object
        return creator


#------------------------------------------------------------------------------#
# Create a new game instance
sculptomat = Sculptomat(MOUNTED_ON_DESK)
