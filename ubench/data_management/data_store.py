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

import abc
import datetime
import os
import pandas
import six

def _read_date(date_str):
    """
    Read date from string.
    Tue May 15 17:15:08 2018
    """
    date_time = datetime.datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')

    return date_time

@six.add_metaclass(abc.ABCMeta)
class DataStore():
    """
    Load, write, extract data from unclebench performance results data files.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def write(self, metadata, data, output_file):
        pass

    @abc.abstractmethod
    def load(self, input_file):
        pass

    def extract_data_from_file(self, filename, benchmark_name, date_interval=None):
        """ Extract benchmark performance data from a file.

        Data are extracted if the benchmark date lies in date_interval and
        the benchmark is benchmark_name.

        Args:
            filename: name of the file containing data.
            benchmark_name: name of the benchmark.
            date_interval: tuple with two dates with the following format :
                           Tue May 18 14:12:02 2038

        Returns:
            A tuple containaing two dictionnaries, one with metadata which is
            information common to evry run. and one with information specific to
            each run.
        """
        metadata ,data = self.load(filename)
        if not (data):
            return (None,None)

        # Check if benchmark_name corresponds
        if benchmark_name != metadata["Benchmark_name"]:
            return(None,None)

        # Check if dates correspond
        if(date_interval):
            run_date = _read_date(metadata['Date'])
            if(run_date<date_interval[0]) or (run_date>date_interval[1]):
                return(None,None)

        return(metadata, data)

    def file_to_panda(self, filename, benchmark_name, date_interval=None, context=(None,None)):
        """
        Return a panda from a file if it is an unclebench performance data file
        with date and benchmark name correponding to those given as argument.
        """
        metadata, data = self.extract_data_from_file(filename, benchmark_name, date_interval)

        if not context[0]:
            context = ([], context[1])
        if not context[1]:
            context = (context[0], None)

        # File is not corresponding
        if not metadata:
            return ({}, pandas.DataFrame(), (None,None), None)

        # Find context in data if not provided
        if not context[0]:
            for id_exec in sorted(data.keys()): # this guarantees the order of nodes
                if not context[0]:
                    context = (set(data[id_exec]['context_fields']),context[1])
                else:
                    context = (context[0].intersection(set(data[id_exec]['context_fields'])), \
                               context[1])
            context = list(context[0]), context[1]
        else:
        # Check that context exists
            pass

        if context[1]:
            full_context = context[0]+[context[1]]
        else:
            full_context = context[0]

        # Check if there are sub_bench
        result_name_column = None
        for id_exec in sorted(data.keys()): # this guarantees the order of nodes
            result_name_column = metadata['Benchmark_name']+'_bench'

        # Build report_info dictionnary
        report_info = {}
        for column in context[0]+['result']:
            report_info[column] = []
        if result_name_column:
            report_info[result_name_column] = []

        # Check if contexts are coherent
        if context[0] and context[1]:
            for ctx in context[0]:
                if ctx in [context[1]]:
                    print(("Error : {} is in both column and row contexts".format(ctx)))
                    return({}, pandas.DataFrame(), (None,None), None)

        # Fill report_info
        for id_exec in sorted(data.keys()): # this guarantees the order of nodes
            value = data[id_exec]

            # result categories can be considered as context
            context_key = []
            for key, result in sorted(value['results_bench'].items()):
                if key in full_context:
                    context_key.append(key)

            # Only one value for hpl, multiple for hpcc
            for key, result in sorted(value['results_bench'].items()):

                if key in full_context:
                    continue

                # Case where a result field should be consired as context (ex: IMB)
                if context_key:
                    for ctx_key in context_key:
                        if not ctx_key in report_info:
                            report_info[ctx_key] = []
                        for index,res in enumerate(result):
                            for column in set(full_context)-set(context_key):
                                if not column in report_info:
                                    report_info[column] = []
                                report_info[column].append(value[column])
                            try:
                                report_info[ctx_key].append(int(value['results_bench'][ctx_key][index]))
                            except:
                                report_info[ctx_key].append(value['results_bench'][ctx_key][index])
                            report_info['result'].append(res)
                            if result_name_column:
                                report_info[result_name_column].append(key)
                else:
                    for column in full_context:
                        if column in value:
                            if not column in report_info:
                                report_info[column] = []
                            report_info[column].append(value[column])
                        else:
                            print(("Error, context {} does not exist for benchmark {}"\
                                  .format(column,benchmark_name)))
                            exit


                    report_info['result'].append(result)
                    if result_name_column:
                        report_info[result_name_column].append(key)

        # Return a tuple
        return (metadata, pandas.DataFrame(report_info), context, result_name_column)


    def dir_to_pandas(self, data_dir, benchmark_name, \
                      date_interval=None,context=(None,None)):
        """
        Load evry data file found in "data_dir" and return a list
        of dictionnaries, each one containing data from a file.
        """
        concatenated_panda = pandas.DataFrame()
        result_context = None
        sub_bench = None
        concatenated_metadata = {}

        if not os.path.isdir(data_dir):
            print(("Cannot find "+data_dir+" directory"))
            exit(1)

        for (dirpath, dirnames, filenames) in os.walk(data_dir):
            for fname in filenames:
                metadata, current_panda, current_context, current_sub_bench \
                    = self.file_to_panda(os.path.join(dirpath, fname), \
                                          benchmark_name, date_interval, context)

                if current_panda.empty:
                    continue
                if concatenated_panda.empty:
                    concatenated_panda = current_panda
                else:
                    concatenated_panda = pandas.concat([concatenated_panda, current_panda])

                for field, value in list(metadata.items()):
                    if not field in concatenated_metadata:
                        concatenated_metadata[field] = []
                    concatenated_metadata[field].append(value)

                if (result_context)and(result_context!=current_context):
                    print("Different result files structure for benchmark {}.".\
                        format(benchmark_name))
                    print("Different context found : {} and {}".\
                        format(str(current_context),str(result_context)))
                else:
                    result_context=current_context

                if (sub_bench)and(sub_bench != current_sub_bench):
                    print("Different result files structure for benchmark {}.".\
                        format(benchmark_name))
                    print("Two different result_bench fields : {} and {}".\
                        format(current_sub_bench, sub_bench))
                else:
                    sub_bench=current_sub_bench

        if (not result_context):
            result_context = (None,None)


        return concatenated_metadata, concatenated_panda, result_context, sub_bench
