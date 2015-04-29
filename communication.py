## INFO ########################################################################
##                                                                            ##
##                                  kibu-vr                                   ##
##                                  =======                                   ##
##                                                                            ##
##        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         ##
##                       Version: 0.1.5.586 (20150429)                        ##
##                           File: communication.py                           ##
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
from itertools    import count
from sys          import getsizeof
from configparser import ConfigParser
from subprocess   import call, check_output
from pickle       import dumps, loads, HIGHEST_PROTOCOL
from socket       import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from errno        import (EISCONN,       # Transport endpoint is already connected
                          EADDRNOTAVAIL) # Cannot assign requested address

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level constants
SET_DEV     = 'sudo ip link set {DEVICE} up'
ADD_DEV     = 'sudo ip address add {HOST}/24 dev {DEVICE}'
AUTO_DEV    = next(n for n in check_output('ls /sys/class/net', shell=True).split()
                     if n.startswith(b'en')).decode('utf-8')



# TODO: instead of pickle use struct => https://docs.python.org/3.4/library/struct.html

#------------------------------------------------------------------------------#
# Helper function
def sizeof_pow2(data):
    s = getsizeof(dumps(data, HIGHEST_PROTOCOL))
    for i in count():
        size = 2**i
        if s <= size:
            return size



#------------------------------------------------------------------------------#
class Socket:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, this_host, this_port, device=None, buffer_size=1024):
        device  = device or AUTO_DEV
        address = this_host, this_port
        self._buffer_size = buffer_size
        call(SET_DEV.format(DEVICE=device), shell=True)
        self._socket = socket(AF_INET, SOCK_STREAM)
        try:
            self._socket.bind(address)
        except OSError as exception:
            if exception.errno != EADDRNOTAVAIL:
                raise exception
            call(ADD_DEV.format(HOST=this_host, DEVICE=device), shell=True)
            self._socket.bind(address)
        print('[ OKAY ] Socket created')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def stop(self):
        self._socket.shutdown(SHUT_RDWR)
        self._socket.close()
        print('[ OKAY ] Socket closed')




#------------------------------------------------------------------------------#
class Server(Socket):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._socket.listen(1)
        print('[ OKAY ] Server is listening')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def connect(self, *args, **kwargs):
        print('[ WAIT ] Server is accepting connection request...')
        self._connection, *rest = self._socket.accept()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def transfer(self, data):
        print('[ WAIT ] Data transfer...')
        self._connection.send(dumps(data, HIGHEST_PROTOCOL))
        return loads(self._connection.recv(self._buffer_size))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def stop(self):
        # If server already has a connection
        try:
            self._connection.shutdown(SHUT_RDWR)
            self._connection.close()
        except AttributeError:
            pass
        super().stop()



#------------------------------------------------------------------------------#
class Client(Socket):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('[ OKAY ] Client is ready')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def connect(self, other_host, other_port):
        print('[ WAIT ] Client is sending connection request...')
        while True:
            try:
                self._socket.connect((other_host, other_port))
            except OSError as exception:
                if exception.errno != EISCONN:
                    raise exception
                return


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def transfer(self, data):
        print('[ WAIT ] Data transfer...')
        self._socket.send(dumps(data, HIGHEST_PROTOCOL))
        data = loads(self._socket.recv(self._buffer_size))
        print('[ OKAY ] Data has been sent')
