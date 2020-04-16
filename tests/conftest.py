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
import os
import pytest
import tempbench
import collections

@pytest.fixture(scope="module")
def init_env(pytestconfig):
    """ It creates a temporary directory structure to
    test JubeBenchmarkingAPI objects"""

    config = {}
    config['main_path'] = "/tmp/ubench_pytest/"
    repository_root = os.path.join(pytestconfig.rootdir.dirname,
                                   pytestconfig.rootdir.basename)

    os.environ["UBENCH_BENCHMARK_DIR"] = os.path.join(config['main_path'],
                                                      'benchmarks')
    os.environ["UBENCH_PLATFORM_DIR"] = os.path.join(repository_root,
                                                     'platform')

    test_env = tempbench.Tempbench(config, repository_root)
    test_env.copy_files()
    os.environ["UBENCH_RUN_DIR_BENCH"] = test_env.config['run_path']
    os.environ["UBENCH_RESOURCE_DIR"] = test_env.config['resources_path']
    yield test_env
    test_env.destroy_dir_structure()

@pytest.fixture(scope="session")
def data_dir(pytestconfig):
    """This fixture helps to access files from data directory"""
    TestFiles = collections.namedtuple('TestFiles', 'root campaign jubeinfo_bad bench_results')
    root_data = os.path.join(pytestconfig.rootdir.dirname,
                             pytestconfig.rootdir.basename,
                             'tests/data')

    return TestFiles(root_data,
                     os.path.join(root_data, 'campaign_metadata.yaml'),
                     os.path.join(root_data, 'mock_jube_info-bad.csv'),
                     os.path.join(root_data, 'bench_results.yaml'))