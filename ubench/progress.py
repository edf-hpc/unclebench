#!/usr/bin/python
##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2017  EDF SA                                          #
#                                                                            #
#  UncleBench is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by      #
#  the Free Software Foundation, either version 3 of the License, or         #
#  (at your option) any later version.                                       #
#                                                                            #
#  UncleBench is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#  GNU General Public License for more details.                              #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with UncleBench.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                            #
##############################################################################
''' Implements UncleBench Progress class'''
# pylint: disable=invalid-encoded-data, invalid-name, no-self-use, unused-variable, unused-argument

import os
import time
import sys
import subprocess

class Progress(object):
    ''' Progress bar

    Attributes:
        msg : message to be printed
        pause : update frequency
        main_char : all cases char
        ltr_char : left to right char
        rtl_char : right to left char

    Methods
        running_period
        flash_chars
        back_and_forward
    '''

    def __init__(self, msg=None, pause=0.03):
        self.msg = msg
        self.vbar = '|'
        self.pause = pause
        self.ltr = '▶'
        self.rtl = '◀'

   #                 ▁▁▁▁▁▁▁▁ ▁▁▁▁▁▁▁                 #
   #    ╲▚▚      ▞▞╱ Callable methods ╲▚▚      ▞▞╱    #
   #     ╲▚▚    ▞▞╱                    ╲▚▚    ▞▞╱     #
   #      ╲▚▚  ▞▞╱                      ╲▚▚  ▞▞╱      #
   #       ╲ ╲╱ ╱                        ╲ ╲╱ ╱       #
   #        ╲  ╱                          ╲  ╱        #


    def blink(self):
        ''' Prints blinking message '''
        self._set_fcolor(2)
        self._set_cursor_invisible()
        while True:
            self._print_message()
            time.sleep(2)
            self._clear_message()
            time.sleep(0.5)

    def running_period(self, size):
        ''' Prints running dots after message '''
        sys.stdout.write(self.msg)
        sys.stdout.flush()
        while True:
            self._point_sleep(size)
            self._move_backwards(size)
            self._erase_forward(size)
            self._move_backwards(size)

    def flash_chars(self):
        ''' Shows one char at a time '''
        while True:
            self._erase_forward(len(self.msg))
            self._move_backwards(len(self.msg))
            for i, c in enumerate(self.msg):
                txt = ' ' * i + c + ' ' * (len(self.msg) - i)
                sys.stdout.write(txt)
                sys.stdout.flush()
                time.sleep(0.5)
                self._move_backwards(len(self.msg)+1)

    def back_and_forward(self, bar_size, neon_size, full=True):
        ''' Simulate a progress bar '''
        _, cols = self._get_terminal_size()
        while True:
            progress_bar = self._left_to_right(bar_size, neon_size, cols)
            for instant in progress_bar:
                sys.stdout.write(instant)
                sys.stdout.flush()
                time.sleep(self.pause)
                self._move_backwards(cols)

            progress_bar = self._right_to_left(bar_size, neon_size, cols)
            for instant in progress_bar:
                sys.stdout.write(instant)
                sys.stdout.flush()
                time.sleep(self.pause)
                self._move_backwards(cols)

   #                 ▁▁▁▁▁▁▁▁ ▁▁▁▁▁▁▁                 #
   #    ╲▚▚      ▞▞╱ Internal methods ╲▚▚      ▞▞╱    #
   #     ╲▚▚    ▞▞╱                    ╲▚▚    ▞▞╱     #
   #      ╲▚▚  ▞▞╱                      ╲▚▚  ▞▞╱      #
   #       ╲ ╲╱ ╱                        ╲ ╲╱ ╱       #
   #        ╲  ╱                          ╲  ╱        #


    def _move_backwards(self, n):
        ''' Moves cursor n steps backwards '''
        sys.stdout.write((b'\x08' * n).decode())

    def _erase_forward(self, n):
        ''' Prints white space n times '''
        sys.stdout.write(' ' * n)
        sys.stdout.flush()

    def _print_message(self):
        ''' Prints message and brings back cursor to start of message '''
        self._erase_forward(len(self.msg))
        self._move_backwards(len(self.msg))
        sys.stdout.write(self.msg)
        sys.stdout.flush()
        self._move_backwards(len(self.msg))

    def _clear_message(self):
        ''' Moves cursor n steps backwards '''
        self._erase_forward(len(self.msg))
        self._move_backwards(len(self.msg))
        sys.stdout.flush()

    def _point_sleep(self, n):
        ''' Prints a period and sleeps
        for 1 second (repeat n times) '''
        for i in range(n):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(self.pause)

    def _left_to_right(self, bar_size, neon, term_size=0):
        time_length = range(bar_size - neon)
        for moment in time_length:
            progress_bar = '[' + ' ' * moment + self.ltr * neon + ' ' * \
                            (bar_size - neon - moment) + ']' + ' ' * (term_size - bar_size - 2)
            yield progress_bar

    def _right_to_left(self, bar_size, neon, term_size):
        time_length = range(bar_size - neon)
        for moment in time_length:
            progress_bar = '[' + ' ' * (bar_size - neon - moment) + self.rtl * \
                           neon + ' ' * moment + ']' + ' ' * (term_size - bar_size - 2)
            yield progress_bar

    def _get_terminal_size(self):
        ''' Return terminal size '''
        p = subprocess.Popen('stty size', stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        output, err = p.communicate()
        p_status = p.wait()
        return int(output.rstrip().split()[0]), int(output.rstrip().split()[1])

    def _set_fcolor(self, color):
        ''' Set terminal foreground color '''
        command = 'tput setaf' + ' ' + str(color)
        os.system(command)
        return 0

    def _set_cursor_invisible(self):
        ''' Set cursor invisible '''
        os.system('tput civis')
        return 0

if __name__ == '__main__':
    progress = Progress(" RUNNING")
    progress.back_and_forward(30, 7)
    progress.blink()
