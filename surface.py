## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.8.775 (20150505)                        ##
##                              File: surface.py                              ##
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
from itertools import count
from pickle    import dump, load, HIGHEST_PROTOCOL

# Import user modules
from utils import name_of_vertex


#------------------------------------------------------------------------------#
class VertexLocked(Exception): pass
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
class VertexAlreadySelected(Exception): pass
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
class SerialisedDataUnmatched(Exception): pass



#------------------------------------------------------------------------------#
class Surface:

    MESH_INDEX     = 0
    MATERIAL_INDEX = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def position(self):
        return self._object.worldPosition


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def orientation(self):
        return self._object.worldOrientation


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, surface_creator, vertex_creator, base_color):
        self._locked   = {}
        self._selected = {}
        self._surface  = surface_creator#()
        self._vertices = vertex_creator#()

        for vertex in self._vertices.children:
            vertex.color = base_color


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # TODO: Check if self._vertices.children is still a KX_VertexProxy. It is
    #       most probably not => update all the function definition's return signatures
    def __iter__(self) -> 'KX_VertexProxy':
        yield from self._vertices.children


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __getitem__(self, identifier: 'index or name') -> 'KX_VertexProxy':
        return self._vertices.children[identifier]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def update(self):
        self._surface.update()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def selected(self) -> 'tuples of index and KX_VertexProxy pair':
        yield from self._selected.items()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def select(self, identifier: 'index or name') -> 'KX_VertexProxy':
        if identifier in self._locked:
            raise VertexLocked
        if identifier in self._selected:
            raise VertexAlreadySelected
        vertex = self._vertices.children[identifier]
        self._selected[identifier] = vertex
        return vertex


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def deselect(self, identifier: 'index or name') -> 'KX_VertexProxy':
        return self._selected.pop(identifier, None)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def deselect_all(self) -> 'tuple of KX_VertexProxies':
        selected = tuple(self._selected.values())
        self._selected = {}
        return selected


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def locked(self) -> 'tuples of index and KX_VertexProxy pair':
        yield from self._locked.items()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def lock(self, identifier: 'index or name') -> 'KX_VertexProxy':
        vertex = self._vertices.children[identifier]
        self._locked[identifier] = vertex
        return vertex


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def unlock(self, identifier: 'index or name') -> 'KX_VertexProxy':
        return self._locked.pop(identifier, None)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def unlock_all(self) -> 'tuple of KX_VertexProxies':
        locked = tuple(self._locked.values())
        self._locked = {}
        return locked


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def serialise(self) -> 'list':
        coords = []
        vertices_children = self._vertices.children
        try:
            for i in count():
                coords.extend(vertices_children[name_of_vertex(i)].localPosition)
        except KeyError:
            return coords


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def deserialise(self, coords):
        vertices_children = self._vertices.children
        try:
            for i, coord in enumerate(zip(*(iter(coords),)*3)):
                vertices_children[name_of_vertex(i)].localPosition = coord
        except KeyError:
            raise SerialisedDataUnmatched
