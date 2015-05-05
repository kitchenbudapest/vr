## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.8.761 (20150504)                        ##
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
from subprocess   import Popen, PIPE, call, check_output


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Read configuration
config = ConfigParser()
with open('config.ini', encoding='utf-8') as file:
    config.read_file(file)



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level constants
SET_DEV = 'sudo -S ip link set {DEVICE} up'
ADD_DEV = 'sudo -S ip address add {HOST}/24 dev {DEVICE}'
GET_DEV = 'ip address show dev {DEVICE} scope global to {HOST}'


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level variables
host   = config['Communication']['this_host']
device = (config['Communication']['device'] or
          next(n for n in check_output('ls /sys/class/net', shell=True).split()
                   if n.startswith(b'en')).decode('utf-8'))

#------------------------------------------------------------------------------#
class CommunicationSetupError(Exception):

    def __init__(self, error):
        self.error = error



#------------------------------------------------------------------------------#
def setup(user_host=host,
          user_device=device,
          user_pass=''):
    # Set up device and set TCP/IP address for it
    for command in (SET_DEV.format(DEVICE=device),
                    ADD_DEV.format(HOST=host, DEVICE=device)):
        # Start using device
        _, response = Popen(args   = command,
                            stdin  = PIPE,
                            stderr = PIPE,
                            shell  = True,
                            universal_newlines = True).communicate(user_pass + '\n')
        if response:
            raise CommunicationSetupError(response)


#------------------------------------------------------------------------------#
def check(user_host=host,
          user_device=device):
    # Show result
    return bool(check_output(GET_DEV.format(HOST=host, DEVICE=device), shell=True))



#------------------------------------------------------------------------------#
if __name__ == '__main__':
    setup()
    check()
