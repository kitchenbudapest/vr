## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.7.708 (20150503)                        ##
##                            File: comm_setup.py                             ##
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
from configparser import ConfigParser
from subprocess   import call, check_output


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Read configuration
config = ConfigParser()
with open('config.ini', encoding='utf-8') as file:
    config.read_file(file)



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level constants
SET_DEV = 'sudo ip link set {DEVICE} up'
ADD_DEV = 'sudo ip address add {HOST}/24 dev {DEVICE}'
GET_DEV = 'ip address show dev {DEVICE} scope global to {HOST}'


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level variables
host   = config['Communication']['this_host']
device = (config['Communication']['device'] or
          next(n for n in check_output('ls /sys/class/net', shell=True).split()
                   if n.startswith(b'en')).decode('utf-8'))

#------------------------------------------------------------------------------#
def setup(user_host=None,
          user_device=None,
          user_pass=''):
    return print(user_pass)
    # Create container for setup settings
    settings = {}
    # Check if user specified a host and a network device name
    user_host   = user_host or host
    user_device = user_device or device
    # Start using device
    call(SET_DEV.format(DEVICE=device), shell=True)
    # Set TCP/IP address for device
    call(ADD_DEV.format(HOST=host, DEVICE=device), shell=True)



#------------------------------------------------------------------------------#
def check(user_host=None,
          user_device=None):
    # Check if user specified a host and a network device name
    user_host   = user_host or host
    user_device = user_device or device
    # Show result
    return bool(check_output(GET_DEV.format(HOST=host, DEVICE=device), shell=True))



#------------------------------------------------------------------------------#
if __name__ == '__main__':
    setup()
    check()
