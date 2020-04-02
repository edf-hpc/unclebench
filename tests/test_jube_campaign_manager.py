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
import pytest_mock
import mock
import fake_data
from ubench.benchmark_managers.campaign_benchmark_manager import CampaignManager
from ubench.benchmarking_tools_interfaces.jube_benchmarking_api import JubeBenchmarkingAPI


MOCK_XML = ["ubench",
            "benchmarking_tools_interfaces",
            "jube_xml_parser",
            "JubeXMLParser"]

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

def mockxmlparser(*args):
    """Mock xmlparser"""
    return fake_data.FakeXML()


# def test_init():

#     campaign = CampaignManager("tests/campaign_metadata.yaml")
#     assert campaign.campaign['name'] in campaign.campaign_dir

# def test_campaign_file():
#     campaign = CampaignManager("tests/campaign_metadata.yaml")
#     assert 'name' in campaign.campaign
#     assert 'benchmarks' in campaign.campaign

#     benchmarks = campaign.campaign['benchmarks']
#     assert type(benchmarks)==dict
#     assert len(benchmarks)==4

# def test_campaign_init():
#     campaign = CampaignManager("tests/campaign_metadata.yaml")
#     benchmarks = campaign.campaign['benchmarks']
#     campaign.init_campaign()
#     benchmark_object = campaign.benchmarks['bench_1']
#     assert type(benchmark_object)==JubeBenchmarkingAPI

def test_campaign_run(mocker):

    def mock_bench_list():
        return ["bench_4", "bench_3", "bench_2", "bench_1"]

    mock_api = mocker.patch("fake_data.FakeAPI2.result")

    mocker.patch(".".join(MOCK_CM+["SlurmInterface"]),
                 side_effect=fake_data.FakeSlurm)

    mocker.patch(".".join(MOCK_JUBE_BENCH_API),
                 side_effect=fake_data.FakeAPI2)

    mocker.patch("ubench.core.ubench_config.UbenchConfig.get_benchmark_list",
                 side_effect=mock_bench_list)

    campaign = CampaignManager("tests/campaign_metadata.yaml")
    campaign.init_campaign()
    campaign.run()
    mock_api.assert_called()
