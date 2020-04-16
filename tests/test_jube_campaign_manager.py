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

import os
import pytest
import fake_data
from ubench.benchmark_managers.campaign_benchmark_manager import CampaignManager
from ubench.benchmarking_tools_interfaces.jube_benchmarking_api import JubeBenchmarkingAPI

MOCK_JUBE_BENCH_API = ["ubench",
                       "benchmarking_tools_interfaces",
                       "jube_benchmarking_api",
                       "JubeBenchmarkingAPI"]

MOCK_SLURM = ["ubench",
              "scheduler_interfaces",
              "slurm_interface"]


MOCK_CM = ["ubench",
           "benchmark_managers",
           "campaign_benchmark_manager"]


@pytest.fixture
def mock_benchs(mocker):
    """it mocks the method get_benchmark_list to add fake benchmarks
    and not generate a Runtime error"""

    def mock_bench_list():
        return ["bench_4", "bench_3", "bench_2", "bench_1"]

    mocker.patch("ubench.core.ubench_config.UbenchConfig.get_benchmark_list",
                 side_effect=mock_bench_list)


@pytest.fixture
def run_dir(tmpdir_factory):
    """it creates a different run directory for each campaign"""

    fn = tmpdir_factory.mktemp("rundir")
    os.environ["UBENCH_RUN_DIR_BENCH"] = str(fn)


def test_init(init_env, mock_benchs, run_dir, data_dir):
    """it test object initialisation"""
    campaign = CampaignManager(data_dir.campaign)
    assert campaign.campaign['name'] in campaign.campaign_dir


def test_campaign_file(init_env, mock_benchs, run_dir, data_dir):
    """it test parsing of campaign file"""

    campaign = CampaignManager(data_dir.campaign)
    assert 'name' in campaign.campaign
    assert 'benchmarks' in campaign.campaign

    benchmarks = campaign.campaign['benchmarks']
    assert type(benchmarks)==dict
    assert len(benchmarks)==4


def test_campaign_init(init_env, mock_benchs, run_dir, data_dir):
    """it test successful load of benchmark class"""

    campaign = CampaignManager(data_dir.campaign)
    benchmarks = campaign.campaign['benchmarks']
    campaign.init_campaign()
    benchmark_object = campaign.benchmarks['bench_1']
    assert type(benchmark_object) == JubeBenchmarkingAPI


def test_campaign_run(mocker, init_env, mock_benchs, run_dir, data_dir):

    """it executes a fake campaign using fake classes that generate
    random job states"""

    mock_api = mocker.patch("fake_data.FakeAPI2.result")
    mocker.patch(".".join(MOCK_CM+["SlurmInterface"]),
                 side_effect=fake_data.FakeSlurm)
    mocker.patch(".".join(MOCK_JUBE_BENCH_API),
                 side_effect=fake_data.FakeAPI2)

    campaign = CampaignManager(data_dir.campaign)
    campaign.init_campaign()
    campaign.run()
    mock_api.assert_called()


def test_campaign_print(mocker, init_env, mock_benchs, run_dir, data_dir):
    """it test the output of campaign execution results"""

    mocker.patch(".".join(MOCK_JUBE_BENCH_API),
                 side_effect=fake_data.FakeAPI2)

    campaign = CampaignManager(data_dir.campaign)
    fake_res = {'HPL[Gflop/s]': 0.23515579071134626}

    formatted_s = campaign.print_results(fake_res)
    assert formatted_s == {'HPL[Gflop/s]': '0.235'}
    formatted_s = campaign.print_results(fake_res, "diff")
    assert formatted_s == {'HPL[Gflop/s]': '0.235%'}

    fake_res = {'HPL[Gflop/s]': ''}
    formatted_s = campaign.print_results(fake_res)
    assert formatted_s == {'HPL[Gflop/s]':'0.000'}
