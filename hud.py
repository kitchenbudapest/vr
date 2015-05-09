## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.0.929 (20150509)                        ##
##                                File: hud.py                                ##
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
from collections import deque

#------------------------------------------------------------------------------#
class Text:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, text_first_object,
                       text_other_object,
                       time_getter,
                       interval):
        self._text_first = text_first_object
        self._text_other = text_other_object
        self._get_time   = time_getter
        self._interval   = interval
        self._messages   = deque()
        self._updated    = False
        self._empty      = True


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def update(self):
        # If there are messages in the deque
        try:
            # If last message's time-stamp is older than current time
            if (self._messages[-1][0] + self._interval) <= self._get_time():
                # Remove oldest message and switch the updated-flag
                self._messages.pop()
                self._udpated = True
        # If there is no message left in the deque
        except IndexError:
            if not self._empty:
                self._updated = True
                self._empty   = True

        # If messages were added or removed
        if self._updated:
            # Write the changed and constructed messages to display
            messages = iter(m for _, m in self._messages)
            try:
                self._text_first.text = next(messages)
                self._text_other.text = '\n'.join(messages)
            except StopIteration:
                self._text_first.text = self._text_other.text = ''
            self._updated = False


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write(self, message):
        # Add new message and switch the updated-flag
        self._messages.appendleft((self._get_time(), message))
        self._updated = True
        self._empty   = False
