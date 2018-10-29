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
"""
Define StandardBenchmarkManager class.
"""
import abc
import os
import re
import sys
import time
import ubench.core.ubench_config as uconfig
import ubench.benchmark_managers.benchmark_manager as benm
from shutil import copy,copytree

class StandardBenchmarkManager(benm.BenchmarkManager):
    """
    Abstract class that manages standard benchmarks.
    get_benchmarking_api method must be implemented by subclass to set
    a benchmarking API.
    """
    __metaclass__ = abc.ABCMeta


    def __init__(self, benchmark_name, platform, uconf):
        """ Constructor
        :param benchmark_name: name of the benchmark
        :type benchmark_name: str
        :param benchmark_path: absolute path of the benchmark root directory.
        :type benchmark_path: str
        :param uconf: ubench configuration
        :type uconf: UbenchConfig
        """
        self.result_array = []
        self.transposed_result_array = []
        self.benchmark_results_path = ''
        self.benchmark_name = benchmark_name
        self.resource_dir = os.path.join(uconf.resource_dir, benchmark_name)
        self.benchmark_path = os.path.join(uconf.run_dir, platform, benchmark_name)
        self.benchmark_src_path = os.path.join(uconf.benchmark_dir, benchmark_name)
        self.benchmarking_api=None

        # Default report parameters
        self.title = benchmark_name
        self.description = ''
        self.print_array = True
        self.print_transposed_array = False
        self.print_plot = False
        self.plot_list = []

    @abc.abstractmethod
    def get_benchmarking_api(self):
        """
        Factory method that should be implemented to return a benchmarking API
        """

