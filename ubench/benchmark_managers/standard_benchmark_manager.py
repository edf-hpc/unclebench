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
# pylint: disable=invalid-name
""" Define StandardBenchmarkManager class. """


from __future__ import print_function

import abc
import os
import re
import sys
import time
from shutil import copy, copytree

import six
import ubench.benchmark_managers.benchmark_manager as benm


@six.add_metaclass(abc.ABCMeta)  # pylint: disable=too-many-instance-attributes
class StandardBenchmarkManager(benm.BenchmarkManager):
    """ Abstract class that manages standard benchmarks.
    get_benchmarking_api method must be implemented by subclass to set
    a benchmarking API.

    Attributes:
        result_array (list)
        transposed_result_array (list)
        benchmark_results_path (str)
        benchmark_name (str)
        resource_dir (str)
        benchmark_path (str)
        benchmark_src_path (str)
        benchmarking_api (str)
        title (str)
        description (str)
        print_array (boolean)
        print_transposed_array (boolean)
        print_plot (boolean)
        plot_list (list)
    """

    def __init__(self, benchmark_name, platform, uconf):
        """ Class constructor

        Args:
            benchmark_name (str): name of the benchmark
            platform (str): name of the platform
            uconf (UbenchConfig): ubench configuration
        """
        # pylint: disable=super-init-not-called
        self.result_array = []
        self.transposed_result_array = []
        self.benchmark_results_path = ''
        self.benchmark_name = benchmark_name
        self.resource_dir = os.path.join(uconf.resource_dir, benchmark_name)
        self.benchmark_path = os.path.join(uconf.run_dir, platform, benchmark_name)
        self.benchmark_src_path = os.path.join(uconf.benchmark_dir, benchmark_name)
        self.platform = platform

        # Default report parameters
        self.title = benchmark_name
        self.description = ''
        self.print_array = True
        self.print_transposed_array = False
        self.print_plot = False
        self.plot_list = []
        # Initialize directory first
        self.benchmarking_api = self.get_benchmarking_api()


    @abc.abstractmethod
    def get_benchmarking_api(self):
        """ Factory method that should be implemented to return a benchmarking API
        """

    # # # # #       BENCHMARK       # # # # #
     # # # #                         # # # #
      # # #                           # # #
       # #                             # #
        #                               #


    def _init_run_dir(self, platform):  # pylint: disable=unused-argument
        """ Create and initialize run directory

        Args:
            platform (str): name of the platform used to retrieve parameters needed
                            to run the benchmark.
        """

        parent_run_dir = os.path.abspath(os.path.join(self.benchmark_path, os.pardir))
        src_dir = self.benchmark_src_path
        dest_dir = self.benchmark_path

        if not os.path.exists(parent_run_dir):
            try:
                os.makedirs(parent_run_dir)
            except (FileExistsError, OSError) as e:
                print('Error while making directory {0} : {1}'.format(parent_run_dir, str(e)))

        try:
            copytree(src_dir, dest_dir, symlinks=True)
        except OSError:
            print("---- {} description files are already present in " \
                  "run directory and will be overwritten.".format(self.benchmark_name))

        print("---- Copying {} to {}".format(src_dir, dest_dir))

        for f in os.listdir(src_dir):
            copy(os.path.join(src_dir, f), dest_dir)


    def run(self, opt_dict={}): # pylint: disable=arguments-differ
        """ Run benchmark on a given platform and write a ubench.log file in
        the benchmark run directory.

        Args:
            opt_dict (dict): dictionary with the options sent to unclebench
        """
        # pylint: disable=dangerous-default-value, too-many-locals, too-many-branches
        self._init_run_dir(self.platform)
        # Set custom node configuration
        if opt_dict['w']:
            w_list = opt_dict['w']
            try:
                nnodes_list = [list(t) for t in zip(*w_list)][0]
                nodes_id_list = [list(t) for t in zip(*w_list)][1]
                # unique values in list
                if len(list(set(nodes_id_list))) == 1 and not nodes_id_list[0]:
                    nodes_id_list = None

                self.benchmarking_api.set_custom_nodes(nnodes_list, nodes_id_list)
            except (ValueError, IndexError):
                print('Custom node configuration is not valid.')
                raise

        if opt_dict['execute']:
            self.benchmarking_api.set_execution_only_mode()

        if not opt_dict['foreground']:
            print('---- Launching benchmark in background')

        try:
            run_dir, ID = self.benchmarking_api.run()
        except (RuntimeError, OSError) as rerror:
            print('---- Error launching benchmark :')
            print(str(rerror))
            raise

        print("---- benchmark run directory: {}".format(run_dir))
        logfile_path = os.path.join(run_dir, 'ubench.log')
        date = time.strftime("%c")
        flattened_w_list = ''
        if 'w_list' in opt_dict:
            for nnodes, nodes_id in w_list:
                if nodes_id:
                    flattened_w_list += str(nodes_id) + ' '
                else:
                    flattened_w_list += str(nnodes) + ' '
        else:
            flattened_w_list = 'default'

        with open(logfile_path, 'w') as logfile:
            logfile.write('Benchmark_name  : {0} \n'.format(self.benchmark_name))
            logfile.write('Platform        : {0} \n'.format(self.platform))
            logfile.write('ID              : {0} \n'.format(ID))
            logfile.write('Date            : {0} \n'.format(date))
            logfile.write('Run_directory   : {0} \n'.format(run_dir))
            logfile.write('Nodes           : {0} \n'.format(flattened_w_list))
            if 'raw_cli' in opt_dict:
                logfile.write('cmdline         : {0} \n'.format(' '.join(opt_dict['raw_cli'])))

        print("---- Use the following command to follow benchmark progress: "\
              "ubench log -p {0} -b {1} -i {2}".format(self.platform,
                                                       self.benchmark_name, ID))
        if opt_dict['foreground']:
            print('---- Waiting benchmark to finish running')
            self.benchmarking_api.wait_run(ID, run_dir)
            print('---- All jobs or processes in background have finished')


    def list_parameters(self, default_values):
        """ List parameters on standard output. TODO improve default values mode.

        Args:
            default_values (bool): if true, tries to interpret parameters.
        """

        print(self.benchmark_src_path)
        all_parameters = self.benchmarking_api.list_parameters(default_values)
        for type_param in all_parameters:
            print("\n")
            if default_values:
                print("DEFAULT PARAMETER VALUES\n")
            print("{} parameters".format(type_param))
            print("-----------------------------------------------")
            for parameter, value in all_parameters[type_param]:
                print(parameter.rjust(20)+' : '+value)

    def set_parameter(self, dict_options):
        """ Set custom parameter from its name and a new value.

        Args:
            dict_options: dictionary with old value as key and new value as value.
        """
        modified_params = self.benchmarking_api.set_parameter(dict_options)
        for elem in modified_params:
            print('---- {0} parameter was modified from {1} to {2} for this run'.format(*elem))
        return


    # # # # #       ANALYZE       # # # # #
     # # # #                       # # # #
      # # #                         # # #
       # #                           # #
        #                             #


    def print_log(self, idb=-1):
        """ Print log from a benchmark run

        Args:
            idb (int): id of the benchmark
        """

        try:
            print(self.benchmarking_api.get_log(idb))
        except (IOError, OSError) as io_error:
            print('---- Error: cannot find benchmark logs :')
            print(str(io_error))
            raise

    def list_runs(self):
        """ List benchmark runs with their IDs and status """
        # pylint: disable=too-many-locals, too-many-branches

        field_pattern = re.compile(r'(\S+).*: (.*)')  # pylint: disable=unused-variable
        field_dict = {}  # pylint: disable=unused-variable
        sorted_key_list = []  # pylint: disable=unused-variable
        nbenchs = 0

        # Retrieve informations from ubench.log files found in the benchmark directory.
        # Informations are organized in a dictionnary.
        logfile_paths = []

        try:
            result_root_dir = os.path.join(self.benchmark_path,
                                           self.benchmarking_api.jube_files.get_bench_outputdir())
        except OSError as ose:
            print('    No run was found for {0} benchmark :'.\
                  format(self.benchmark_name))
            print("    {}".format(ose))

        for fd in os.listdir(result_root_dir):
            for filename in os.listdir(os.path.join(result_root_dir, fd)):
                if filename == 'ubench.log':
                    logfile_paths.append(os.path.join(result_root_dir, fd, 'ubench.log'))

        # The second loop is need to parse files in a sorted order.
        list_data = {}
        for filepath in sorted(logfile_paths):
            with open(filepath, 'r') as logfile:
                nbenchs += 1
                list_data[nbenchs] = {}
                fields = field_pattern.findall(logfile.read())
                for field in fields:
                    if field[0] == 'Run_directory':
                        list_data[nbenchs][field[0]] = os.path.dirname(filepath)
                    else:
                        list_data[nbenchs][field[0]] = field[1].strip()

        if not list_data:
            print('----no benchmark run found for : {0}'.format(self.benchmark_name))

        # Print dictionnary with a table layout.
        separating_line = ''
        columns = list(set([c for x in list(list_data.keys()) for c in list(list_data[x].keys())]))

        max_dict = {k:0 for k in columns}

        for data in list(list_data.values()):
            max_dict.update({k:max([v, len(data[k])])\
                             for k, v in list(max_dict.items()) if k in data})

        if 'Platform' in columns:
            columns.remove('Platform')
        if 'Benchmark_name' in columns:
            columns.remove('Benchmark_name')

        if list(list_data.values()):
            header = list(list_data.values())[0]
            print('\nPlatform: {0} \nBenchmark: {1}\n'.
                  format(header['Platform'], header['Benchmark_name']))

        for column in columns:
            sys.stdout.write(column.ljust(max_dict[column]) + ' | ')
            separating_line += '-' * (max_dict[column]+2)

        separating_line += '-' * (len(columns)-1)
        print('')
        print(separating_line)

        for bench in list(list_data.values()):
            for column in columns:
                if column in bench:
                    sys.stdout.write(bench[column].ljust(max_dict[column]) + ' | ')
                else:
                    sys.stdout.write(''.ljust(max_dict[column]) + ' | ')
            print('')


    def analyse(self, benchmark_id):
        """ Analyse benchmark results

        Args:
            benchmark_id (int): id of the benchmark to analyze
        """
        self.benchmark_results_path = self.benchmarking_api.analyse(benchmark_id)


    def extract_results(self, benchmark_id):
        """ Get result from a jube benchmark with its id and build a python result array

        Args:
            benchmark_id (int): id of the benchmark to analyze
        """

        self.result_array = self.benchmarking_api.extract_results(benchmark_id)
        self.benchmarking_api.write_bench_data(benchmark_id)
        self.transposed_result_array = [list(x) for x in zip(*self.result_array)]


    # # # # #       REPORT      # # # # #
     # # # #                     # # # #
      # # #                       # # #
       # #                         # #
        #                           #


    def print_result_array(self, output_file=None):
        """ Asciidoc printing of Jube result array

        Args:
            output_file (str): path of a file where to write the array.
                               If not set the array is printed on stdout.
        """

        result_array = self.result_array

        self.result_array = result_array
        if output_file:
            output_file.write('[options="header"]\n')
            output_file.write('|=== \n')
            for row in self.result_array:
                output_file.write('|')
                output_file.write('|'.join(row).replace('\n', ''))
                output_file.write('\n')
            output_file.write('|=== \n')
        else:
            # Print formatted array on stdout
            max_width = []
            for row in self.result_array:
                col = 0
                for elem in row:
                    if (len(max_width)-1) < col:
                        max_width.append(len(elem))
                    else:
                        max_width[col] = max(max_width[col], len(elem))
                    col += 1

            print('')
            for row in self.result_array:
                col = 0
                for elem in row[:-1]:
                    print(str(elem).ljust(max_width[col]+1), end=' ')
                    col += 1
                if row[-1]:
                    print(str(row[-1]).strip())
                else:
                    print('')
            print('')


    def print_transposed_result_array(self, output_file=None):
        """ Asciidoc printing of transposed Jube result array

        Args:
            output_file (str): path of a file where to write the array.
                               If not set the array is printed on stdout.
        """

        if output_file:
            output_file.write('[options="header"]\n')
            output_file.write('|=== \n')

            for row in self.transposed_result_array:
                output_file.write('|')
                output_file.write('|'.join(row).replace('\n', ''))
                output_file.write('\n')
            output_file.write('|=== \n')
