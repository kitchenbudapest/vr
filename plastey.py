#!/usr/bin/env python3
## INFO ########################################################################
##                                                                            ##
##                                  plastey                                   ##
##                                  =======                                   ##
##                                                                            ##
##      Oculus Rift + Leap Motion + Python 3 + C + Blender + Arch Linux       ##
##                       Version: 0.1.8.772 (20150505)                        ##
##                              File: plastey.py                              ##
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
from subprocess   import Popen, PIPE
from configparser import ConfigParser
from tkinter      import (Tk,
                          Toplevel,
                          Label,
                          Entry,
                          Button,
                          Radiobutton,
                          StringVar,
                          BooleanVar,
                          TOP,
                          BOTH,
                          CENTER,
                          W as WEST,
                          E as EAST,
                          NW as NORTH_WEST)

# Import plastey modules
from comm_setup import setup, check, CommunicationSetupError

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Read configuration
config = ConfigParser()
with open('config.ini', encoding='utf-8') as file:
    config.read_file(file)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Module level constants
MODE_SINGLE_PLAYER   = False
MODE_MULTI_PLAYER    = True
BASE_OPENED_GEOMETRY = False
BASE_CLOSED_GEOMETRY = True
COMM_SOCKET_CLIENT   = False
COMM_SOCKET_SERVER   = True
COMM_THIS_HOST       = config['Communication']['this_host']
COMM_THIS_PORT       = config['Communication']['this_port']
COMM_OTHER_HOST      = config['Communication']['other_host']
COMM_OTHER_PORT      = config['Communication']['other_port']
ADDR_NO_ADDRESS      = 'Address not bound.'
ADDR_HAVE_ADDRESS    = 'Address bound.'
CONN_NOT_CONNECTED   = 'Disconnected.'
CONN_CONNECTED       = 'Connected.'
GUI_PAD_X            = 16
GUI_PAD_Y            = GUI_PAD_X
GUI_SECTION_PAD_X    = 32
GUI_SECTION_PAD_Y    = GUI_SECTION_PAD_X
DRAW_FULL_SCREEN     = bool(eval(config['Render']['full_screen']))
DRAW_DISPLAY_X       = int(config['Render']['display_x'])
DRAW_DISPLAY_Y       = int(config['Render']['display_y'])
DRAW_RESOLUTION_X    = int(config['Render']['resolution_x'])
DRAW_RESOLUTION_Y    = int(config['Render']['resolution_y'])

# Set external module level constants
with open('WARNING', encoding='utf-8') as file:
    WARN_TEXT = file.read()


#------------------------------------------------------------------------------#
class Report(Toplevel):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, message, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)

        Label(master = self,
              text   = message).pack()
        Button(master  = self,
               text    = 'OK',
               command = self.destroy)


#------------------------------------------------------------------------------#
class Password(Toplevel):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def on_return(self):
        return self._on_return
    @on_return.setter
    def on_return(self, value):
        self._on_return = value


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, string_var, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)

        self.wm_title('SUDO Password')

        Label(master = self,
              text   = 'Root password:').pack()

        self._input = input = Entry(master = self,
                                    show   = '*')

        def set_pass(*args, **kwargs):
            string_var.set(input.get())
            self.destroy()

        input.bind('<KeyRelease-Return>', set_pass)
        #input.pack(side=TOP, fill=BOTH, expand=True)
        input.pack()
        input.focus_set()

        Button(master  = self,
               text    = 'Cancel',
               command = self.destroy).pack()

        Button(master  = self,
               text    = 'OK',
               command = set_pass).pack()



