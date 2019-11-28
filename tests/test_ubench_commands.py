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

# pylint: disable=unused-import,unused-variable,line-too-long
import pytest
import mock
import pytest_mock
import ubench.core.ubench_commands as ubench_commands

BMS_MOCK = ["ubench",
            "benchmark_managers",
            "benchmark_manager_set",
            "BenchmarkManagerSet"]

def test_wlist():
    """Test translation of list of nodes"""

    cmd = ubench_commands.UbenchCmd("platform", [])
    assert cmd.translate_wlist_to_scheduler_wlist(['1', '2', '3']) == [(1, None), (2, None), (3, None)]
    assert cmd.translate_wlist_to_scheduler_wlist(['6', 'cn184', 'cn[380,431-433]']) == [(6, None), (1, 'cn184'), (4, 'cn[380,431-433]')]
    assert cmd.translate_wlist_to_scheduler_wlist(['6', 'cn184', 'host1']) == [(6, None), (1, 'cn184'), (1, 'host1')]

def test_run_noresourcedir(mocker):
    """ Test with results result dir failing """

    mock_bms = mocker.patch(".".join(BMS_MOCK+["run"]))

    cmd = ubench_commands.UbenchCmd("platform", [])

    assert cmd.run({'w':[]}) is False

def test_run_withresourcedir(mocker):
    """Test with results method with result dir success"""

    mock_bms = mocker.patch(".".join(BMS_MOCK+["run"]))
    mock_isdir = mocker.patch("os.path.isdir")
    cmd = ubench_commands.UbenchCmd("platform", [])

    assert cmd.run({'w':[], 'file_params' :[], 'custom_params' : []}) is True
    mock_bms.assert_called_with("platform", {'w':[],
                                             'file_params' :[],
                                             'custom_params' : []})

    cmd.run({'w':['6', 'cn184', 'cn[380,431-433]'], 'file_params' :[], 'custom_params' : []})
    mock_bms.assert_called_with("platform", {'w':[(6, None), (1, 'cn184'), (4, 'cn[380,431-433]')],
                                             'file_params' :[],
                                             'custom_params' : []})


def test_log(mocker):
    """ Test log command"""
    cmd = ubench_commands.UbenchCmd("platform", [])
    mock_bms = mocker.patch(".".join(BMS_MOCK+["print_log"]))
    cmd.log()
    mock_bms.assert_called_with(-1)
    cmd.log([2])
    mock_bms.assert_called_with(2)
    cmd.log([2, 3])
    mock_bms.assert_called_with(3)

def test_result(mocker):
    """ Test log command"""
    cmd = ubench_commands.UbenchCmd("platform", [])
    mock_bms = mocker.patch(".".join(BMS_MOCK+["analyse"]))
    cmd.result(['last'])
    mock_bms.assert_called_with('last')
    cmd.result([2], None)
    mock_bms.assert_called_with(2)
    cmd.result([2, 3], None)
    mock_bms.assert_called_with(3)

def test_result_none(mocker):
    """Test result with None value """
    cmd = ubench_commands.UbenchCmd("platform", [])
    mock_bms = mocker.patch(".".join(BMS_MOCK+["analyse"]))
    cmd.result(None, None)
