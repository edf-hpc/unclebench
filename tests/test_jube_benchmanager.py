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
# pylint: disable=line-too-long,missing-docstring,unused-variable,unused-import

import pytest
import pytest_mock
import mock
import ubench.benchmark_managers.jube_benchmark_manager as jbm
import ubench.benchmark_managers.standard_benchmark_manager as stdbm
import ubench.benchmarking_tools_interfaces.jube_benchmarking_api as jba
import fake_data


MOCK_XML = ["ubench",
            "benchmarking_tools_interfaces",
            "jube_xml_parser",
            "JubeXMLParser"]

MOCK_MANAGER = ["ubench",
                "benchmark_managers",
                "standard_benchmark_manager",
                "StandardBenchmarkManager"]

def mockxmlparser(*args):
    """Mock xmlparser"""
    return fake_data.FakeXML()

@pytest.fixture
def mocks_custom(mocker):
    mock_listdir = mocker.patch("os.listdir")
    mock_xml = mocker.patch(".".join(MOCK_XML),
                            side_effect=mockxmlparser)
    mock_jbm = mocker.patch(".".join(MOCK_MANAGER + ["_init_run_dir"]))

def test_std_manager(mocker, mocks_custom):
    std_bm = jbm.JubeBenchmarkManager('bench', 'platform')

def test_run_empty(mocker, mocks_custom):
    std_bm = jbm.JubeBenchmarkManager('bench', 'platform')

    std_bm.benchmarking_api = fake_data.FakeAPI()
    std_bm.run({'w': [], 'execute': False, 'foreground': False})
