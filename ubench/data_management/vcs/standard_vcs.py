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
''' Implements Version Control System API abstract class '''

# pylint: disable=superfluous-parens

import os
import abc
import ubench.utils as utils

class StandardVCS(object):
    '''  Abstract class defining the methods to be implemented in order to
         provide unclebench the funtionality it needs to clone repositories,
         add new files, update, commit changes and push back to public repo.
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, local_dir=None, repo_str=None):
        ''' Initializes variables '''
        self.local_dir = local_dir
        self.repo_str = repo_str

    def copy_remote_to_local(self):
        ''' Copies remote repository to local directory '''

        status, _, stderr = utils.run_cmd(self.clone_command(), self.local_dir)
        if status:
            print(stderr)
            msg = 'Error when executing command: {}'.format(self.clone_command())
            raise RuntimeError(msg)
        else:
            print('Cloning remote repository using Git')

    def update_remote(self):
        ''' Update remote repository with local copy '''

        status, _, stderr = utils.run_cmd(self.push_command(), self.local_dir)
        if status:
            print(stderr)
            msg = 'Error when executing command: {}'.format(self.push_command())
            raise RuntimeError(msg)
        else:
            print('Cloning remote repository using Git')

    def add_contents_to_local_repo(self, file_list, commit_msg=None):
        ''' Executes both add and commit operations '''

        status, _, stderr = utils.run_cmd(self.add_command(file_list), self.local_dir)
        if status:
            print(stderr)
            msg = 'Error when executing command: {}'.format(self.add_command(file_list))
            raise RuntimeError(msg)
        else:
            print('New contents added to repository using Git')

        status, _, stderr = utils.run_cmd(self.commit_command(commit_msg), self.local_dir)
        if status:
            print(stderr)
            msg = 'Error when executing command: {}'.format(self.commit_command(commit_msg))
            raise RuntimeError(msg)
        else:
            print('New contents commited to local repository using Git')

    def get_files_from_tag(self, tag):
        ''' Returns files related with tag '''
        _, files, _ = utils.run_cmd(self.show_command(tag), self.local_dir)
        return [os.path.join(self.local_dir, fl) for fl in files]

    @abc.abstractmethod
    def clone_command(self):
        ''' Abstract method for downloading repository '''
        raise NotImplementedError('Error: method not found')

    @abc.abstractmethod
    def add_command(self):
        ''' Abstract method for adding contents to the repository '''
        raise NotImplementedError('Error: method not found')

    @abc.abstractmethod
    def commit_command(self, file_list, commit_msg):
        ''' Abstract method for commiting changes to the repository '''
        raise NotImplementedError('Error: method not found')

    @abc.abstractmethod
    def push_command(self):
        ''' Abstract method for updating remote repository '''
        raise NotImplementedError('Error: method not found')

    @abc.abstractmethod
    def show_command(self, tag):
        ''' Abstract method for listing files related to tag '''
        raise NotImplementedError('Error: method not found')
