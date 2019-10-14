"""
Define BenchmarkManager abstract class.
"""

import abc
import six

@six.add_metaclass(abc.ABCMeta)
class BenchmarkManager():
    """
    Abtract class that defines the interface to manage a benchmark.
    """


    @abc.abstractmethod
    def __init__(self, benchmark_names, platform_name, uconf):
        """ Constructor
        :param benchmark_name: name of the benchmark
        :type benchmark_name: str
        :param benchmark_path: absolute path of the benchmark root directory.
        :type benchmark_path: str
        :param uconf: ubench configuration
        :type uconf: UbenchConfig
        """

    @abc.abstractmethod
    def run(self, platform, opt_dict={}):
        """ Run benchmark on a given platform and write a ubench.log file in
        the benchmark run directory.
        :param platform: name of the platform used to retrieve parameters needed to run
        the benchmark.
        :type platform: str
        :param w_list: nodes configurations used to run the benchmark.
        :type w_list: list of tuples [(number of nodes, nodes id list), ....]
        :param raw_cli: raw command line used to call ubench run
        :type raw_cli: str
        """

    @abc.abstractmethod
    def list_parameters(self, default_values):
        """
        List parameters on standard output. TODO improve default values mode.
        :param default_values: If true, tries to interpret parameters.
        :type default_values: boolean
        """

    @abc.abstractmethod
    def set_parameter(self, dict_options):
        """
        Set custom parameter from its name and a new value.
        :param parameter_name: name of the parameter to customize
        :type parameter_name:
        :param value: value to substitute to old value
        :type value: str
        :returns: Return a list of tuples [(filename,param1,old_value,new_value),
        (filename,param2,old_value,new_value),....]
        :rtype: List of 3-tuples ex:[(parameter_name,old_value,value),....]
        """

#===============      Analyze part   ===============#
    @abc.abstractmethod
    def print_log(self, idb=-1):
        """ Print log from a benchmark run
        :param idb: id of the benchmark
        :type idb:int
        """

    @abc.abstractmethod
    def list_runs(self):
        """ List benchmark runs with their IDs and status """

    @abc.abstractmethod
    def analyse(self, benchmark_id):
        """ Analyse benchmark results
        :param benchmark_id: id of the benchmark to analyze
        :type benchmark_id: int"""

    @abc.abstractmethod
    def extract_results(self, benchmark_id):
        """ Get result from a benchmark with its id and build a python result array
        :param benchmark_id: id of the benchmark to analyze
        :type benchmark_id: int"""

    @abc.abstractmethod
    def analyse_last(self):
        """ Analyse last benchmark results """

    @abc.abstractmethod
    def extract_results_last(self):
        """ Get last result from a  benchmark """

    @abc.abstractmethod
    def print_result_array(self, debug_mode=False, output_file=None):
        """ Asciidoc printing result array
        :param output_file:  path of a file where to write the array,
        if not set the array is printed on stdout.
        :type output_file: string"""

    @abc.abstractmethod
    def print_transposed_result_array(self, output_file=None):
        """ Asciidoc printing of transposed result array
        :param output_file:  path of a file where to write the array,
        if not set the array is printed on stdout.
        :type output_file: string"""
