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
""" Provides test API """

# pylint: disable=unused-import,unused-variable,line-too-long,unused-argument
from subprocess import Popen
import pytest
import mock
import pytest_mock
import ubench.scheduler_interfaces.slurm_interface as slurm_i


class MockPopen(object):
    """ docstring """

    # pylint: disable=R0201
    def wait(self):
        """ docstring """
        return 0

    @property
    def stdout(self):
        """ docstring """
        return ["node\tup\tinfinite\t16\tidle node[0006-0008,0020-0031]"]

def test_emptylist():
    """ docstring """
    interface = slurm_i.SlurmInterface()
    assert not interface.get_available_nodes()


def test_available_nodes(mocker):
    """ docstring """
    def mocksubpopen(args, shell, cwd, stdout=None, universal_newlines=False):
        """ docstring """

        return MockPopen()

    mock_popen = mocker.patch("ubench.scheduler_interfaces.slurm_interface.Popen",
                              side_effect=mocksubpopen)

    interface = slurm_i.SlurmInterface()
    node_list = interface.get_available_nodes(5)
    assert interface.get_available_nodes()
    assert len(node_list) == 3
    assert node_list[0] == "node[0006-0008,0020-0021]"
