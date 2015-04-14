## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.2.313 (20150414)                        ##
##                             File: callback.py                              ##
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
from collections import OrderedDict

#------------------------------------------------------------------------------#
class CallbackManager:

    # Class level constants
    REFERENCE_ERROR = ('{!r} is not a valid callback '
                       'reference for {.__class__.__name__!r}')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, valid_references=None):
        self._states    = {}
        if valid_references is None:
            self._restricted = False
            self._callbacks  = OrderedDict()
        else:
            self._restricted = True
            self._callbacks  = OrderedDict.fromkeys(valid_references, [])


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def append_callback(self, reference, callback):
        # If reference already has a list of callbacks
        try:
            # Store the new callback
            self._callbacks[reference].append(callback)
        # If reference doesn't have a list of callbacks
        except KeyError:
            # If this manager-object is restricted
            if self._restricted:
                # Tell user, he can't set such reference
                raise KeyError(self.REFERENCE_ERROR.format(reference, self))
            # Create list of callbacks and store the new callback
            self._callbacks[reference] = [callback]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def remove_callback(self, reference, index=-1):
        self._callbacks[reference].pop(index)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def remove_callbacks(self, reference):
        if self._restricted:
            self._callbacks[reference] = []
        else:
            del self._callbacks[reference]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def remove_all_callbacks(self):
        if self._restricted:
            self._callbacks = OrderedDict.fromkeys(self._callbacks.keys(), [])
        else:
            self._callbacks = OrderedDict()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def execute_callback(self, reference, index=-1):
        self._callbacks[reference][index](self._states)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def execute_callbacks(self, reference):
        states = self._states
        for callback in self._callbacks[reference]:
            callback(states)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def execute_all_callbacks(self):
        states = self._states
        for callbacks in self._callbacks.values():
            for callback in callbacks:
                callback(states)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_states(self, **states):
        self._states.update(states)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def del_states(self, *states):
        _states = self._states
        for state in states:
            _states.pop(state, None)
