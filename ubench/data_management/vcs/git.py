# -*- coding: utf-8 -*-
##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2020 EDF SA                                           #
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
""" Implements Version Control System API abstract class """

from ubench.data_management.vcs.standard_vcs import StandardVCS

class Git(StandardVCS):
    ''' Implements interface with Git VCS '''

    def push_command(self):
        ''' Return Git push command '''
        cmd = 'git push'
        return cmd

    def clone_command(self):
        ''' Return Git clone command '''
        cmd = 'git clone' + ' ' + self.repo_str
        return cmd

    def add_command(self, files):
        ''' Return Git add command '''
        cmd = 'git add' + ' ' + ' '.join(files)
        return cmd

    def commit_command(self, commit_msg):
        ''' Return Git commit command '''
        cmd = 'git commit -m \'{}\''.format(commit_msg)
        return cmd

    def show_command(self, tag):
        ''' Return Git show command '''
        cmd = 'git show {} --pretty=\'\' --name-only'.format(tag)
        return cmd
