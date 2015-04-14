## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.2.333 (20150414)                        ##
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

# Import user modules
from app import Application, MOUNTED_ON_DESK, MOUNTED_ON_HEAD

# Import global level constants
from const import (COLOR_ROTATE_PINCH_BASE,
                   COLOR_ROTATE_PINCH_OKAY,
                   COLOR_GRAB_PINCH_BASE,
                   COLOR_GRAB_PINCH_FAIL,
                   COLOR_GRAB_PINCH_OKAY,
                   COLOR_GEOMETRY_BASE,
                   COLOR_GEOMETRY_DARK,
                   COLOR_GEOMETRY_LITE)



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level constants
PINCH_FINGERS_DISTANCE        = 2
PINCH_VERTEX_FINGERS_DISTANCE = 1



# Helper functions
#------------------------------------------------------------------------------#
def distance(position1, position2):
    return sqrt(pow(position2[0] - position1[0], 2) +
                pow(position2[1] - position1[1], 2) +
                pow(position2[2] - position1[2], 2))



#------------------------------------------------------------------------------#
class KibuVR(Application):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *args, **kwargs):
        super().__init__(MOUNTED_ON_DESK, *args, **kwargs)

        # TODO: pinches:
        #       - thumb + index  => move selected
        #       - thumb + middle => select
        #       - thumb + ring   => deselect
        #       - thumb + pinky  => deselect all

        # Set callback-states which will be used
        # duyring the execution of the callbacks
        self.hands.left.set_states(grabbed=False,
                                   thumb_index_pinched_vertex=None)
        self.hands.right.set_states(grabbed=False,
                                    thumb_index_pinched_vertex=None)

        # Set actual callbacks
        self.hands.append_callback('grab', self.on_grab)
        self.hands.right.append_callback('pinch', self.on_pinch)
        self.hands.left.append_callback('pinch', self.on_pinch)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_grab(self, states):
        left    = states['left_hand']
        right   = states['right_hand']
        grabbed = False

        # If both hands are pinching with thumb and middle
        if (distance(left.thumb.position,
                     left.middle.position) < PINCH_FINGERS_DISTANCE and
            distance(right.thumb.position,
                     right.middle.position) < PINCH_FINGERS_DISTANCE):
                grabbed = True
                left.thumb.color  = left.middle.color  = \
                right.thumb.color = right.middle.color = COLOR_ROTATE_PINCH_OKAY
                self.vertex_origo.applyRotation((0, 0, radians(2)))
                self.surface.update()
        # If only one or none of the hands are pinching with thumb and middle
        else:
            left.middle.color = right.middle.color = COLOR_ROTATE_PINCH_BASE

        # Set hand-level callback state
        left.set_states(grabbed=grabbed)
        right.set_states(grabbed=grabbed)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_pinch(self, states):
        # TODO: while pinching, make other fingers hidden
        if states['grabbed']:
            return

        # Get local reference of this hand
        hand = states['hand']

        # If user is pinching with thumb and index fingers
        if distance(hand.thumb.position,
                    hand.index.position) < PINCH_FINGERS_DISTANCE:

            surface = self.surface
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
                if (distance(hand.thumb.position,
                             vertex.worldPosition) < PINCH_VERTEX_FINGERS_DISTANCE or
                    distance(hand.index.position,
                             vertex.worldPosition) < PINCH_VERTEX_FINGERS_DISTANCE):
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



#------------------------------------------------------------------------------#
application = KibuVR()
