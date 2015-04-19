## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.2.470 (20150419)                        ##
##                      File: pylinmath/linmath_test.py                       ##
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

from linmath import Vec3, Mat4x4

v1 = Vec3(1, 2, 3)
v2 = Vec3(4, 5, 6)
print(v1)
print(v2)
print(v1 + v2)

print(*v1)
print(*v2)
print(tuple(v1), tuple(v2))

for f in v1 + v2:
    print(f)

print(v1, v1.normalize())
print(Vec3.from_line(*(tuple(v1) + tuple(v2))).normalize())

print(v1.x, v1.y, v1.z)

print(Vec3.from_line(x1=1, y2=1).normalize().length)
print(v1.length)

print(v1.reflect(v2).normalize() * 2)

#------------------------------------------------------------------------------#
print('-'*80)

m1 = Mat4x4((-2,  5, 88,  0),
            (56, 17,  9, -1),
            (-1, -1, 78,  9),
            ( 7,  3,  8,  1))
print(m1)

m2 = Mat4x4.identity()
print(m2)
print(m2[0][0], m2[1][1], m2[2][2], m2[3][3])

print(m1 + m2)
print(m1 - m2)

#------------------------------------------------------------------------------#
print('-'*80)

#------------------------------------------------------------------------------#
def rotation_matrix_from_vectors(direction, target_direction):
    v = target_direction.cross_product(direction)
    skew = Mat4x4(( 0.0, -v.z,  v.y,  0.0),
                  ( v.z,  0.0, -v.x,  0.0),
                  (-v.y,  v.x,  0.0,  0.0),
                  ( 0.0,  0.0,  0.0,  0.0))
    try:
        return (Mat4x4.identity() + skew +
                (skew*skew)*((1 - direction*target_direction)/v.length**2))
    except ZeroDivisionError:
        return Mat4x4.identity()



#------------------------------------------------------------------------------#
print(rotation_matrix_from_vectors(Vec3.from_line(-2, 1, 0, 3, -1, 0).normalize(),
                                   Vec3.from_line(-2, -1, 0, 3, 2, 0).normalize()))