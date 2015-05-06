## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.8.841 (20150506)                        ##
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
from itertools import repeat, chain
from math import sqrt, radians

# Import blender modules
from mathutils import Matrix

# Import linmath modules
from linmath import Vec3, Mat4x4

# Import user modules
from utils   import (name_of_vertex,
                     index_of_vertex)
from surface import (VertexLocked,
                     VertexAlreadySelected)
from app     import (Application,
                     EscapeApplication,
                     RestartApplication,
                     MOUNTED_ON_DESK,
                     MOUNTED_ON_HEAD)

# Import global level constants
from const import (APP_ESCAPED,
                   COLOR_ROTATE_PINCH_BASE,
                   COLOR_ROTATE_PINCH_OKAY,
                   COLOR_GRAB_PINCH_BASE,
                   COLOR_GRAB_PINCH_FAIL,
                   COLOR_GRAB_PINCH_OKAY,
                   COLOR_GEOMETRY_BASE,
                   COLOR_GEOMETRY_DARK,
                   COLOR_GEOMETRY_LITE,
                   COLOR_LOCKED,
                   COLOR_UNLOCKED,
                   COMM_IS_PAIRED,
                   COMM_IS_MASTER,
                   COMM_RESTART)



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level constants
PICK_HOLD_DISTANCE    = 3.5
PICK_RELEASE_DISTANCE = 2.5
#GRAB_HOLD_DISTANCE    = 3.5
GRAB_RELEASE_DISTANCE = 3.5

ZOOM_SCALE_FACTOR     = 0.1
ROTATE_SCALE_FACTOR   = 0.1



