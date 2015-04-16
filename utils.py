## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.2.357 (20150416)                        ##
##                               File: utils.py                               ##
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

from math import sqrt, acos, degrees
def vec3_rotation(x1, y1, z1,
                  x2, y2, z2):
    return acos(x1*x2 + y1*y2 + z1*z2)



#------------------------------------------------------------------------------#
class vec3:

    @property
    def length(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def from_line(x1, y1, z1, x2, y2, z2) -> 'vec3':
        return vec3(x2 - x1, y2 - y1, z2 - z1)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __iter__(self) -> float:
        yield from (self.x, self.y, self.z)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __repr__(self) -> str:
        return 'vec3(x={0.x:f}, y={0.y:f}, z={0.z:f})'.format(self)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def normalize(self) -> 'vec3':
        length = self.length
        try:
            return vec3(self.x/length, self.y/length, self.z/length)
        except ZeroDivisionError:
            return vec3()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def dot_product(self, other, y=0, z=0) -> float:
        try:
            return self.x*other.x + self.y*other.y + self.z*other.z
        except AttributeError:
            return self.x*other + self.y*y + self.z*z


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def cross_product(self, other, y=0, z=0) -> 'vec3':
        try:
            return vec3(self.y*other.z - other.y*self.z,
                        self.z*other.x - other.z*self.x,
                        self.x*other.y - other.x*self.y)
        except AttributeError:
            return vec3(self.y*z     - y*self.z,
                        self.z*other - z*self.x,
                        self.x*y     - other*self.y)



#------------------------------------------------------------------------------#
class mat4x4:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self,  *values):
        self._values = values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def identity() -> 'mat4x4':
        return mat4x4(1.0, 0.0, 0.0, 0.0,
                      0.0, 1.0, 0.0, 0.0,
                      0.0, 0.0, 1.0, 0.0,
                      0.0, 0.0, 0.0, 1.0)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __len__(self):
        return len(self._values)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __iter__(self):
        yield from self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __add__(self, other) -> 'mat4x4':
        values = []
        for v1, v2 in zip(self, other):
            values.append(v1 + v2)
        return mat4x4(*values)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __mul__(self, other) -> 'mat4x4':
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def scale(self, x, y, z) -> 'mat4x4':
        pass



#------------------------------------------------------------------------------#
def rotation_matrix_from_vectors(direction, target_direction):
    v = target_direction.cross_product(direction)
    s = v.length
    c = direction.dot_product(target_direction)

    skew = mat4x4( 0.0, -v.z,  v.y,  0.0,
                   v.z,  0.0, -v.x,  0.0,
                  -v.y,  v.x,  0.0,  0.0,
                   0.0,  0.0,  0.0,  0.0)

    n = (1 - c) / s**2
    result = mat4x4.identity() + skew + (skew*skew).scale(*(n,)*3)



#------------------------------------------------------------------------------#
print(rotation_matrix_from_vectors(vec3.from_line(-2, 1, 0, 3, -1, 0).normalize(),
                                   vec3.from_line(-2, -1, 0, 3, 2, 0).normalize()))
