#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2017  EDF SA                                          #
#                                                                            #
#  UncleBench is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by      #
#  the Free Software Foundation, either version 3 of the License, or         #
#  (at your option) any later version.                                       #
#                                                                            #
#  UncleBench is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#  GNU General Public License for more details.                              #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with UncleBench.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                            #
##############################################################################

class BenchmarkingAPI:
    """ Interface class for benchmarking environnement tools """

    def __init__(self,benchmark_name,platform):
        """ Constructor
        :param benchmark_name: name of the benchmark
        :type benchmark_name: str
        :param benchmark_path: absolute path of the benchmark root directory.
        :type benchmark_path: str
        """
        self.platform=platform
        self.benchmark_name=benchmark_name

    def analyse_benchmark(self,benchmark_id):
        """ Analyze benchmark results
        :param benchmark_id: id of the benchmark to be analyzed
        :type benchmark_id: int
        :returns: result directory absolute path
        :rtype: str
        :raises: IOError
        """
        pass

    def analyse_last_benchmark(self):
        """ Get last result from a jube benchmark.
        :returns: result directory absolute path, None if analysis failed.
        :rtype: str
        """
        pass

    def get_results_root_directory(self):
        """ Returns benchmark results root directory
        :returns: result directory asbolut path
        :rtype: str
        """
        pass

    def get_log(self,idb=-1):
        """ Get a log from a benchmark run
        :param idb: id of the benchmark
        :type idb:int
        :returns: log
        :rtype:str
        """
        pass


    def extract_result_from_benchmark(self,benchmark_id):
        """ Get result from a jube benchmark with its id and build a python result array
        :param benchmark_id: id of the benchmark
        :type benchmark_id:int
        :returns: result array
        :rtype:str
        """
        pass

    def extract_result_from_last_benchmark(self):
        """ Get result from the last execution of a benchmark
        :param benchmark_id: id of the benchmark
        :type benchmark_id:int
        :returns: result array
        :rtype:str
        """
        pass

    def run_benchmark(self,platform):
        """ Run benchmark on a given platform and return the benchmark run directory path
        and a benchmark ID.
        :param platform: name of the platform used to configure the benchmark options relative
        to the platform architecture and software.
        :type platform: str
        :returns: return absolute path of the benchmark result directory
        :rtype: str
        """
        pass

    def set_custom_nodes(self,nnodes_list,nodes_id_list):
        """
        Modify benchmark xml file to set custom nodes configurations.
        :param nnodes_list: list of number of nodes ex: [1,6]
        :type nnodes_list: list of int
        :param nodes_id_list: list of corresonding nodes ids  ex: ['cn050','cn[103-107,145]']
        :type nodes_id_list:  list of strings
        """
        pass

    def status(self,benchmark_id):

        pass

    def list_parameters(self,config_dir_path=None):
        """
        List benchmark customisable parameters
        :param config_dir_path: Optional parameter reprenting the path of the config files (usefull when a benchmark has never been run).
        :type config_dir_path: str
        :returns: Return a list of tuples [(param1,value),(param2,value),....]
        :rtype: list of tuples
        """
        pass

    def set_parameter(self,parameter_name,value):
        """
        Set custom parameter from its name and a new value.
        :param parameter_name: name of the parameter to customize
        :type parameter_name:
        :param value: value to substitute to old value
        :type value: str
        :returns: Return a list of tuples [(filename,param1,old_value,new_value),(filename,param2,old_value,new_value),....]
        :rtype: List of 3-tuples ex:[(parameter_name,old_value,value),....]
        """
        pass
