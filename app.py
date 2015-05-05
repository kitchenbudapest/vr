## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.8.826 (20150505)                        ##
##                                File: app.py                                ##
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
from datetime import datetime
from pickle   import dump, HIGHEST_PROTOCOL
from sys      import path as sys_path, stderr

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

# Import oculus modules
import oculus

# Import blender modules
import bge
from mathutils import Vector, Matrix, Euler, Quaternion

# Import user modules
from hand     import Hands
from surface  import Surface
from callback import CallbackManager
from utils    import save_to_file, load_from_file

# Import global level constants
from const import (INT_OUTPUT_FILE,
                   APP_RUNNING,
                   APP_ESCAPED,
                   OBJ_PROTOTYPE_FINGER,
                   OBJ_PROTOTYPE_SURFACE,
                   OBJ_PROTOTYPE_VERTEX_ALL,
                   OBJ_GLOBAL,
                   OBJ_DOT,
                   COLOR_GEOMETRY_DARK,
                   LEAP_MULTIPLIER,
                   RIFT_MULTIPLIER,
                   RIFT_POSITION_SHIFT_Y,
                   RIFT_POSITION_SHIFT_Z,
                   RIFT_ORIENTATION_SHIFT,
                   COMM_IS_PAIRED,
                   COMM_DEVICE_NAME,
                   COMM_THIS_HOST,
                   COMM_THIS_PORT,
                   COMM_OTHER_HOST,
                   COMM_OTHER_PORT,
                   COMM_IS_MASTER,
                   COMM_RUNNING,
                   COMM_RESTART)

# Import conditional user modules
if COMM_IS_PAIRED:
    if COMM_IS_MASTER:
        from communication import sizeof_pow2, Server as Connection
    else:
        from communication import sizeof_pow2, Client as Connection
    # Conditional module level constant
    BUFFER_SIZE = sizeof_pow2([(int(), float(), float(), float()),
                               (int(), float(), float(), float())])

# TODO: make build-script work :)
# Import cutils modules => versioning
#import build



# Module level constants
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
MOUNTED_ON_HEAD = 0
MOUNTED_ON_DESK = 1
# Local references of blender constants
SPACE_KEY       = bge.events.SPACEKEY
ESCAPE_KEY      = bge.events.ESCKEY
JUST_ACTIVATED  = bge.logic.KX_INPUT_JUST_ACTIVATED



#------------------------------------------------------------------------------#
class RestartApplication(Exception): pass
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
class EscapeApplication(Exception): pass



#------------------------------------------------------------------------------#
class Application(CallbackManager):

    # NOTE: local->global: http://blenderartists.org/forum/archive/index.php/t-180690.html

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def hands(self):
        return self._hands

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def surface(self):
        return self._surface

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def vertex_origo(self):
        return self._vertex_origo


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, mounted_on_desk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove current exit key (make it available for customised setting)
        # HACK: There is no 'NONE_KEY' defined, so setting the escape key to 0
        #       could cause undefined behaviour, as it is undocomunted. During
        #       the tests, this setting did not activate any of the keys, so it
        #       is a working work-around. (At least on Arch Linux)
        bge.logic.setExitKey(0)

        try:
            # Create connection
            self._connection = Connection(this_host=COMM_THIS_HOST,
                                          this_port=COMM_THIS_PORT,
                                          buffer_size=BUFFER_SIZE,
                                          device=COMM_DEVICE_NAME)
            self._connection.connect(other_host=COMM_OTHER_HOST,
                                     other_port=COMM_OTHER_PORT)
        # If connection is not imported
        except NameError:
            pass
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

        # Create hands
        self._hands = Hands(self._prototype_creator(OBJ_PROTOTYPE_FINGER))

        # Create surface blender object from prototype and
        # store its reference inside a Surface instance
        # HACK: Surface arguments should be protoype_creator methods, instead of
        #       actual objects, but right now, prototyping the surface object
        #       with its armature and all bones are not copying.. or something
        #       like that..
        self._surface = Surface(self._blender_scene.objects[OBJ_PROTOTYPE_SURFACE],
                                self._blender_scene.objects[OBJ_PROTOTYPE_VERTEX_ALL],
                                COLOR_GEOMETRY_DARK)

        # TODO: fake casted shadow with negative lamp:
        #       https://www.youtube.com/watch?v=iJUlqwKEdVQ

        # HACK: yuck.. this is getting out of hands now :(:(:(
        self._vertex_origo = self._blender_scene.objects[OBJ_PROTOTYPE_VERTEX_ALL]

        # Set position setter
        # If DESK
        if mounted_on_desk:
            self._positioner = self._positioner_on_desk
            self._selector   = self._select_right_hand_on_desk
        # If HEAD
        else:
            self._positioner = self._positioner_on_head
            self._selector   = self._select_right_hand_on_head


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __call__(self):
        self.set_states(restart=COMM_RUNNING,
                        escape =APP_RUNNING)
        # If user pressed the space bar => restart game
        if bge.logic.keyboard.events[ESCAPE_KEY] == JUST_ACTIVATED:
            self.set_states(escape=APP_ESCAPED)
        elif bge.logic.keyboard.events[SPACE_KEY] == JUST_ACTIVATED:
            self.set_states(restart=COMM_RESTART)

        # Get current values of oculus-rift
        rift_frame = self._rift_controller.frame()
        # Get current values of the leap-motion
        leap_frame = self._leap_controller.frame()

        # Set camera position and orientation
        #self._camera.worldPosition = rift_frame.position
        #self._camera.worldOrientation = \
        #    RIFT_ORIENTATION_SHIFT*Quaternion(rift_frame.orientation)

        # If leap was unable to get a proper frame
        if not leap_frame.is_valid:
            return print('(leap) Invalid frame', file=stderr)

        # If leap was able to get the frame set finger positions
        selector   = self._selector
        positioner = self._positioner
        try:
            self.execute_all_callbacks()
            for leap_hand in leap_frame.hands:
                hand = selector(leap_hand.is_right)
                # TODO: do I still need to set the states of these?
                hand.set_states(hand=hand, leap_hand=leap_hand)
                for finger in leap_hand.fingers:
                    # TODO: positioner(*finger.tip_position) => leaking memory and never returns
                    hand.finger_by_leap(finger.type()).position = positioner(finger.tip_position)
                hand.execute_all_callbacks()
            self._hands.execute_all_callbacks()
        except EscapeApplication:
            self._clean_up()
            bge.logic.endGame()
        except RestartApplication:
            self._clean_up()
            bge.logic.restartGame()


        # TODO: In the following order should things executed:
        #           1) both hands => it can block a single hand
        #           2) one hand   => it can block a single finger
        #           3) one finger
        #       Try to make the access of data and the execution of callbacks to
        #       a single (optimised) loop if possible

        #print(leap_frame.images)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _select_right_hand_on_head(self, is_left):
        return self._hands.left if is_left else self._hands.right


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _select_right_hand_on_desk(self, is_right):
        return self._hands.right if is_right else self._hands.left


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


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _clean_up(self):
        # Close connection if app is paired
        try:
            self.connection.stop()
        except AttributeError:
            pass
        # Save created mesh
        save_to_file(path=INT_OUTPUT_FILE.format(datetime.now()),
                     data=self._surface.serialise())
        print('[OKAY] a temporary file has been saved')