# Helper functions
#------------------------------------------------------------------------------#
def distance(position1, position2):
    return sqrt(pow(position2[0] - position1[0], 2) +
                pow(position2[1] - position1[1], 2) +
                pow(position2[2] - position1[2], 2))


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def midpoint(position1, position2):
    return ((position1[0] + position2[0])/2,
            (position1[1] + position2[1])/2,
            (position1[2] + position2[2])/2)


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

        # Set escape handler
        self.append_callback('exit', self.on_exit)
        self.append_callback('reset', self.on_reset)

        # Set communication
        if COMM_IS_PAIRED:
            self.append_callback('comm', self.on_communication)
            if not COMM_IS_MASTER:
                self.vertex_origo.applyRotation((0, 0, radians(180)))
                self.surface.update()

        # Set initial states
        self._is_picked        = False
        self._grab_position    = None
        self._dual_grab_vector = None
        self._dual_grab_length = None

        # Set callback-states which will be used
        # duyring the execution of the callbacks
        self.hands.left.set_states(grabbed=False)
        self.hands.right.set_states(grabbed=False)

        # Set actual callbacks
        self.hands.append_callback('grab', self.on_grab)
        self.hands.right.append_callback('pick', self.on_pick)
        self.hands.left.append_callback('pick', self.on_pick)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, states):
        if states['escape'] == APP_ESCAPED:
            raise EscapeApplication


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_reset(self, states):
        if states['restart'] == COMM_RESTART:
            raise RestartApplication


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_communication(self, states):
        # Local reference
        surface = self.surface
        # Prepare and send data
        data = []
        for identifier, vertex in surface.selected():
            vertex_position = vertex.localPosition
            data.append((index_of_vertex(vertex.name),
                         vertex_position[0],
                         vertex_position[1],
                         vertex_position[2]))

        # Receive data and act based on it
        for vertex in surface.unlock_all():
            vertex.color = COLOR_UNLOCKED
        try:
            received_data = self._connection.transfer(data)
            for i, x, y, z in received_data:
                vertex_name = name_of_vertex(i)
                surface[vertex_name].localPosition = x, y, z
                surface.lock(vertex_name).color = COLOR_LOCKED
            surface.update()
        # If 'NoneType|int' object is not iterable
        except TypeError:
            if received_data == COMM_RESTART:
                raise RestartApplication


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_grab(self, states):
        grabbing = []
        # Check both hands
        for hand in self.hands:
            thumb_position = hand.thumb.position
            # Check index and middle fingers as well
            for finger in (hand.index,
                           hand.middle):
                # If thumb's and the finger's distance
                # is beyond the grabbing-release-range
                if not distance(thumb_position,
                                finger.position) < GRAB_RELEASE_DISTANCE:
                    # Set state and stop checking the other finger
                    hand.set_states(grabbed=False)
                    break
            # If both fingers are in the range of grabbing-release-range
            else:
                # Set state, and collect hand in the grabbing-hands list
                grabbing.append(hand)
                hand.set_states(grabbed=True)

        # If both hands are grabbing
        try:
            # Get hands separately
            left_hand, right_hand = grabbing
            #  Color thumbs and hide other fingers, so it won't confuse the user
            left_hand.thumb.color = right_hand.thumb.color = COLOR_ROTATE_PINCH_OKAY
            left_hand.hide(all_except=('thumb',))
            right_hand.hide(all_except=('thumb',))
            # Get the thumb positionS
            ltp = left_hand.thumb.position
            rtp = right_hand.thumb.position
            # Get essentaial informations about the current state
            curr_grab_vector = Vec3.from_line(ltp[0], ltp[1], ltp[2],
                                              rtp[0], rtp[1], rtp[2])
            curr_grab_length = curr_grab_vector.length
            curr_grab_vector = curr_grab_vector.normalize()
            # If this grab is part of a previous grab-cycle
            try:
                rotation = Matrix(tuple(rotation_matrix_from_vectors(self._dual_grab_vector,
                                                                     curr_grab_vector))).to_euler()
                # Rotate parent object of all vertices
                self.vertex_origo.applyRotation((-rotation[0],
                                                 -rotation[1],
                                                 -rotation[2]))
                # Scale the parent object
                try:
                    scale = 1/(self._dual_grab_length/curr_grab_length)
                    self.vertex_origo.worldScale = \
                        [old*new for old, new in zip(self.vertex_origo.worldScale, repeat(scale))]
                except ZeroDivisionError:
                    pass
                # Update geometry
                self.surface.update()
            # If this grab is a new grab-cycle
            except TypeError:
                pass
            # Store current values as previous ones for the next cycle
            self._dual_grab_vector = curr_grab_vector
            self._dual_grab_length = curr_grab_length
            print('[ ROTATING ]')
        except ValueError:
            # If only one hand is grabbing
            try:
                curr = tuple(grabbing[0].thumb.position)
                prev = self._grab_position
                # If this grab is part of a previous grab-cycle
                try:
                    # Calculate vector between previous
                    # and current thumb positions
                    movement = Vec3.from_line(prev[0], prev[1], prev[2],
                                              curr[0], curr[1], curr[2])
                    # Move all selected vertices
                    for _, vertex in self.surface.selected():
                        vertex.applyMovement(movement)
                    # Update geometry
                    self.surface.update()
                # If this grab is starting a new grab-cycle
                except TypeError:
                    pass
                # Store current position as previous one for the next cycle
                self._grab_position = curr
                print('[ GRABBING ]')
            # If none of the hands are grabbing
            except IndexError:
                self._grab_position    = \
                self._dual_grab_vector = \
                self._dual_grab_length = None


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_pick(self, states):
        # IF there is a grabbing going on
        if states['grabbed']:
            return
        # Get local reference of this hand
        hand = states['hand']
        # Local reference
        thumb_position = hand.thumb.position
        # Check all fingers
        for finger in hand.fingers_except_thumb():
            # If finger's distance to the thumb is in the picking-release-range
            if distance(thumb_position,
                        finger.position) < PICK_RELEASE_DISTANCE:
                # Local reference
                surface = self.surface
                pick_position = midpoint(thumb_position, finger.position)
                # Check all vertices on the surface
                for vertex in surface:
                    # If vertex's distance to the thumb is in the picking-hold-range
                    if distance(pick_position,
                                vertex.worldPosition) < PICK_HOLD_DISTANCE:
                        # If user is already picking
                        if self._is_picked:
                            return
                        # Try to select vertex
                        try:
                            surface.select(vertex.name)
                            vertex.color = COLOR_GEOMETRY_LITE
                            print('[ SELECTED ] vertex:', vertex.name)
                        # If vertex has been selected by the opponent user
                        except VertexLocked:
                            return
                        except VertexAlreadySelected:
                            # If user already released the previous pick
                            surface.deselect(vertex.name)
                            vertex.color = COLOR_GEOMETRY_BASE
                            print('[DESELECTED] vertex:', vertex.name)
                        # Set state
                        self._is_picked = True
                        # Feedback the user about the pick's state
                        hand.thumb.color = finger.color = COLOR_GRAB_PINCH_OKAY
                        # Stop the iterations
                        return
        # If pick is released
        else:
            # Feedback the user about the pick's state
            hand.thumb.color  = \
            hand.index.color  = \
            hand.middle.color = \
            hand.ring.color   = \
            hand.pinky.color  = COLOR_GRAB_PINCH_BASE
            # Set state
            self._is_picked = False


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
                hand.selected_vertices.worldPosition = hand.index.position
                surface.update()
                return
            except (TypeError, AttributeError):
                pass

            hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_FAIL

            # Go through all vertices of surfaces
            for vertex in surface:
                # Check if pinching a vertex
                if (distance(hand.thumb.position,
                             vertex.worldPosition) < PINCH_VERTEX_FINGERS_DISTANCE or
                    distance(hand.index.position,
                             vertex.worldPosition) < PINCH_VERTEX_FINGERS_DISTANCE):
                        try:
                            surface.select(vertex.name)
                        except VertexLocked:
                            return
                        # If so edit the vertex's position and stop iterating
                        # TODO: calculate the midpoint between index and thumb
                        hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_OKAY
                        vertex.color = COLOR_GEOMETRY_LITE
                        vertex.worldPosition = hand.index.position
                        hand.selected_vertices = vertex
                        surface.update()
                        return
        # If there is no pinch or pinch was released
        else:
            try:
                vertex = hand.selected_vertices
                vertex.color = COLOR_GEOMETRY_DARK
                self.surface.deselect(vertex.name)
            # 'NoneType' object has no attribute 'color'
            except AttributeError:
                pass
            hand.selected_vertices = None
            hand.thumb.color = hand.index.color = COLOR_GRAB_PINCH_BASE



#------------------------------------------------------------------------------#
application = KibuVR()