#===============  Benchmarking part  ===============#

    def init_run_dir(self,platform):
        """ Create and initialize run directory
        :param platform: name of the platform used to retrieve parameters needed
        to run the benchmark.
        :type platform: str
        """
        parent_run_dir=os.path.abspath(os.path.join(self.benchmark_path, os.pardir))
        if not os.path.exists(parent_run_dir):
            try:
                os.makedirs(parent_run_dir)
            except Exception as e:
                print 'Error while making directory {0} : {1}'.format(parent_run_dir, str(e))

        src_dir = self.benchmark_src_path
        dest_dir = self.benchmark_path

        try:
            copytree(src_dir, dest_dir, symlinks=True)
        except OSError as oserror:
            print '---- '+self.benchmark_name+\
                ' description files are already present in run directory and will be overwritten.'
        print '---- Copying '+self.benchmark_src_path+' to '+self.benchmark_path

        for f in os.listdir(src_dir):
            copy(os.path.join(src_dir, f), dest_dir)

        if not self.benchmarking_api:
            self.benchmarking_api = self.get_benchmarking_api()



    def run(self, platform, w_list=None, raw_cli=None):
        """ Run benchmark on a given platform and write a ubench.log file in
        the benchmark run directory.
        :param platform: name of the platform used to retrieve parameters needed
        to run the benchmark.
        :type platform: str
        :param w_list: nodes configurations used to run the benchmark.
        :type w_list: list of tuples [(number of nodes, nodes id list), ....]
        :param raw_cli: raw command line used to call ubench run
        """

        self.init_run_dir(platform)

        # Set custom node configuration
        if w_list:
            try:
                nnodes_list = [list(t) for t in zip(*w_list)][0]
                nodes_id_list = [list(t) for t in zip(*w_list)][1]
                # unique values in list
                if len(list(set(nodes_id_list))) == 1 and not nodes_id_list[0]:
                    nodes_id_list = None

                self.benchmarking_api.set_custom_nodes(nnodes_list, nodes_id_list)
            except ValueError:
                print 'Custom node configuration is not valid.'
                return
            except IndexError:
                print 'Custom node configuration is not valid.'
                return

        print '---- Launching benchmark in background'
        try:
            run_dir, ID = self.benchmarking_api.run(platform)
        except RuntimeError as rerror:
            print '---- Error launching benchmark :'
            print str(rerror)
            return
        except OSError:
            print
            return

        print '---- benchmark run directory :', run_dir
        logfile_path = os.path.join(run_dir, 'ubench.log')
        date = time.strftime("%c")
        flattened_w_list = ''
        if w_list:
            for nnodes, nodes_id in w_list:
                if nodes_id:
                    flattened_w_list += str(nodes_id)+' '
                else:
                    flattened_w_list += str(nnodes)+' '
        else:
            flattened_w_list = 'default'

        with open(logfile_path, 'w') as logfile:
            logfile.write('Benchmark_name  : {0} \n'.format(self.benchmark_name))
            logfile.write('Platform        : {0} \n'.format(platform))
            logfile.write('ID              : {0} \n'.format(ID))
            logfile.write('Date            : {0} \n'.format(date))
            logfile.write('Run_directory   : {0} \n'.format(run_dir))
            logfile.write('Nodes           : {0} \n'.format(flattened_w_list))
            logfile.write('cmdline         : {0} \n'.format(' '.join(raw_cli)))

        print '---- Use the following command to follow benchmark progress :'\
            +'    " ubench log -p {0} -b {1} -i {2}"'.format(platform, self.benchmark_name, ID)

    def list_parameters(self, default_values):
        """
        List parameters on standard output. TODO improve default values mode.
        :param default_values: If true, tries to interpret parameters.
        :type default_values: boolean
        """
        print self.benchmark_src_path
        if not self.benchmarking_api:
            self.benchmarking_api = self.get_benchmarking_api()
        all_parameters = self.benchmarking_api.list_parameters(default_values)
        for type_param in all_parameters:
            print "\n"
            if default_values:
                print "DEFAULT PARAMETER VALUES\n"
            print type_param + " parameters"
            print "-----------------------------------------------"
            for parameter, value in all_parameters[type_param]:
                print parameter.rjust(20)+' : '+value

    def set_parameter(self, dict_options):
        """
        Set custom parameter from its name and a new value.
        : param dic_options: dictionnary with old value as key and new value as value.
        : type dic_options: dictionary
        """
        if not self.benchmarking_api:
            self.benchmarking_api = self.get_benchmarking_api()
        modified_params = self.benchmarking_api.set_parameter(dict_options)
        for elem in modified_params:
            print '---- {0} parameter was modified from {1} to {2} for this run'.format(*elem)
        return

