## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.5.627 (20150501)                        ##
##                               File: main.py                                ##
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
from itertools import repeat
from math import sqrt, radians

# Import blender modules
from mathutils import Matrix

# Import linmath modules
from linmath import Vec3, Mat4x4

# Import user modules
from surface import VertexLocked
from app     import Application, MOUNTED_ON_DESK, MOUNTED_ON_HEAD

# Import global level constants
from const import (COLOR_ROTATE_PINCH_BASE,
                   COLOR_ROTATE_PINCH_OKAY,
                   COLOR_GRAB_PINCH_BASE,
                   COLOR_GRAB_PINCH_FAIL,
                   COLOR_GRAB_PINCH_OKAY,
                   COLOR_GEOMETRY_BASE,
                   COLOR_GEOMETRY_DARK,
                   COLOR_GEOMETRY_LITE,
                   COLOR_LOCKED,
                   COLOR_UNLOCKED,
                   COMM_IS_PAIRED)



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level constants
GRAB_STRENGTH                 = 0.98
PINCH_FINGERS_DISTANCE        = 2
PINCH_VERTEX_FINGERS_DISTANCE = 1



# Helper functions
#------------------------------------------------------------------------------#
def distance(position1, position2):
    return sqrt(pow(position2[0] - position1[0], 2) +
                pow(position2[1] - position1[1], 2) +
                pow(position2[2] - position1[2], 2))


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def rotation_matrix_from_vectors(direction, target_direction):
    v = target_direction.cross_product(direction)
    skew = Mat4x4(( 0.0, -v.z,  v.y,  0.0),
                  ( v.z,  0.0, -v.x,  0.0),
                  (-v.y,  v.x,  0.0,  0.0),
                  ( 0.0,  0.0,  0.0,  0.0))
    try:
        return (Mat4x4.identity() + skew +
                (skew*skew)*((1 - direction*target_direction)/v.length**2))
    except ZeroDivisionError:
        return Mat4x4.identity()



