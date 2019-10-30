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
""" Provides Tempbench class"""


import os
import shutil


class Tempbench(object):
    """ This class creates a test env for unclebench """

    def __init__(self, config, repository_root):
        """ Class constructor """

        self.config = config
        self.config['bench_path'] = config['main_path'] + '/benchmarks'
        self.config['plugin_path'] = config['main_path'] + '/plugin'
        self.config['run_path'] = config['main_path'] + '/run'
        self.config['resources_path'] = config['main_path'] + '/resources'
        self.config['bench_input'] = os.path.join(repository_root, 'benchmarks/simple')

        self.create_dir_structure()


    def create_dir_structure(self):
        """ Creates directory structure """

        for name, path in self.config.items():  # pylint: disable=unused-variable
            if not os.path.exists(path):
                os.makedirs(path)


    def copy_files(self):
        """ docstring """

        bench_input = self.config['bench_input']
        bench_path = os.path.join(self.config['bench_path'], 'simple.')
        shutil.copytree(bench_input, bench_path)


    def create_empty_bench(self):
        """ docstring """

        bench_path = os.path.join(self.config['bench_path'], 'test_bench')
        os.makedirs(bench_path)
        open(os.path.join(bench_path, 'test_bench.xml'), 'a').close()


    def create_run_dir(self, bench):
        """ docstring """

        path_bench = os.path.join(self.config['run_path'], bench)
        os.makedirs(path_bench)


    def destroy_dir_structure(self):
        """ docstring """

        self.config.pop('bench_input', None)
        for name, path in self.config.items():  # pylint: disable=unused-variable
            if os.path.exists(path):
                shutil.rmtree(path)
