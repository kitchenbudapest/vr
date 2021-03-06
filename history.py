## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.0.933 (20150509)                        ##
##                              File: history.py                              ##
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

from collections import deque


#------------------------------------------------------------------------------#
class History(deque):

    NONE = -1
    UNDO =  0
    REDO =  1
    UNDO_PREFIX = '[UNDO] '
    REDO_PREFIX = '[REDO] '
    NONE_PREFIX = ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def event(function):
        return lambda direction, prefix: function(direction, prefix)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, function_if_empty, max_size=64, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = 0
        self._empty = function_if_empty
        # Set memory limit
        max_len = self.maxlen
        if (max_len is not None and
            max_size <= max_len):
            self._max_size = max_len
        else:
            self._max_size = max_size


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def push(self, undo, redo):
        after_undo = False
        # If there was an undo before
        for i in range(self._index + 1, len(self)):
            after_undo = True
            self.pop()
        # If hit the memory limit
        if len(self) >= self._max_size:
            self.popleft()
        # If this is after an undo call
        elif after_undo:
            self._index += 2
        # If this is npot after an undo call
        # nor hit the memory limit
        else:
            self._index += 1
        # Finally add the new element
        self.append((undo, redo))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def do(self):
        try:
            self[self._index][self.REDO](self.NONE, self.NONE_PREFIX)
        except IndexError:
            self._empty(self.NONE, self.NONE_PREFIX)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def undo(self):
        try:
            self._index -= 1
            self[self._index][self.UNDO](self.UNDO, self.UNDO_PREFIX)
        except IndexError:
            self._empty(self.UNDO, self.UNDO_PREFIX)
            self._index = 0


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def redo(self):
        try:
            self._index += 1
            self[self._index][self.REDO](self.REDO, self.REDO_PREFIX)
        except IndexError:
            self._empty(self.REDO, self.REDO_PREFIX)
            self._index = 0
