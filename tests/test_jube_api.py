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
# pylint: disable=line-too-long,missing-docstring,unused-variable,unused-import,unused-argument

import time
import re
import pytest
import pytest_mock
import mock
import ubench.benchmarking_tools_interfaces.jube_benchmarking_api as jba
import fake_data

#jubebenchmarkingAPI uses the values set in test_bench_api
MOCK_XML = ["ubench",
            "benchmarking_tools_interfaces",
            "jube_xml_parser",
            "JubeXMLParser"]

MOCK_JAPI = ["ubench",
             "benchmarking_tools_interfaces",
             "jube_benchmarking_api"]

def test_analyse(mocker):
    mock_listdir = mocker.patch("os.listdir")
    mock_isdir = mocker.patch("os.path.isdir")
    mock_chdir = mocker.patch("os.chdir")
    jube_api = jba.JubeBenchmarkingAPI('simple', 'platform')
    def mocksubpopen(args, shell, cwd, stdout=None, universal_newlines=False):
        """ docstring """
        return fake_data.MockPopen("jubeanalyse")

    def mock_g_dir():
        return "benchmark_runs"

    mock_xml = mocker.patch(".".join(MOCK_XML+["get_bench_outputdir"]),
                            side_effect=mock_g_dir)

    mock_popen = mocker.patch(".".join(MOCK_JAPI+["Popen"]),
                              side_effect=mocksubpopen)

    assert jube_api.analyse(0) == "/tmp/ubench_pytest//run/platform/simple/benchmark_runs/000001"




def test_run(mocker):

    mock_listdir = mocker.patch("os.listdir")
    mock_isdir = mocker.patch("os.path.isdir")
    mock_chdir = mocker.patch("os.chdir")
    mock_rmdir = mocker.patch("shutil.rmtree")
    jube_api = jba.JubeBenchmarkingAPI('test', 'platform')


    def mocksubpopen(args, cwd, shell, env, stdout, universal_newlines):# pylint: disable=too-many-arguments
        """ docstring """

        return fake_data.MockPopen("juberun")

    def mockanalyse(bench_id):
        rand = str(time.time())
        fake_id = rand[9]
        return "/tmp/run/platform/simple/benchmark_runs/00000{}".format(fake_id)

    mock_popen = mocker.patch(".".join(MOCK_JAPI+["Popen"]),
                              side_effect=mocksubpopen)
    mock_analyse = mocker.patch(".".join(MOCK_JAPI+["JubeBenchmarkingAPI", "analyse"]),
                                side_effect=mockanalyse)

    dir_result, id_b = jube_api.run(0)
    id_regx = re.compile(r'00000\d')

    assert id_regx.match(id_b)
