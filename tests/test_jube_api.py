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
# pylint: disable=line-too-long,missing-docstring,unused-variable,unused-import,unused-argument,redefined-outer-name,too-many-arguments

import time
import re
import pytest
import pytest_mock
import mock
import ubench.benchmarking_tools_interfaces.jube_benchmarking_api as jba
import ubench.core.ubench_config as uconfig
import fake_data

#jubebenchmarkingAPI uses the values set in test_bench_api
MOCK_XML = ["ubench",
            "benchmarking_tools_interfaces",
            "jube_xml_parser",
            "JubeXMLParser"]

MOCK_JAPI = ["ubench",
             "benchmarking_tools_interfaces",
             "jube_benchmarking_api"]

MOCK_UTILS = ["ubench", "utils"]

@pytest.fixture
def mock_os_methods(mocker):
    mock_listdir = mocker.patch("os.listdir")
    mock_isdir = mocker.patch("os.path.isdir")
    mock_chdir = mocker.patch("os.chdir")
    mock_rmdir = mocker.patch("shutil.rmtree")


def mockxmlparser(*args):
    """Mock xmlparser"""
    return fake_data.FakeXML()

def mockpopen(args, shell, cwd, env, stdout=None, stderr=None, universal_newlines=False):
    """Mock Popen"""
    if 'analyse' in args:
        return fake_data.MockPopen("jubeanalyse")

    return fake_data.MockPopen("juberun")

def mock_b_dir():
    return "benchmark_runs"

def test_analyse(mocker, mock_os_methods):

    mock_xml = mocker.patch("ubench.benchmarking_tools_interfaces.jube_xml_parser.JubeXMLParser",
                            side_effect=mockxmlparser)

    uconf = uconfig.UbenchConfig()
    jube_api = jba.JubeBenchmarkingAPI('simple', 'platform', uconf)

    mock_popen = mocker.patch(".".join(MOCK_UTILS+["Popen"]),
                              side_effect=mockpopen)

    assert jube_api.analyse(0) == "/tmp/ubench_pytest//run/platform/simple/benchmark_runs/000001"

def test_run(mocker, mock_os_methods):

    mock_xml = mocker.patch("ubench.benchmarking_tools_interfaces.jube_xml_parser.JubeXMLParser",
                            side_effect=mockxmlparser)

    uconf = uconfig.UbenchConfig()
    jube_api = jba.JubeBenchmarkingAPI('test', 'platform', uconf)

    def mockanalyse(bench_id):
        rand = str(time.time())
        fake_id = int(rand[9])
        return fake_id, '000001'


    mock_popen = mocker.patch(".".join(MOCK_UTILS+["Popen"]),
                              side_effect=mockpopen)

    mock_analyse = mocker.patch(".".join(MOCK_JAPI+["JubeBenchmarkingAPI", "_get_max_id"]),
                                side_effect=mockanalyse)

    dir_result, id_b = jube_api.run()

    assert isinstance(id_b, int)
