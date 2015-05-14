## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.2.2.112 (20150514)                        ##
##                               File: const.py                               ##
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
from math         import radians
from configparser import ConfigParser
from os.path      import join, expanduser

# Import blender modules => at the bottom

# Read configuration
config = ConfigParser()
with open('config.ini', encoding='utf-8') as file:
    config.read_file(file)

# Internal details
INT_BLENDER_COUNTER      = config['Internal']['blender_counter']
INT_TEXT_INTERVAL        = float(config['Internal']['message_interval'])
INT_AUTO_SAVE_INTERVAL   = float(config['Internal']['auto_save_interval'])
INT_TEMPORARY_FOLDER     = expanduser(config['Internal']['temp_base_dir'])
INT_PERMANENT_FOLDER     = expanduser(config['Internal']['permanent_save_dir'])
INT_TEMP_SAVE_FOLDER     = expanduser(join(INT_TEMPORARY_FOLDER,
                                           config['Internal']['temp_save_folder']))
INT_TEMP_SAVE_FILE       = join(INT_TEMP_SAVE_FOLDER,
                                config['Internal']['temp_save_file'])
INT_AUTO_SAVE_FOLDER     = expanduser(join(INT_TEMPORARY_FOLDER,
                                           config['Internal']['temp_auto_save_dir']))
INT_AUTO_SAVE_FILE       = join(INT_AUTO_SAVE_FOLDER,
                                config['Internal']['temp_auto_save_file'])
#INT_STATE_SHUT_DOWN      = join(config['Internal']['temp_base_dir'],
#                                config['Internal']['temp_states'],
#                                config['Internal']['state_shut_down'])
#INT_STATE_RESTART        = join(config['Internal']['temp_base_dir'],
#                                config['Internal']['temp_states'],
#                                config['Internal']['state_restart'])
#INT_STATE_RECOVER_AUTO   = join(config['Internal']['temp_base_dir'],
#                                config['Internal']['temp_states'],
#                                config['Internal']['state_recover_auto'])
#INT_STATE_DONE           = join(config['Internal']['temp_base_dir'],
#                                config['Internal']['temp_feedbacks'],
#                                config['Internal']['state_done'])

WINDOW_FULL_SCREEN       = bool(eval(config['Render']['full_screen']))
WINDOW_DISPLAY_X         = int(config['Render']['display_x'])
WINDOW_DISPLAY_Y         = int(config['Render']['display_y'])
WINDOW_RESOLUTION_X      = int(config['Render']['resolution_x'])
WINDOW_RESOLUTION_Y      = int(config['Render']['resolution_y'])

# Application constants
APP_RUNNING              =  0
APP_ESCAPED              = -1

# Blender object names
OBJ_PROTOTYPE_FINGER     = config['Names']['finger_object']
OBJ_PROTOTYPE_SURFACE    = config['Names']['armature_object']
OBJ_PROTOTYPE_VERTEX_ALL = config['Names']['armature_control']


# EXPERIMENTAL
OBJ_ARMATURE_CONTROL     = config['Names']['armature_control']
OBJ_ARMATURE             = config['Names']['armature_object']
OBJ_GEOMETRY             = config['Names']['geometry_object']
# EXPERIMENTAL


OBJ_GLOBAL               = config['Names']['logic']
OBJ_DOT                  = config['Names']['dot_object'] + INT_BLENDER_COUNTER
OBJ_TEXT_FIRST           = config['Names']['text_first_object']
OBJ_TEXT_OTHER           = config['Names']['text_other_object']
OBJ_HUD_SCENE            = config['Names']['hud_scene']

# Blender properties
PROP_TEXT_TIMER          = config['Scripts']['var_text_time']

# Communication settings
COMM_IS_PAIRED           = bool(eval(config['Communication']['paired']))
COMM_DEVICE_NAME         = config['Communication']['device']
COMM_THIS_HOST           = config['Communication']['this_host']
COMM_THIS_PORT           = int(config['Communication']['this_port'])
COMM_OTHER_HOST          = config['Communication']['other_host']
COMM_OTHER_PORT          = int(config['Communication']['other_port'])
COMM_IS_MASTER           = bool(eval(config['Communication']['master']))
COMM_RUNNING             =  0
COMM_RESTART             = -1

# Colors
COLOR_GEOMETRY_BASE      = 0.000, 0.448, 0.205, 1.000
COLOR_GEOMETRY_DARK      = 0.000, 0.073, 0.036, 1.000
COLOR_GEOMETRY_LITE      = 0.000, 1.000, 0.448, 1.000

COLOR_FINGER_BASE        = 1.000, 1.000, 1.000, 1.000
COLOR_GRAB_PINCH_BASE    = COLOR_FINGER_BASE
COLOR_GRAB_PINCH_OKAY    = 0.000, 1.000, 0.000, 0.350
COLOR_GRAB_PINCH_FAIL    = 1.000, 0.000, 0.000, 1.000

COLOR_ROTATE_PINCH_BASE  = COLOR_FINGER_BASE
COLOR_ROTATE_PINCH_OKAY  = 0.000, 0.000, 1.000, 1.000

COLOR_GRAB_MOVE_BASE     = COLOR_FINGER_BASE
COLOR_GRAB_MOVE_OKAY     = 1.000, 1.000, 0.000, 1.000

COLOR_LOCKED             = 1.000, 1.000, 0.000, 1.000
COLOR_UNLOCKED           = COLOR_FINGER_BASE

COLOR_SELECTED           = 0.000, 1.000, 1.000, 1.000
COLOR_DESELECTED         = COLOR_FINGER_BASE

# Sizes
SIZE_FINGER_THUMB        = 1.00
SIZE_FINGER_INDEX        = 0.60
SIZE_FINGER_MIDDLE       = 0.70
SIZE_FINGER_RING         = 0.60
SIZE_FINGER_PINKY        = 0.55

# Hardware fine-tuning
LEAP_MULTIPLIER          =  0.1
RIFT_MULTIPLIER          =  10
RIFT_POSITION_SHIFT_Y    = -20
RIFT_POSITION_SHIFT_Z    =  10

try:
    from mathutils import Quaternion
    RIFT_ORIENTATION_SHIFT   = Quaternion((1, 0, 0), radians(80))
except ImportError:
    print('const.py => RIFT_ORIENTATION_SHIFT is not available.\n'
          '(Hint: Failed to load the mathutils module of blender)')