#------------------------------------------------------------------------------#
class Plastey(Tk):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.wm_title('Plastey Configurator')

        # Create GUI driven variables
        self._mode       = BooleanVar()
        self._base       = BooleanVar()
        self._comm       = BooleanVar()
        self._pass       = StringVar()
        self._addressed  = StringVar()
        self._connected  = StringVar()
        self._this_host  = StringVar()
        self._this_port  = StringVar()
        self._other_host = StringVar()
        self._other_port = StringVar()

        # Create GUI
        self._build_gui()

        # Set default values for GUI driven variables
        self._mode.set(MODE_SINGLE_PLAYER)
        self._base.set(BASE_OPENED_GEOMETRY)
        self._comm.set(COMM_SOCKET_SERVER)
        self._pass.set('')
        self._addressed.set(ADDR_HAVE_ADDRESS if check(COMM_THIS_HOST) else ADDR_NO_ADDRESS)
        self._connected.set(CONN_NOT_CONNECTED)
        self._this_host.set(COMM_THIS_HOST)
        self._this_port.set(COMM_THIS_PORT)
        self._other_host.set(COMM_THIS_HOST)
        self._other_port.set(COMM_OTHER_PORT)

        # Follow changes on password
        self._pass.trace('w', self._on_bind_address)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui(self):
        # Create GUI sections
        row = 0
        col = 0

        # Warning text
        Label(master  = self,
              text    = WARN_TEXT,
              anchor  = WEST,
              justify = CENTER).grid(row     = row,
                                     column  = col,
                                     sticky  = NORTH_WEST,
                                     rowspan = 16)

        # Set column spacing
        self.columnconfigure(index = col,
                             pad   = GUI_SECTION_PAD_X)
        row  = 0
        col += 1

        # Game mode options
        Label(master = self,
              text   = 'Game Mode:').grid(row    = row,
                                          column = col,
                                          sticky = WEST)
        row += 1
        Radiobutton(master   = self,
                    text     = 'Single Player',
                    value    = MODE_SINGLE_PLAYER,
                    variable = self._mode).grid(row    = row,
                                                column = col,
                                                sticky = WEST)
        row += 1
        Radiobutton(master   = self,
                    text     = 'Multi Player',
                    value    = MODE_MULTI_PLAYER,
                    variable = self._mode).grid(row    = row,
                                                column = col,
                                                sticky = WEST)
        row += 1

        # Base object modes
        Label(master = self,
              text   = 'Base Object:').grid(row    = row,
                                            column = col,
                                            sticky = WEST)
        row += 1
        Radiobutton(master   = self,
                    text     = 'Plane mesh',
                    value    = BASE_OPENED_GEOMETRY,
                    variable = self._base).grid(row    = row,
                                                column = col,
                                                sticky = WEST)
        row += 1
        Radiobutton(master   = self,
                    text     = 'Sphere mesh',
                    value    = BASE_CLOSED_GEOMETRY,
                    variable = self._base).grid(row    = row,
                                                column = col,
                                                sticky = WEST)
        row += 1

        # Start oculus-daemon
        Label(master = self,
              text   = 'Daemons:').grid(row    = row,
                                        column = col,
                                        sticky = WEST)
        row += 1
        Button(master  = self,
               text    = 'Start OVRD',
               command = self._on_start_oculus_daemon).grid(row    = row,
                                                            column = col,
                                                            sticky = WEST)

        # Set column spacing
        self.columnconfigure(index = col,
                             pad   = GUI_SECTION_PAD_X)
        row  = 0
        col += 1

        # Multiplayer mode options
        Label(master = self,
              text   = 'Multi Player Options:').grid(row        = row,
                                                     column     = col,
                                                     sticky     = WEST,
                                                     columnspan = 2)
        row += 1

        Label(master = self,
              text   = 'This role:').grid(row    = row,
                                          column = col,
                                          sticky = WEST)
        Radiobutton(master   = self,
                    text     = 'Server',
                    value    = COMM_SOCKET_SERVER,
                    variable = self._comm).grid(row    = row,
                                                column = col + 1,
                                                sticky = WEST)
        row += 1
        Radiobutton(master   = self,
                    text     = 'Client',
                    value    = COMM_SOCKET_CLIENT,
                    variable = self._comm).grid(row    = row,
                                                column = col + 1,
                                                sticky = WEST)
        row += 1

        Label(master = self,
              text   = 'This host:').grid(row    = row,
                                          column = col,
                                          sticky = WEST)
        Entry(master       = self,
              textvariable = self._this_host).grid(row    = row,
                                                   column = col + 1,
                                                   sticky = WEST)
        row += 1
        Label(master = self,
              text   = 'This port:').grid(row    = row,
                                          column = col,
                                          sticky = WEST)
        Entry(master       = self,
              textvariable = self._this_port).grid(row    = row,
                                                   column = col + 1,
                                                   sticky = WEST)
        row += 1

        Label(master = self,
              text   = 'Other host:').grid(row    = row,
                                           column = col,
                                           sticky = WEST)
        Entry(master       = self,
              textvariable = self._other_host).grid(row    = row,
                                                    column = col + 1,
                                                    sticky = WEST)
        row += 1
        Label(master = self,
              text   = 'Other port:').grid(row    = row,
                                           column = col,
                                           sticky = WEST)
        Entry(master       = self,
              textvariable = self._other_port).grid(row    = row,
                                                    column = col + 1,
                                                    sticky = WEST)
        row += 1

        Button(master  = self,
               text    = 'Bind address',
               command = self._on_ask_password).grid(row        = row,
                                                     column     = col,
                                                     sticky     = WEST + EAST)
        Label(master       = self,
              textvariable = self._addressed).grid(row    = row,
                                                   column = col + 1,
                                                   sticky = WEST)
        row += 1
        Button(master  = self,
               text    = 'Connect machines',
               command = self._on_bind_address).grid(row        = row,
                                                     column     = col,
                                                     sticky     = WEST + EAST)
        Label(master       = self,
              textvariable = self._connected).grid(row    = row,
                                                   column = col + 1,
                                                   sticky = WEST)

        # Set column spacing
        self.columnconfigure(index = col + 1,
                             pad   = GUI_SECTION_PAD_X)
        row  = 0
        col += 2

        # Controller buttons
        Label(master = self,
              text   = 'Controllers:').grid(row    = row,
                                            column = col,
                                            sticky = WEST)
        row += 1

        Button(master  = self,
               text    = 'Start game',
               command = self._on_start_game).grid(row    = row,
                                                   column = col,
                                                   sticky = WEST + EAST)
        row += 1
        Button(master  = self,
               text    = 'Save last mesh',
               command = self._on_save_mesh).grid(row    = row,
                                                  column = col,
                                                  sticky = WEST + EAST)
        row += 1
        Button(master  = self,
               text    = 'Load last mesh',
               command = self._on_load_mesh).grid(row    = row,
                                                  column = col,
                                                  sticky = WEST + EAST)
        row += 1
        Button(master  = self,
               text    = 'Save log file',
               command = self._on_save_log).grid(row     = row,
                                                  column = col,
                                                  sticky = WEST + EAST)
        row += 1


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_ask_password(self, *args, **kwargs):
        # Create a password-dialog
        self._dialog = Password(self._pass)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_start_oculus_daemon(self, *args, **kwargs):
        print('starting daemon...')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_bind_address(self, *args, **kwargs):
        # Check for status and if address is not bound
        if not check(COMM_THIS_HOST):
            # Bind address
            try:
                setup(self._this_host, user_pass=self._pass.get())
            except CommunicationSetupError as exception:
                Report(exception.error)
            # Check status and report to user
            self._addressed.set(ADDR_HAVE_ADDRESS if check(COMM_THIS_HOST)
                                                  else ADDR_NO_ADDRESS)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_connect(self, *args, **kwargs):
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_start_game(self, *args, **kwargs):
        # HACK: Is this really the best option we have, to get into fullscreen,
        #       other than using the blender's fullscreen option, which will
        #       unfortunately resize the display's resolution??? :(
        window_command = ['sleep 1']
        window_command.append('wmctrl -r :ACTIVE: '
                              '-e 0,{},{},{},{}'.format(DRAW_DISPLAY_X,
                                                        DRAW_DISPLAY_Y,
                                                        DRAW_RESOLUTION_X,
                                                        DRAW_RESOLUTION_Y))
        if DRAW_FULL_SCREEN:
            window_command.append('wmctrl -r :ACTIVE: -b add,fullscreen')

        for command in (' && '.join(window_command),
                        './plastey'):
            Popen(args   = command,
                  shell  = True,
                  stdin  = PIPE,
                  stderr = PIPE,
                  universal_newlines=True)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_save_mesh(self, *args, **kwargs):
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_load_mesh(self, *args, **kwargs):
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_save_log(self, *args, **kwargs):
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        self.mainloop()



#------------------------------------------------------------------------------#
if __name__ == '__main__':
    Plastey().run()
