## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.2.112 (20150514)                        ##
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
from os.path    import join
from select     import select
from threading  import Thread
from math       import radians
from datetime   import datetime
from subprocess import Popen, PIPE
from queue      import Queue, Empty
from os         import makedirs, listdir
from pickle     import dump, HIGHEST_PROTOCOL
from sys        import path as sys_path, stderr, stdin

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

# Import oculus modules
import oculus

# Import blender modules
import bge
from mathutils import Vector, Matrix, Euler, Quaternion

# Import user modules
from hud      import Text
from hand     import Hands
from surface  import Surface
from callback import CallbackManager
from utils    import save_to_file, load_from_file

# Import global level constants
from const import (INT_TEMP_SAVE_FILE,
                   INT_AUTO_SAVE_FILE,
                   INT_TEXT_INTERVAL,
                   INT_AUTO_SAVE_INTERVAL,
                   INT_TEMPORARY_FOLDER,
                   INT_PERMANENT_FOLDER,
                   INT_AUTO_SAVE_FOLDER,
                   INT_TEMP_SAVE_FOLDER,
                   WINDOW_FULL_SCREEN,
                   WINDOW_DISPLAY_X,
                   WINDOW_DISPLAY_Y,
                   WINDOW_RESOLUTION_X,
                   WINDOW_RESOLUTION_Y,
                   APP_RUNNING,
                   APP_ESCAPED,
                   OBJ_PROTOTYPE_FINGER,
                   OBJ_PROTOTYPE_SURFACE,
                   OBJ_PROTOTYPE_VERTEX_ALL,

                   OBJ_ARMATURE_CONTROL,
                   OBJ_ARMATURE,
                   OBJ_GEOMETRY,

                   OBJ_GLOBAL,
                   OBJ_DOT,
                   OBJ_TEXT_FIRST,
                   OBJ_TEXT_OTHER,
                   OBJ_HUD_SCENE,
                   PROP_TEXT_TIMER,
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
S_KEY           = bge.events.SKEY
R_KEY           = bge.events.RKEY
L_KEY           = bge.events.LKEY
HOME_KEY        = bge.events.HOMEKEY
SPACE_KEY       = bge.events.SPACEKEY
ESCAPE_KEY      = bge.events.ESCKEY
BACK_SPACE_KEY  = bge.events.BACKSPACEKEY
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
    def text(self):
        return self._text

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

        # Place the window
        window_command = ['sleep 1']
        window_command.append('wmctrl -r :ACTIVE: '
                              '-e 0,{},{},{},{}'.format(WINDOW_DISPLAY_X,
                                                        WINDOW_DISPLAY_Y,
                                                        WINDOW_RESOLUTION_X,
                                                        WINDOW_RESOLUTION_Y))
        if WINDOW_FULL_SCREEN:
            window_command.append('wmctrl -r :ACTIVE: -b add,fullscreen')

        Popen(args   = ' && '.join(window_command),
              shell  = True,
              stdin  = PIPE,
              stderr = PIPE,
              universal_newlines=True)

        # Create folder structures if they don't exists yet
        makedirs(INT_TEMPORARY_FOLDER,  exist_ok=True)
        makedirs(INT_PERMANENT_FOLDER,  exist_ok=True)
        makedirs(INT_TEMP_SAVE_FOLDER,  exist_ok=True)
        makedirs(INT_AUTO_SAVE_FOLDER,  exist_ok=True)

        ## Start input-daemon
        #self._lines_queue = Queue()
        #def get_input():
        #    print('start')
        #    for line in iter(stdin.readline, ''):
        #        print('try')
        #        self._lines_queue.put(line)
        #    print('stop')
        #    stdin.close()

        #Thread(name   = 'inputd',
        #       target = get_input).start()
        #self._should_restart   = False
        #self._should_shut_down = False

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
        self._leap_controller = leap_controller = Leap.Controller()
        # Create a new instance of the oculus-rift controller
        self._rift_controller = oculus.OculusRiftDK2(head_factor =RIFT_MULTIPLIER,
                                                     head_shift_y=RIFT_POSITION_SHIFT_Y,
                                                     head_shift_z=RIFT_POSITION_SHIFT_Z)

        # Enable HMD optimisation
        if MOUNTED_ON_HEAD:
            leap_controller.set_policy(Leap.Controller.POLICY_OPTIMIZE_HMD)
        ## Enable circle gesture
        #leap_controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        ## Configure circle gesture
        #leap_controller.config.set("Gesture.Circle.MinRadius", 100.0)
        #leap_controller.config.set("Gesture.Circle.MinArc", radians(359))
        ## Configure swipe gesture
        #leap_controller.config.set("Gesture.Swipe.MinLength", 200.0)
        #leap_controller.config.set("Gesture.Swipe.MinVelocity", 750)
        #leap_controller.config.save()

        # Create a reference to the blender scene
        self._blender_scene = blender_scene = bge.logic.getCurrentScene()
        bge.logic.addScene(OBJ_HUD_SCENE, 1)
        # HUD scene has to be set up
        self._preprocess = True

        # Make references to blender objects
        self._camera = blender_scene.active_camera
        self._origo  = blender_scene.objects[OBJ_GLOBAL]

        # Create hands
        self._hands = Hands(self._prototype_creator(OBJ_PROTOTYPE_FINGER))

        # Create surface blender object from prototype and
        # store its reference inside a Surface instance
        # HACK: Surface arguments should be protoype_creator methods, instead of
        #       actual objects, but right now, prototyping the surface object
        #       with its armature and all bones are not copying.. or something
        #       like that..
        self._surface = Surface(blender_scene.objects[OBJ_PROTOTYPE_SURFACE],
                                blender_scene.objects[OBJ_PROTOTYPE_VERTEX_ALL],
                                COLOR_GEOMETRY_DARK)

        # TODO: fake casted shadow with negative lamp:
        #       https://www.youtube.com/watch?v=iJUlqwKEdVQ

        # HACK: yuck.. this is getting out of hands now :(:(:(
        self._vertex_origo = blender_scene.objects[OBJ_PROTOTYPE_VERTEX_ALL]

        # EXPERIMENTAL
        self._armature_control = blender_scene.objects[OBJ_ARMATURE_CONTROL]
        self._armature         = blender_scene.objects[OBJ_ARMATURE]
        self._geometry         = blender_scene.objects[OBJ_GEOMETRY]
        # EXPERIMENTAL

        # Set position setter
        # If DESK
        if mounted_on_desk:
            self._positioner = self._positioner_on_desk
            self._selector   = self._select_right_hand_on_desk
        # If HEAD
        else:
            self._positioner = self._positioner_on_head
            self._selector   = self._select_right_hand_on_head

        # Last time saved
        self._auto_save_time = self._origo[PROP_TEXT_TIMER]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def reset_view(self):
        orientation = Matrix(((1.0, 0.0, 0.0),
                              (0.0, 1.0, 0.0),
                              (0.0, 0.0, 1.0)))
        self._armature_control.worldOrientation = orientation
        self._armature.worldOrientation = orientation
        self._vertex_origo.worldScale = 1, 1, 1
        self._surface.update()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def save(self):
        # Save created mesh
        file_path = INT_TEMP_SAVE_FILE.format(datetime.now())
        save_to_file(path=file_path, data=self._surface.serialise())
        print('[OKAY] file has been saved to:', file_path)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load(self):
        try:
            file_path = join(INT_TEMP_SAVE_FOLDER,
                             next(reversed(sorted(listdir(INT_TEMP_SAVE_FOLDER)))))
            self._surface.deserialise(load_from_file(file_path))
            print('[OKAY] file has been loaded from:', file_path)
        except StopIteration:
            print('[FAIL] there is no file in:', INT_TEMP_SAVE_FOLDER)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def auto_save(self):
        current_time = self._origo[PROP_TEXT_TIMER]
        if self._auto_save_time + INT_AUTO_SAVE_INTERVAL <= current_time:
            # Update last-time checked value
            self._auto_save_time = current_time
            # Save created mesh
            save_to_file(path=INT_AUTO_SAVE_FILE,
                         data=self._surface.serialise())
            print('[OKAY] file has been auto-saved to:', INT_AUTO_SAVE_FILE)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def recover_from_auto_save(self):
        self._auto_save_time = self._origo[PROP_TEXT_TIMER]
        self._surface.deserialise(load_from_file(INT_AUTO_SAVE_FILE))
        print('[OKAY] file has been recovered from:', INT_AUTO_SAVE_FILE)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __call__(self):
        # HACK: The ugliest hack I've ever done...
        if self._preprocess:
            try:
                # Set HUD scene
                self._blender_overlay_scene = bge.logic.getSceneList()[1]
                # Stop preprocessing loops
                self._preprocess = False
                # Set text and its details
                text_1st_obj = self._blender_overlay_scene.objects[OBJ_TEXT_FIRST]
                text_nth_obj = self._blender_overlay_scene.objects[OBJ_TEXT_OTHER]
                text_1st_obj.resolution = text_nth_obj.resolution = 10
                # Create HUD messaging system
                self._text = Text(text_first_object=text_1st_obj,
                                  text_other_object=text_nth_obj,
                                  time_getter=lambda: self._origo[PROP_TEXT_TIMER],
                                  interval=INT_TEXT_INTERVAL)
            except IndexError:
                return

        # Try to create backup
        self.auto_save()

        #try:
        #    print('input:', self._lines_queue.get_nowait())
        #except Empty:
        #    pass

        # Ste states
        self.set_states(restart=COMM_RUNNING,
                        escape =APP_RUNNING)
        # If user pressed the space bar => restart game
        if bge.logic.keyboard.events[ESCAPE_KEY] == JUST_ACTIVATED:
            self.set_states(escape=APP_ESCAPED)
        elif bge.logic.keyboard.events[SPACE_KEY] == JUST_ACTIVATED:
            self.set_states(restart=COMM_RESTART)
        elif bge.logic.keyboard.events[R_KEY] == JUST_ACTIVATED:
            self.recover_from_auto_save()
        elif bge.logic.keyboard.events[S_KEY] == JUST_ACTIVATED:
            self.save()
        elif bge.logic.keyboard.events[L_KEY] == JUST_ACTIVATED:
            self.load()
        elif bge.logic.keyboard.events[HOME_KEY] == JUST_ACTIVATED:
            self.reset_view()
        elif bge.logic.keyboard.events[BACK_SPACE_KEY] == JUST_ACTIVATED:
            self._text.clear()

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

        # Update messaging system
        self._text.update()

        # If leap was able to get the frame set finger positions
        selector   = self._selector
        positioner = self._positioner
        try:
            self.execute_all_callbacks()
            #circle_cw = circle_ccw = False
            #for gesture in leap_frame.gestures():
            #    if (gesture.type is Leap.Gesture.TYPE_CIRCLE and
            #        gesture.is_valid and
            #        gesture.state is Leap.Gesture.STATE_STOP):
            #            circle =  Leap.CircleGesture(gesture)
            #            if (circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2):
            #                circle_ccw=True
            #            else:
            #                circle_cw=True
            #self._hands.set_states(circle_cw=circle_cw,
            #                       circle_ccw=circle_ccw)
            for leap_hand in leap_frame.hands:
                hand = selector(leap_hand.is_right)
                # TODO: do I still need to set the states of these?
                hand.set_states(hand=hand,
                                #circle_cw=circle_cw,
                                #circle_ccw=circle_ccw,
                                leap_hand=leap_hand)
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

        # TODO: use `leap_frame.images` as background

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
                position[1] *  LEAP_MULTIPLIER -10)#-25)


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
        self.save()
