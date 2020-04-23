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
from ubench.core.ubench_commands import UbenchCmd
import fake_data

BMS_MOCK = ["ubench",
            "benchmark_managers",
            "benchmark_manager_set",
            "BenchmarkManagerSet"]

SBM_MOCK = ["ubench",
            "benchmark_managers",
            "standard_benchmark_manager",
            "StandardBenchmarkManager"]

JBA_MOCK = ["ubench",
            "benchmarking_tools_interfaces",
            "jube_benchmarking_api",
            "JubeBenchmarkingAPI"]

UCONF_MOCK = ["ubench",
              "core",
              "ubench_config",
              "UbenchConfig"]

XML_MOCK = ["ubench",
            "benchmarking_tools_interfaces",
            "jube_xml_parser",
            "JubeXMLParser"]

# pylint: disable=unused-argument
def mockxmlparser(*args):
    """Mock xmlparser"""
    return fake_data.FakeXML()


def test_run_noresourcedir(mocker):
    """ Test with results result dir failing """

    mocker.patch(".".join(BMS_MOCK+["run"]))

    cmd = UbenchCmd("platform", [])

    assert cmd.run({'w': []}) is False


def test_run_withresourcedir(mocker):
    """Test with results method with result dir success"""
    mocker.patch("os.path.isdir")
    mock_bms = mocker.patch(".".join(BMS_MOCK+["run"]))

    cmd = UbenchCmd("platform", [])

    assert cmd.run({'w': [], 'file_params': [], 'custom_params': []}) is True
    mock_bms.assert_called_with({'w': [],
                                 'file_params': [],
                                 'custom_params': {}})

    cmd.run({'w': ['6', 'cn184', 'cn[380,431-433]'], 'file_params': [], 'custom_params': []})
    mock_bms.assert_called_with({'w':[(6, None), (1, 'cn184'), (4, 'cn[380,431-433]')],
                                 'file_params': [],
                                 'custom_params': {}})


def test_run_wlist_parameter(mocker):
    """ Test parameter wlist"""
    def mock_benchmark_list():
        return ["simple"]

    def mock_listdir(path):
        return []

    mocker.patch(".".join(UCONF_MOCK+["get_benchmark_list"]),
                              side_effect=mock_benchmark_list)
    mocker.patch(".".join(XML_MOCK), side_effect=mockxmlparser)
    mocker.patch(".".join(SBM_MOCK+["_init_run_dir"]))
    mocker.patch("os.path.isdir")
    mocker.patch("os.listdir", side_effect=mock_listdir)
    mock_jba = mocker.patch(".".join(JBA_MOCK + ["_set_custom_nodes"]))

    cmd = UbenchCmd("platform", ["simple"])
    cmd.run({'w': ['160', 'cn184', 'cn[380,431-433]'],
             'file_params':[], 'custom_params' : [],
             'foreground': False, 'execute' : False})

    mock_jba.assert_called_with([(160, None), (1, 'cn184'), (4, 'cn[380,431-433]')])


def test_log(mocker):
    """ Test log command"""
    mock_bms = mocker.patch(".".join(BMS_MOCK+["print_log"]))

    cmd = UbenchCmd("platform", [])
    cmd.log(None)
    mock_bms.assert_called_with(-1)
    cmd.log([2])
    mock_bms.assert_called_with(2)
    cmd.log([2, 3])
    mock_bms.assert_called_with(3)
