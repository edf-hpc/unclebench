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
# pylint: disable=superfluous-parens
""" Define BenchmarkManagerSet class. """


import ubench.benchmark_managers.benchmark_manager as benm
import ubench.benchmark_managers.jube_benchmark_manager as jbm


class BenchmarkManagerSet(benm.BenchmarkManager):
    """ Composite class that manages multiple BenchmarkManager.

    Attributes:
        run
        list_parameters
        set_parameter
        print_log
        list_runs
        analise
        analise_last
        extract_results
        extract_results_lst
        print_result_array
        print_transposed_result_array
    """


    def __init__(self, benchmark_names, platform_name, uconf):
        """ Class constructor

        Arg:
            benchmark_names (list): with benchmark names
            platform_name (str): name of the platform
            uconf (UbenchConfig): ubench configuration
        """
        # pylint: disable=super-init-not-called

        self.benchmark_manager_list = []
        self.platform = platform_name

        for benchmark_name in benchmark_names:
            if benchmark_name in uconf.get_benchmark_list():
                # Benchmark type should be checked and BenchmarkManager instance
                # should be chosen accordingly.
                self.benchmark_manager_list.append(
                    jbm.JubeBenchmarkManager(benchmark_name, platform_name, uconf))


    def run(self, opt_dict={}):  # pylint: disable=dangerous-default-value,arguments-differ
        """ Executes run command.

        Run benchmarks on a given platform and write a ubench.log file in
        each benchmark run directory.

        Args:
             platform (string): name of the platform used to retrieve parameters needed to
                                run the benchmark.
             opt_dict (dictionnary): values passed to unclebench at the command line
        """

        for bench_m in self.benchmark_manager_list:
            bench_m.run(opt_dict)


    def list_parameters(self, default_values):
        """ List parameters on standard output.

        Args:
            default_values (boolean): value which if true, tries to interpret parameters.
        """

        for bench_m in self.benchmark_manager_list:
            bench_m.list_parameters(default_values)


    def set_parameter(self, dic_options): # pylint: disable=arguments-differ
        """ Set custom parameter from its name and a new value.

        Args:
            dic_options (dictionnary): dictionnary with old value as key and new value as value.
        """

        for bench_m in self.benchmark_manager_list:
            bench_m.set_parameter(dic_options)


    def print_log(self, idb=-1):
        """ Print log from a benchmark run

        Args:
            idb (int): id of the benchmark
        """

        for bench_m in self.benchmark_manager_list:
            try:
                bench_m.print_log(idb)
            except OSError as ose:
                print('    No run was found for '+\
                    '{0} benchmark with id {1}: '.format(bench_m.benchmark_name, str(idb)))
                print('    '+str(ose))
        print('')


    def list_runs(self):
        """ List benchmark runs with their IDs and status """

        for bench_m in self.benchmark_manager_list:
            try:
                bench_m.list_runs()
            except OSError as ose:
                print('    No run was found for {0} benchmark :'.\
                    format(bench_m.benchmark_name))
                print('    '+str(ose))
            print('')


    def analyse(self, benchmark_id):
        """ Analyse benchmark results

        Arguments
            benchmark_id (int): id of the benchmark to analyze
        """

        for bench_m in self.benchmark_manager_list:
            print('----analysing {0} results'.format(bench_m.benchmark_name))
            try:
                bench_m.analyse(benchmark_id)
            except IOError:
                print('----no {0} run found'.format(bench_m.benchmark_name))


    def analyse_last(self):
        """ Analyse last benchmark results """

        for bench_m in self.benchmark_manager_list:
            bench_m.analyse_last()


    def extract_results(self, benchmark_id):
        """ Get results from benchmark runs corresponding to benchmark_id
        and build python results array

        Args:
            benchmark_id (int): id of the benchmark to analyze
        """

        for bench_m in self.benchmark_manager_list:
            print('----extracting results')
            print('----benchmark results path: {0}'.format(bench_m.benchmark_results_path))
            try:
                bench_m.extract_results(benchmark_id)
            except IOError:
                print('----no result analyzer found, only'+\
                    ' raw results will be copied to the report directory')


    def extract_results_last(self):
        """ Get results from benchmarks last runs"""

        for bench_m in self.benchmark_manager_list:
            bench_m.extract_results_last()


    def print_result_array(self, output_file=None):
        """ Asciidoc printing result array

        Args:
            output_file (str): path of a file where to write the array,
        """

        for bench_m in self.benchmark_manager_list:
            bench_m.print_result_array(output_file)


    def print_transposed_result_array(self, output_file=None):
        """ Asciidoc printing of transposed result array

        Args:
            output_file (str): path of a file where to write the array,
        """

        for bench_m in self.benchmark_manager_list:
            bench_m.print_transposed_result_array(output_file)
