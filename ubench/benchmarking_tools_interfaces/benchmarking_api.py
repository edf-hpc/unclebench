# -*- coding: utf-8 -*-
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
""" BenchmarkingAPI class """


class BenchmarkingAPI(object):
    """ Interface class for benchmarking environnement tools """


    def __init__(self, benchmark_name, platform_name):
        """ Class constructor

        Args:
            benchmark_name (str): name of the benchmark
             platform_name (str): name of the platform
        """
        pass


    def result(self, idb):
        """ Generate and print results
        Args:
             (int) idb: id of the benchmark

        Returns:
            (list) numeric results
        """
        pass

    def get_results_root_directory(self):
        """ Returns benchmark results root directory

        Returns:
            (str) Absolut path of result directory
        """
        pass


    def get_log(self, idb=-1):
        """ Get a log from a benchmark run

        Args:
             (int) idb: id of the benchmark

        Returns
            (str) benchmark run log
        """
        pass


    def run(self, opts):
        """ Runs benchmark.

        Run benchmark on a given platform and return the benchmark run directory path
        and a benchmark ID.

        Args:
            platform (str): name of the platform used to configure the benchmark options relative
                            to the platform architecture and software.

        Return:
            (str) Absolute path of the benchmark result directory
        """
        pass


    def set_custom_nodes(self, nnodes_list, nodes_id_list):
        """ Modify benchmark xml file to set custom nodes configurations.

        Args:
            nnodes_list (list): list of number of nodes ex: [1,6]
            nodes_id_list (list): list of corresonding nodes ids  ex: ['cn050','cn[103-107,145]']
        """
        pass


    def list_parameters(self, default_values):
        """ List benchmark customisable parameters

        Args:
            default_values:

        Returns:
            List of tuples [(param1, value), (param2, value), ...]
        """
        pass
