## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.0.141 (20150401)                        ##
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
from hand import LeftHand, RightHand



# Module level constants
#------------------------------------------------------------------------------#
THUMB    = Leap.Finger.TYPE_THUMB
INDEX    = Leap.Finger.TYPE_INDEX
MIDDLE   = Leap.Finger.TYPE_MIDDLE
RING     = Leap.Finger.TYPE_RING
PINKY    = Leap.Finger.TYPE_PINKY
FINGERS  = THUMB, INDEX, MIDDLE, RING, PINKY
LEFT     = False
RIGHT    = True
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

    VERSION = '2.0.0'


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, mounted_on):
        # Create a new instance of the leap-motion controller
        self._leap_controller = Leap.Controller()
        # Create a new instance of the oculus-rift controller
        self._rift_controller = oculus.OculusRiftDK2(device_index=0)
        # Create a reference to the blender scene
        self._blender_scene = bge.logic.getCurrentScene()

        # Make references to blender objects
        self._camera  = self._blender_scene.active_camera
        self._surface = Surface(self._blender_scene.objects['surface'].meshes[0])

        self._left_hand  = LeftHand(self._blender_scene)
        self._right_hand = RightHand(self._blender_scene)
        self._hands = {}

        # Set position setter
        # If DESK
        if mounted_on:
            self._hands[LEFT]  = self._right_hand
            self._hands[RIGHT] = self._left_hand
            self.set_position  = self._set_position_on_desk
        # If HEAD
        else:
            self._hands[LEFT]  = self._left_hand
            self._hands[RIGHT] = self._right_hand
            self.set_position  = self._set_position_on_head


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

        # Set finger positions
        set_position = self.set_position
        for hand in leap_frame.hands:
            h = self._hands[hand.is_right]
            for finger in hand.fingers:
                set_position(h, finger.type(), finger.tip_position)

        #for finger in leap_frame.fingers:
        #    set_position(finger.type(), finger.tip_position)

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
    def _set_position_on_head(self, hand, type, position):
        # The USB cable is on the right side and
        # the indicator light is on the top
        hand[type] = (position[0] * -MINIFIER,
                      position[1] *  MINIFIER - 10,
                      position[2] * -MINIFIER + 10)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _set_position_on_desk(self, hand, type, position):
        # The USB cable is on the right side and
        # the indicator light is at the back
        hand[type] = (position[0] *  MINIFIER,
                      position[2] * -MINIFIER,
                      position[1] *  MINIFIER - 10)



#------------------------------------------------------------------------------#
# Create a new game instance
sculptomat = Sculptomat(mounted_on=DESK)




#leap_controller = Leap.Controller()

## Create a container for fingers
#SCENE = bge.logic.getCurrentScene()
#FINGERS = {
#    Leap.Finger.TYPE_THUMB  : SCENE.objects['finger_1_thumb'],
#    Leap.Finger.TYPE_INDEX  : SCENE.objects['finger_2_index'],
#    Leap.Finger.TYPE_MIDDLE : SCENE.objects['finger_3_middle'],
#    Leap.Finger.TYPE_RING   : SCENE.objects['finger_4_ring'],
#    Leap.Finger.TYPE_PINKY  : SCENE.objects['finger_5_pinky'],
#}

#MINIFIER = 0.1

#MATERIAL_INDEX = 0
#SURFACE_MESH = SCENE.objects['surface'].meshes[0]
#SURFACE_MESH_LENGTH = SURFACE_MESH.getVertexArrayLength(MATERIAL_INDEX)



##------------------------------------------------------------------------------#
#def main_loop(blender_controller):
#    # Position fingers based on leap's data

#    OCULUS.poll()
#    OCULUS.rotation


#    frame = leap_controller.frame()
#    for finger in frame.fingers:
#        position = finger.tip_position

#    # Check if user performed a "pick" action
#    if distance(FINGERS[Leap.Finger.TYPE_THUMB].localPosition,
#                FINGERS[Leap.Finger.TYPE_INDEX].localPosition) < 2:
#        # If the "pick" happened near to one of the vertices of the 'surface'
#        for i in range(SURFACE_MESH_LENGTH):
#            vertex = SURFACE_MESH.getVertex(MATERIAL_INDEX, i)
#            # If so, color that vertex to 'red'
#            if (distance(FINGERS[Leap.Finger.TYPE_THUMB].localPosition, vertex.getXYZ()) < 1.5 or
#                distance(FINGERS[Leap.Finger.TYPE_INDEX].localPosition, vertex.getXYZ()) < 1.5):
#                    vertex.color = 1.0, 0.0, 0.0, 1.0  # red
#            # If not change the color back 'white'
#            else:
#                vertex.color = 1.0, 1.0, 1.0, 1.0  # white
