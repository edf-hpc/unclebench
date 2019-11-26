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
# pylint: disable=no-self-use,unused-argument,no-init,old-style-class,missing-docstring
""" Provides fake data and clases for test purposes """

import collections

UConf = collections.namedtuple('Uconf', 'resource_dir run_dir benchmark_dir')


class MockPopen(object):
    """Fakes slurm commands """

    def __init__(self, cmd):
        self.cmd = cmd

    # pylint: disable=R0201
    def wait(self):
        """ docstring """
        return 0

    @property
    def stdout(self):
        """ docstring """
        if self.cmd == "sinfo":
            return ["node\tup\tinfinite\t16\tidle node[0006-0008,0020-0031]"]
        elif self.cmd == "squeue":
            return ["   175757  RUNNING"]
        elif self.cmd == "sacct":
            return [" 26938.0     COMPLETED", " 26382.0     COMPLETED"]

        return [""]



class FakeAPI:
    """Fakes benchmark API"""

    def run(self, platform):
        return '/tmp/', 0

    def set_custom_nodes(self, nnodes, nodes):
        return True
