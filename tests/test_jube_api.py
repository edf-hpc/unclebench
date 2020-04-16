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
import csv
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

MOCK_DATA = ["ubench",
             "data_management",
             "data_store_yaml"]

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
    """Mock XMLparser"""
    return fake_data.FakeXML()


def mockpopen(args, shell, cwd, env, stdout=None, stderr=None, universal_newlines=False):
    """Mock Popen"""
    if 'analyse' in args:
        return fake_data.MockPopen("jubeanalyse")

    return fake_data.MockPopen("juberun")


def mock_b_dir():
    return "benchmark_runs"


def test_run(mocker, mock_os_methods):
    """Test run method of JubeBenchmarkingAPI"""
    def mockanalyse(bench_id):
        rand = str(time.time())
        fake_id = int(rand[9])
        return fake_id, '000001'

    mocker.patch(".".join(MOCK_XML),
                 side_effect=mockxmlparser)

    mocker.patch(".".join(MOCK_UTILS+["Popen"]),
                          side_effect=mockpopen)

    mocker.patch(".".join(MOCK_JAPI+["JubeBenchmarkingAPI", "get_max_id"]),
                 side_effect=mockanalyse)

    jube_api = jba.JubeBenchmarkingAPI('test', 'platform')
    j_job, updated_params = jube_api.run({'w': "", 'execute': False, 'custom_params': {}})

    assert isinstance(j_job.jubeid, int)


def test_bench_datagen():
    fake_data.gen_jubeinfo_output()
    with open('data/mock_jube_info.cvs', 'rb') as csvfile:
        jubereader = csv.DictReader(csvfile, delimiter='~')
        num_col = len(jubereader.fieldnames)
        for row in jubereader:
            assert num_col == len(row)


@pytest.mark.xfail
def test_bench_datagenbad():
    with open('data/mock_jube_info-bad.csv', 'rb') as csvfile:
        jubereader = csv.DictReader(csvfile, delimiter='~')
        num_col = len(jubereader.fieldnames)
        for row in jubereader:
            assert num_col == len(row)


def test_result(mocker, mock_os_methods):
    """It test the generation of benchmark data.

    It mainly test the method _write_bench_data
    """
    # Unclebench mocks
    mocker.patch(".".join(MOCK_XML),
                 side_effect=mockxmlparser)
    mocker.patch(".".join(MOCK_JAPI+["JubeBenchmarkingAPI", "_analyse"]))
    mocker.patch(".".join(MOCK_JAPI+["JubeBenchmarkingAPI", "_extract_results"]))
    mock_data_write = mocker.patch(".".join(MOCK_DATA+["DataStoreYAML", "write"]))

    # STD lib mocks
    mocker.patch("tempfile.TemporaryFile", side_effect=fake_data.get_mock_jube_file)
    mocker.patch(".".join(MOCK_JAPI+["Popen"]))
    mocker.patch(".".join(MOCK_JAPI+["open"]),
                 side_effect=fake_data.get_results_file)

    jube_api = jba.JubeBenchmarkingAPI('test', 'platform')

    jube_api.result(0)
    metadata, context, r_file = mock_data_write.call_args.args

    assert '1' in context
    assert 'results_bench' in context['1']
    assert context['1']['results_bench'] == {'p_pat_min': '9', 'p_pat_max': '11', 'p_pat_avg': '10'}
    assert context['5']['results_bench'] == {'p_pat_min': '45', 'p_pat_max': '51', 'p_pat_avg': '50'}