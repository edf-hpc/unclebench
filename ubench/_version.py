#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import subprocess
import os


VERSION= "0.2.3"


def get_git_revision_short_hash():
    #check if we are in a git repository
    return None
    # current_path = os.path.dirname(os.path.abspath(__file__))
    # os.chdir(current_path)
    # if subprocess.call(["git", "branch"], stderr=open(os.devnull, 'w'), stdout=open(os.devnull, 'w')) != 0:
    #   return None
    # else:
    #   return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])


def get_version():

  version = VERSION
  git_revision = get_git_revision_short_hash()

  if git_revision:
    version+= "-{}".format(git_revision.rstrip())

  return version
