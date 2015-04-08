## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.0.212 (20150408)                        ##
##                               File: hand.py                                ##
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
from sys import path as sys_path
from collections import OrderedDict

# Import leap modules
sys_path.insert(0, '/usr/lib/Leap')
import Leap

FINGER_CONSTS = [('thumb' , {'leap_type'    : Leap.Finger.TYPE_THUMB,
                             'scale_factor' : 1.00}),
                 ('index' , {'leap_type'    : Leap.Finger.TYPE_INDEX,
                             'scale_factor' : 0.60}),
                 ('middle', {'leap_type'    : Leap.Finger.TYPE_MIDDLE,
                             'scale_factor' : 0.70}),
                 ('ring'  , {'leap_type'    : Leap.Finger.TYPE_RING,
                             'scale_factor' : 0.60}),
                 ('pinky' , {'leap_type'    : Leap.Finger.TYPE_PINKY,
                             'scale_factor' : 0.55})]

#------------------------------------------------------------------------------#
class Finger:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def position(self):
        return self._object.worldPosition
    @position.setter
    def position(self, value):
        object = self._object
        object.worldPosition = value
        for callback in self._callbacks['position']:
            callback(object)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def color(self):
        return self._object.color
    @color.setter
    def color(self, value):
        object = self._object
        object.color = value
        for callback in self._callbacks['color']:
            callback(object)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, object):
        self._object = object
        self._callbacks = OrderedDict([('position', []),
                                       ('scale'   , []),
                                       ('color'   , [])])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def append_callback(self, reference, function):
        try:
            self._callbacks[reference].append(function)
        except KeyError:
            raise KeyError('Finger object has no callback '
                           'reference {!r}'.format(reference))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def clear_callback(self, reference):
        if reference in self._callbacks:
            self._callbacks[reference] = []



#------------------------------------------------------------------------------#
class Hand:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, finger_creator):
        self._callbacks = OrderedDict()
        self._fingers = fingers = OrderedDict()
        for finger, details in FINGER_CONSTS:
            # Create blender object from prototype
            object = Finger(finger_creator(localScale=(details['scale_factor'],)*3))

            # Make finger accessible through this hand as a member
            setattr(self, finger, object)

            # Store fingers to be accessible via leap-types
            fingers[details['leap_type']] = object


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __repr__(self):
        return ('Hand(thumb={}, index={}, middle={}, '
                'ring={}, pinky={})').format(*self._fingers.values())


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def append_callback(self, reference, callback):
        self._callbacks[reference] = callback


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def clear_callback(self, reference):
        try:
            del self._callbacks[reference]
        except KeyError:
            pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def do_callbacks(self):
        for callback in self._callbacks.values():
            callback(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def do_finger(self, finger_leap_type, **actions):
        finger = self._fingers[finger_leap_type]
        for action, value in actions.items():
            try:
                getattr(finger, action)(value)
            except TypeError:
                setattr(finger, action, value)
