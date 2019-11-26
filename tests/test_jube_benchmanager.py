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

TEST_CONF = fake_data.UConf(resource_dir='/tmp/',
                            run_dir='/tmp/',
                            benchmark_dir='/tmp/')


def test_std_manager():
    std_bm = jbm.JubeBenchmarkManager('bench', 'platform', TEST_CONF)

def test_run_empty(mocker):
    std_bm = jbm.JubeBenchmarkManager('bench', 'platform', TEST_CONF)
    mock_jbm = mocker.patch(
        "ubench.benchmark_managers.standard_benchmark_manager.StandardBenchmarkManager.init_run_dir")

    std_bm.benchmarking_api = fake_data.FakeAPI()
    std_bm.run('platform', {'w':[], 'execute': False})


def test_w_option(mocker):
    mock_jbm = mocker.patch(
        "ubench.benchmark_managers.standard_benchmark_manager.StandardBenchmarkManager.init_run_dir")

    mock_set_w = mocker.patch(
        "fake_data.FakeAPI.set_custom_nodes")

    std_bm = jbm.JubeBenchmarkManager('bench', 'platform', TEST_CONF)
    std_bm.benchmarking_api = fake_data.FakeAPI()

    std_bm.run('platform', {'w':[(6, None), (1, 'cn184'), (4, 'cn[380,431-433]')], 'execute': False})
    mock_set_w.assert_called_with([6, 1, 4], [None, 'cn184', 'cn[380,431-433]'])
