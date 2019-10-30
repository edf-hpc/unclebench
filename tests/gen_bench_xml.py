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
""" Unclebench unit testing """


import os
import tempbench
import ubench.benchmarking_tools_interfaces.jube_benchmarking_api as jba


test_env = None  # pylint: disable=invalid-name

# You have to export UBENCH_BENCHMARK_DIR=
# path of bench you want to test"


def init_env():
    """ Initializes environment variables """

    config = {}
    config['main_path'] = '/tmp/ubench_multisource_test/'

    global test_env  # pylint: disable=invalid-name, global-statement
    test_env = tempbench.Tempbench(config)  # pylint: disable=no-value-for-parameter
    test_env.copy_files()

    os.environ['UBENCH_RUN_DIR_BENCH'] = test_env.config['run_path']
    os.environ['UBENCH_RESOURCE_DIR'] = test_env.config['resources_path']


def get_bench_multisource_git(bench):
    """ dosctring """

    benchmarking_api = jba.JubeBenchmarkingAPI(bench, '')
    path = os.path.join(test_env.config['run_path'], bench)
    if not os.path.exists(path):
        os.makedirs(path)
    benchmarking_api.jube_xml_files.add_bench_input()
    benchmarking_api.jube_xml_files.write_bench_xml()


init_env()
get_bench_multisource_git('aster')
print('Files were generated in {0}'
      .format(test_env.config['run_path']))  # pylint: disable=superfluous-parens
