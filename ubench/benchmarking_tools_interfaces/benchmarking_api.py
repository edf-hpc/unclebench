#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright (C) 2015 EDF SA                                                 #
#                                                                            #
#  This file is part of UncleBench                                           #
#                                                                            #
#  This software is governed by the CeCILL license under French law and      #
#  abiding by the rules of distribution of free software. You can use,       #
#  modify and/ or redistribute the software under the terms of the CeCILL    #
#  license as circulated by CEA, CNRS and INRIA at the following URL         #
#  "http://www.cecill.info".                                                 #
#                                                                            #
#  As a counterpart to the access to the source code and rights to copy,     #
#  modify and redistribute granted by the license, users are provided only   #
#  with a limited warranty and the software's author, the holder of the      #
#  economic rights, and the successive licensors have only limited           #
#  liability.                                                                #
#                                                                            #
#  In this respect, the user's attention is drawn to the risks associated    #
#  with loading, using, modifying and/or developing or reproducing the       #
#  software by the user in light of its specific status of free software,    #
#  that may mean that it is complicated to manipulate, and that also         #
#  therefore means that it is reserved for developers and experienced        #
#  professionals having in-depth computer knowledge. Users are therefore     #
#  encouraged to load and test the software's suitability as regards their   #
#  requirements in conditions enabling the security of their systems and/or  #
#  data to be ensured and, more generally, to use and operate it in the      #
#  same conditions as regards security.                                      #
#                                                                            #
#  The fact that you are presently reading this means that you have had      #
#  knowledge of the CeCILL license and that you accept its terms.            #
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