#------------------------------------------------------------------------------#
class KibuVR(Application):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *args, **kwargs):
        super().__init__(MOUNTED_ON_DESK, *args, **kwargs)

        if COMM_IS_PAIRED:
            self.set_states(this_left=None, this_right=None,
                            other_left=None, other_right=None)
            self.append_callback('comm', self.on_communication)

        # TODO: pinches:
        #       - thumb + index  => move selected
        #       - thumb + middle => select
        #       - thumb + ring   => deselect
        #       - thumb + pinky  => deselect all

        self._prev_grabbed_line = None

        # Set callback-states which will be used
        # duyring the execution of the callbacks
        self.hands.left.set_states(grabbed=False,
                                   selected_vertices=None)
        self.hands.right.set_states(grabbed=False,
                                    selected_vertices=None)

        # Set actual callbacks
        self.hands.append_callback('grab', self.on_grab)
        self.hands.right.append_callback('pinch', self.on_pinch)
        self.hands.left.append_callback('pinch', self.on_pinch)

        self.hands.right.append_callback('grabbing', self.on_grabbing)
        self.hands.left.append_callback('grabbing', self.on_grabbing)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_communication(self, states):
        # Prepare and send data
        data = []
        for i, v in self.surface.selected():
            data.append((i, v.worldPosition[0], v.worldPosition[1], v.worldPosition[2]))

        #try:
        #    i, v = self.hands.left.selected_vertices
        #    d1 = i, v.worldPosition[0], v.worldPosition[1], v.worldPosition[2]
        #except (TypeError, AttributeError):
        #    d1 = None
        #try:
        #    i, v = self.hands.right.selected_vertices
        #    d2 = i, v.worldPosition[0], v.worldPosition[1], v.worldPosition[2]
        #except (TypeError, AttributeError):
        #    d2 = None

        # Receive data and act based on it
        for vertex in self.surface.unlock_all():
            vertex.color = COLOR_UNLOCKED
        for i, x, y, z in self._connection.transfer(data):
            self.surface[i].worldPosition = x, y, z
            self.surface.lock(i).color = COLOR_LOCKED

        #try:
        #    i, x, y, z = d1
        #    self.surface[i].worldPosition = x, y, z
        #    self.surface.lock(i)
        #except TypeError:
        #    pass
        #try:
        #    i, x, y, z = d2
        #    self.surface[i].worldPosition = x, y, z
        #    self.surface,lock(i)
        #except TypeError:
        #    pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_grabbing(self, states):
        states['hand'].grab_strength = states['leap_hand'].grab_strength


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_grab(self, states):
        left    = states['left_hand']
        right   = states['right_hand']
        grabbed = False

        try:
            left_grab = left.grab_strength
            right_grab = right.grab_strength
        except AttributeError:
            return

        # If both hands are pinching with thumb and middle
        #if (distance(left.thumb.position,
        #             left.middle.position) < PINCH_FINGERS_DISTANCE and
        #    distance(right.thumb.position,
        #             right.middle.position) < PINCH_FINGERS_DISTANCE):
        if (left_grab  >= GRAB_STRENGTH and
            right_grab >= GRAB_STRENGTH):

                left.hide(all_except=('thumb'))
                right.hide(all_except=('thumb'))
                left.thumb.color = right.thumb.color = COLOR_ROTATE_PINCH_OKAY

                lpos = left.thumb.position
                rpos = right.thumb.position
                curr_grabbed_line = Vec3.from_line(lpos[0], lpos[1], lpos[2],
                                                   rpos[0], rpos[1], rpos[2])
                curr_grabbed_line_length = curr_grabbed_line.length
                curr_grabbed_line = curr_grabbed_line.normalize()

                # If previous orientation line has a vector
                if self._prev_grabbed_line:
                    grabbed = True
                    rotation = rotation_matrix_from_vectors(self._prev_grabbed_line,
                                                            curr_grabbed_line)

                    rotation = Matrix(tuple(rotation)).to_euler()
                    self.vertex_origo.applyRotation((-rotation[0],
                                                     -rotation[1],
                                                     -rotation[2]))
                    try:
                        scale = 1/(self._prev_grabbed_line_length/curr_grabbed_line_length)
                        self.vertex_origo.worldScale = \
                            [old*new for old, new in zip(self.vertex_origo.worldScale, repeat(scale))]
                    except ZeroDivisionError:
                        pass

                    self.surface.update()

                # Store current line as previous one for the next cycle
                self._prev_grabbed_line = curr_grabbed_line
                self._prev_grabbed_line_length = curr_grabbed_line_length
        # If only one or none of the hands are pinching with thumb and middle
        else:
            left.color = right.color = COLOR_ROTATE_PINCH_BASE
            self._prev_grabbed_line = None

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
                hand.selected_vertices[1].worldPosition = hand.index.position
                surface.update()
                return
            except (TypeError, AttributeError):
                pass

            hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_FAIL

            # Go through all vertices of surfaces
            for i, vertex in enumerate(surface):
                # Check if pinching a vertex
                if (distance(hand.thumb.position,
                             vertex.worldPosition) < PINCH_VERTEX_FINGERS_DISTANCE or
                    distance(hand.index.position,
                             vertex.worldPosition) < PINCH_VERTEX_FINGERS_DISTANCE):
                        try:
                            surface.select(i)
                        except VertexLocked:
                            return
                        # If so edit the vertex's position and stop iterating
                        # TODO: calculate the midpoint between index and thumb
                        hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_OKAY
                        vertex.color = COLOR_GEOMETRY_LITE
                        vertex.worldPosition = hand.index.position
                        hand.selected_vertices = i, vertex
                        surface.update()
                        return
        # If there is no pinch or pinch was released
        else:
            try:
                i, vertex = hand.selected_vertices
                vertex.color = COLOR_GEOMETRY_DARK
                self.surface.deselect(i)
            except (TypeError, AttributeError):
                pass
            hand.selected_vertices = None
            hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_BASE



#------------------------------------------------------------------------------#
application = KibuVR()
