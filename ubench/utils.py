# -*- coding: utf-8 -*-
##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2019 EDF SA                                           #
#                                                                            #
#  UncleBench is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by      #
#  the Free Software Foundation, either version 3 of the License, or         #
#  (at your option) any later version.                                       #
#                                                                            #
#  UncleBench is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU General Public License for more details.                              #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with UncleBench. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                            #
##############################################################################
''' Provides useful methods '''

from subprocess import Popen, PIPE

def run_cmd(cmd_string, cwd, env=None):
    ''' Wrapper for Popen with communicate method '''
    cmd = Popen(cmd_string,
                cwd=cwd,
                shell=True,
                env=env,
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True)

    stdout, stderr = cmd.communicate()
    ret_code = cmd.returncode
    # we remove empty lines
    stdout_stream = [line for line in stdout.split('\n') if line]
    stderr_stream = [line for line in stderr.split('\n') if line]

    return ret_code, stdout_stream, stderr_stream

def run_cmd_bg(cmd_string, cwd, env=None):
    ''' Wrapper for Popen no blocking '''
    cmd = Popen(cmd_string,
                cwd=cwd,
                shell=True,
                env=env,
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True)

    return cmd
