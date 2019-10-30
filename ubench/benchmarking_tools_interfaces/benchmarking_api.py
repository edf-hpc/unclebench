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


    def analyse(self, benchmark_id):
        """ Analyze benchmark results

        Args:
            benchmark_id (int): id of the benchmark to be analyzed

        Returns:
            (str) result directory absolute path

        Raises:
            IOError
        """
        pass


    def analyse_last(self):
        """ Get last result from a jube benchmark.

        Returns:
            (str) result directory absolute path, None if analysis failed.
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


    def extract_result(self, benchmark_id):
        """ Get result from a jube benchmark with its id and build a python result array

        Args:
            benchmark_id (int): id of the benchmark

        Returns:
            (str) Array with the benchmark results
        """
        pass


    def extract_result_last(self):
        """ Get result from the last execution of a benchmark

        Returns:
            (str) Array with the benchmark results
        """
        pass


    def run(self, platform):
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


    def status(self, benchmark_id):
        """
            Args:
                benchmark_id (int):

            Returns:
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


    def set_parameter(self, doc_options):
        """ Set custom parameter from its name and a new value.

        Args:
            doc_options (dict): TODO

        Returns:
            List of tuples [(filename,param1,old_value,new_value),
                            (filename,param2,old_value,new_value),
                             ...]
        """
        pass
