## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.5.613 (20150501)                        ##
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
GET_DEV = 'ip address show dev {DEVICE}'



#------------------------------------------------------------------------------#
def setup():
    # Create container for setup settings
    settings = {}
    # Check if user specified a network device name
    device = (config['Communication']['device'] or
              next(n for n in check_output('ls /sys/class/net', shell=True).split()
                   if n.startswith(b'en')).decode('utf-8'))
    # Start using device
    call(SET_DEV.format(DEVICE=device), shell=True)
    # Set TCP/IP address for device
    call(ADD_DEV.format(HOST=config['Communication']['this_host'],
                        DEVICE=device), shell=True)
    # Show result
    call(GET_DEV.format(DEVICE=device), shell=True)



#------------------------------------------------------------------------------#
if __name__ == '__main__':
    setup()