#===============      Analyze part   ===============#
    def print_log(self, idb=-1):
        """ Print log from a benchmark run
        :param idb: id of the benchmark
        :type idb:int
        """
        try:
            if not self.benchmarking_api:
                self.benchmarking_api = self.get_benchmarking_api()
            print self.benchmarking_api.get_log(idb)
        except IOError as io_error:
            print '---- Error: cannot find benchmark logs :'
            print str(io_error)
            return

    def list_runs(self):
        """ List benchmark runs with their IDs and status """
        field_pattern = re.compile(r'(\S+).*: (.*)')
        field_dict = {}
        sorted_key_list = []
        nbenchs = 0
        # Retrieve informations from ubench.log files found in the benchmark directory.
        # Informations are organized in a dictionnary.
        logfile_paths = []
        if not self.benchmarking_api:
            self.benchmarking_api = self.get_benchmarking_api()
        result_root_dir = self.benchmarking_api.get_results_root_directory()
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
            print '----no benchmark run found for : {0}'.format(self.benchmark_name)

        # Print dictionnary with a table layout.

        separating_line = ''
        columns = list(set([c for x in list_data.keys() for c in list_data[x].keys()]))

        max_dict = {k:0 for k in columns}

        for data in list_data.values():
            max_dict.update({k:max([v, len(data[k])])\
                             for k, v in max_dict.items() if data.has_key(k)})

        if 'Platform' in columns:
            columns.remove('Platform')
        if 'Benchmark_name' in columns:
            columns.remove('Benchmark_name')

        if len(list_data.values()) > 0:
            header = list_data.values()[0]
            print "\nPlatform: {0} \nBenchmark: {1}\n".\
                format(header['Platform'], header['Benchmark_name'])

        for column in columns:
            sys.stdout.write(column.ljust(max_dict[column])+' | ')
            separating_line += '-'*(max_dict[column]+2)

        separating_line += '-'*(len(columns)-1)
        print ''
        print separating_line

        for bench in list_data.values():
            for column in columns:
                if bench.has_key(column):
                    sys.stdout.write(bench[column].ljust(max_dict[column])+' | ')
                else:
                    sys.stdout.write(''.ljust(max_dict[column])+' | ')
            print ''


    def analyse(self, benchmark_id):
        """ Analyse benchmark results
        :param benchmark_id: id of the benchmark to analyze
        :type benchmark_id: int"""
        if not self.benchmarking_api:
            self.benchmarking_api = self.get_benchmarking_api()
        self.benchmark_results_path = self.benchmarking_api.analyse(benchmark_id)

    def extract_results(self, benchmark_id):
        """ Get result from a jube benchmark with its id and build a python result array
        :param benchmark_id: id of the benchmark to analyze
        :type benchmark_id: int"""
        if not self.benchmarking_api:
            self.benchmarking_api = self.get_benchmarking_api()
        self.result_array = self.benchmarking_api.extract_results(benchmark_id)
        self.benchmarking_api.write_bench_data(benchmark_id)
        self.transposed_result_array = [list(x) for x in zip(*self.result_array)]

    def analyse_last(self):
        """ Get last result from a jube benchmark """
        self.benchmark_results_path = self.benchmarking_api.analyse_last()

    def extract_results_last(self):
        """ Get last result from a jube benchmark """
        self.result_array = self.benchmarking_api.extract_results_last()
        self.transposed_result_array = [list(x) for x in zip(*self.result_array)]

#===============    Reporting part   ===============#

    def print_result_array(self, debug_mode=False,output_file=None):
        """ Asciidoc printing of Jube result array
        :param output_file:  path of a file where to write the array,
        if not set the array is printed on stdout.
        :type output_file: string"""
        result_array=self.result_array
        for i in range(0,len(result_array)/2):
            result_array[i].append(result_array[len(result_array)/2+i][0])

        result_array=result_array[:len(result_array)/2]
        if not debug_mode:
            for i in range(0,len(result_array)):
                result_array[i]=result_array[i][:len(result_array[i])-1]
        self.result_array=result_array
        if output_file:
            output_file.write('[options="header"]\n')
            output_file.write('|=== \n')
            for row in self.result_array:
                output_file.write('|')
                output_file.write('|'.join(row).replace("\n", ""))
                output_file.write('\n')
            output_file.write('|=== \n')
        else:
            # print formatted array on stdout
            max_width = []
            for row in self.result_array:
                col = 0
                for elem in row:
                    if (len(max_width)-1) < col:
                        max_width.append(len(elem))
                    else:
                        max_width[col] = max(max_width[col], len(elem))
                    col += 1

            print ''
            for row in self.result_array:
                col = 0
                for elem in row[:-1]:
                    print str(elem).ljust(max_width[col]+1),
                    col += 1
                if row[-1]:
                    print str(row[-1]).strip()
                else:
                    print ''
            print ''


    def print_transposed_result_array(self, output_file=None):
        """ Asciidoc printing of transposed Jube result array
        :param output_file:  path of a file where to write the array,
        if not set the array is printed on stdout.
        :type output_file: string"""
        if output_file:
            output_file.write('[options="header"]\n')
            output_file.write('|=== \n')

            for row in self.transposed_result_array:
                output_file.write('|')
                output_file.write('|'.join(row).replace("\n", ""))
                output_file.write('\n')
            output_file.write('|=== \n')
