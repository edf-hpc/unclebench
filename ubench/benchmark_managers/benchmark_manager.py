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
""" Define BenchmarkManager abstract class """


import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BenchmarkManager():
    """  Abtract class that defines the interface to manage a benchmark.
    """


    @abc.abstractmethod
    def __init__(self, benchmark_names, platform_name, uconf):
        """ Class constructor

        Args:
            benchmark_name (string): name of the benchmark
            platform_name (string): name fo the platform
            uconf (UbenchConfig): ubench configuration
        """


    @abc.abstractmethod
    def run(self):  # pylint: disable=dangerous-default-value
        """ Run benchmark on a given platform and write a ubench.log file in
        the benchmark run directory.

        Args:
            platform (string):  name of the platform used to retrieve parameters
                      needed to run the benchmark.
            opt_dict (dictionnary): with the options invoked at the command line
        """


    @abc.abstractmethod
    def list_parameters(self, default_values):
        """ List parameters on standard output.

        Args:
            default_values (bool): if true, tries to interpret parameters.
        """


    @abc.abstractmethod
    def set_parameter(self, dict_options):
        """ Set custom parameter from its name and a new value.

        Args:

        Returns:
            list of tuples [(filename,param1,old_value,new_value),
                            (filename,param2,old_value,new_value), ...]
        """


    # # # # #      Analyze part      # # # # #
     # # # #                          # # # #
      # # #                            # # #
       # #                              # #
        #                                #


    @abc.abstractmethod
    def print_log(self, idb=-1):
        """ Print log from a benchmark run

        Args:
            idb: (int) id of the benchmark
        """


    @abc.abstractmethod
    def list_runs(self):
        """ List benchmark runs with their IDs and status """


    @abc.abstractmethod
    def analyse(self, benchmark_id):
        """ Analyse benchmark results

        Args:
            benchmark_id: (int) id of the benchmark to analyze
        """


    @abc.abstractmethod
    def extract_results(self, benchmark_id):
        """ Get result from a benchmark with its id and build a python result array

        Args:
            benchmark_id: (int) id of the benchmark to analyze
        """


    @abc.abstractmethod
    def analyse_last(self):
        """ Analyse last benchmark results """


    @abc.abstractmethod
    def extract_results_last(self):
        """ Get last result from a  benchmark """


    @abc.abstractmethod
    def print_result_array(self, output_file=None):
        """ Asciidoc printing result array

        Args:
            output_file (string): path of a file where to write the array.
                                  If not set the array is printed to stdout.
            debug_mode (boolean):
        """


    @abc.abstractmethod
    def print_transposed_result_array(self, output_file=None):
        """ Asciidoc printing of transposed result array

        Args:
            output_file (string): path of a file where to write the array.
                                  If not set the array is printed to stdout.
        """
