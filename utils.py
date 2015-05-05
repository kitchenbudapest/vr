## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.8.737 (20150504)                        ##
##                               File: utils.py                               ##
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
from bz2    import open as bz2_open
from pickle import dumps, loads, HIGHEST_PROTOCOL

# Import user modules
from const import OBJ_DOT

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def index_of_vertex(vertex_name):
    return int(vertex_name.split('.')[-1])


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def name_of_vertex(vertex_index):
    return OBJ_DOT.format(vertex_index)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def save_to_file(path, data):
    with bz2_open(path, mode='wb') as file:
        file.write(dumps(data, protocol=HIGHEST_PROTOCOL))

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def load_from_file(path) -> 'Python object':
    with bz2_open(path, mode='rb') as file:
        return loads(file.read())
