## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.2.112 (20150514)                        ##
##                               File: hand.py                                ##
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
from itertools   import chain
from collections import OrderedDict
from sys         import path as sys_path

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

# Import user modules
from callback import CallbackManager

# Import global level constants
from const import (SIZE_FINGER_THUMB,
                   SIZE_FINGER_INDEX,
                   SIZE_FINGER_MIDDLE,
                   SIZE_FINGER_RING,
                   SIZE_FINGER_PINKY)



#------------------------------------------------------------------------------#
class Finger(CallbackManager):

    # Class level constants
    REFERENCES = 'position', 'scale', 'color'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def position(self):
        return self._object.worldPosition

    @position.setter
    def position(self, value):
        object = self._object
        object.worldPosition = value
        self.execute_callbacks('position')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def color(self):
        return self._object.color

    @color.setter
    def color(self, value):
        object = self._object
        object.color = value
        self.execute_callbacks('color')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, value):
        self._object.localScale = (value,)*3
        self._scale = value
        self.execute_callbacks('scale')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, object, *args, **kwargs):
        super().__init__(valid_references=self.REFERENCES, *args, **kwargs)
        self._scale  = 1.0
        self._object = object
        self.set_states(finger=object)



#------------------------------------------------------------------------------#
class Hand(CallbackManager):

    # Class level constants
    FINGER_CONSTS = [('thumb' , {'leap_type'    : Leap.Finger.TYPE_THUMB,
                                 'scale_factor' : SIZE_FINGER_THUMB}),
                     ('index' , {'leap_type'    : Leap.Finger.TYPE_INDEX,
                                 'scale_factor' : SIZE_FINGER_INDEX}),
                     ('middle', {'leap_type'    : Leap.Finger.TYPE_MIDDLE,
                                 'scale_factor' : SIZE_FINGER_MIDDLE}),
                     ('ring'  , {'leap_type'    : Leap.Finger.TYPE_RING,
                                 'scale_factor' : SIZE_FINGER_RING}),
                     ('pinky' , {'leap_type'    : Leap.Finger.TYPE_PINKY,
                                 'scale_factor' : SIZE_FINGER_PINKY})]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        for finger in self._fingers.values():
            finger.color = value
        self._color = value


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self,
                 finger_creator,
                 init_position,
                 init_factor,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._fingers = fingers = OrderedDict()
        self._names   = set()
        for i, (finger, details) in enumerate(self.FINGER_CONSTS):
            # Create blender object from prototype
            object = Finger(finger_creator(localScale=(details['scale_factor'],)*3,
                                           worldPosition=(init_position + i*init_factor, 0, 0)))

            # Make finger accessible through this hand as a member
            setattr(self, finger, object)

            # Store names as well
            self._names.add(finger)

            # Store fingers to be accessible via leap-types
            fingers[details['leap_type']] = object

        # HACK:
        self.ring._object.setVisible(False, True)
        self.pinky._object.setVisible(False, True)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __iter__(self):
        yield from self._fingers.values()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def fingers_except_thumb(self):
        yield from (self.index, self.middle, self.ring, self.pinky)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def finger_by_leap(self, leap_type):
        return self._fingers[leap_type]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hide(self, name):
        getattr(self, name)._object.setVisible(False, True)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hide_all(self, *exceptions):
        for name in self._names:
            if name not in exceptions:
                getattr(self, name)._object.setVisible(False, True)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show(self, name):
        getattr(self, name)._object.setVisible(True, True)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_all(self, *exceptions):
        # HACK:
        exceptions = set(chain(exceptions, ('ring', 'pinky')))
        for name in self._names:
            if name not in exceptions:
                getattr(self, name)._object.setVisible(True, True)



#------------------------------------------------------------------------------#
class Hands(CallbackManager):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def left(self):
        return self._left


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def right(self):
        return self._right


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, finger_creator, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create both hands
        self._left  = Hand(finger_creator, init_position=-2, init_factor=-2)
        self._right = Hand(finger_creator, init_position= 2, init_factor= 2)

        # Create references to hands, which will be passed as
        # arguments during the execution of callbacks
        self.set_states(left_hand  = self._left,
                        right_hand = self._right)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __iter__(self):
        yield from (self._left, self._right)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_all(self):
        for hand in self:
            hand.show_all()
