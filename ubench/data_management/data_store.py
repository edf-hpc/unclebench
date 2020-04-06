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
""" Provides DataStore class """


import abc
import datetime
import os
import pandas # pylint: disable=import-error
import six


def _read_date(date_str):
    """  Read date from string.

    Args:
        date_str (str): string containing some date

    Returns:
        datetime object with the following format - Tue May 15 17:15:08 2018
    """
    date_time = datetime.datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')

    return date_time


@six.add_metaclass(abc.ABCMeta)
class DataStore(object):
    """ Load, write, extract data from unclebench performance results data files.

    Methods
        write:
        load:
        extract_data_from_file:
        file_to_panda:
        dir_to_pandas:
    """

    def __init__(self):
        """ Class contructor """
        pass


    @abc.abstractmethod
    def write(self, metadata, data, output_file):
        """

        Args:
            metadata
            data
            output_file
        """
        pass


    @abc.abstractmethod
    def load(self, input_file):
        """

        Args:
            input_file
        """
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

        metadata, data = self.load(filename)
        if not data:
            return (None, None)

        # Check if benchmark_name corresponds
        if benchmark_name != metadata['Benchmark_name']:
            return(None, None)

        # Check if dates correspond
        if date_interval:
            run_date = _read_date(metadata['Date'])
            if (run_date < date_interval[0]) or (run_date > date_interval[1]):
                return(None, None)

        return(metadata, data)


    def file_to_panda(self, filename, benchmark_name,
                      date_interval=None, context=(None, None),
                      d_filter=None):
        """ Return a panda from a file if it is an unclebench performance data file
        with date and benchmark name correponding to those given as argument.

        Args:
            filename
            benchmark_name
            date_interval
            context
        """
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements

        def get_data(data, d_filter):
            filter_data = {}
            for index in data:
                new_data = {k:v for k, v in d_filter.items() if data[index][k] == v}
                if len(new_data) == len(d_filter):
                    filter_data[index] = data[index]

            return filter_data

        if date_interval:
            metadata, data = self.extract_data_from_file(filename, benchmark_name, date_interval)
        elif d_filter:
            metadata, data = self.load(filename)
            data = get_data(data, d_filter)
        else:
            metadata, data = self.load(filename)

        if not context[0]:
            context = ([], context[1])
        if not context[1]:
            context = (context[0], None)

        # File is not corresponding
        if not metadata:
            return ({}, pandas.DataFrame(), (None, None), None)

        # Find context in data if not provided
        if not context[0]:
            for id_exec in sorted(data.keys()):  # This guarantees the order of nodes
                if not context[0]:
                    context = (set(data[id_exec]['context_fields']), context[1])
                else:
                    context = (context[0].intersection(set(data[id_exec]['context_fields'])), \
                               context[1])
            context = list(context[0]), context[1]
        else:
            pass

        if context[1]:
            full_context = context[0] + [context[1]]
        else:
            full_context = context[0]

        # Check if there are sub_benchcolumn_headers
        result_name_column = None
        for id_exec in sorted(data.keys()):  # This guarantees the order of nodes
            result_name_column = metadata['Benchmark_name'] + '_results'

        # Build report_info dictionnary
        report_info = {}
        for column in context[0] + ['result']:
            report_info[column] = []
        if result_name_column:
            report_info[result_name_column] = []

        # Check if contexts are coherent
        if context[0] and context[1]:
            for ctx in context[0]:
                if ctx in [context[1]]:
                    print('Error : {} is in both column and row contexts'
                          .format(ctx))  # pylint: disable=superfluous-parens
                    return({}, pandas.DataFrame(), (None, None), None)

        # Fill report_info
        # This guarantees the order of nodes
        for id_exec in sorted(data.keys()):  # pylint: disable=too-many-nested-blocks
            value = data[id_exec]

            # Result categories can be considered as context
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
                        for index, res in enumerate(result):
                            for column in set(full_context) - set(context_key):
                                if not column in report_info:
                                    report_info[column] = []
                                report_info[column].append(value[column])
                            try:
                                report_info[ctx_key].append(
                                    int(value['results_bench'][ctx_key][index]))
                            except:  # pylint: disable=bare-except
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
                            print(('Error, context {} does not exist for benchmark {}'
                                   .format(column, benchmark_name)))
                            exit(1)  # pylint: disable=pointless-statement

                    report_info['result'].append(result)
                    if result_name_column:
                        report_info[result_name_column].append(key)

        # Return a tuple
        return (metadata, pandas.DataFrame(report_info), context, result_name_column)


    def dir_to_pandas(self, data_dir, benchmark_name,
                      date_interval=None, context=(None, None),
                      result_filter=None):
        """ Load evry data file found in "data_dir" and return a list
        of dictionnaries, each one containing data from a file.

        Args:
            data_dir
            benchmark_name
            date_interval
            context
            result_filter (dic): keys are benchmark name, values are names of the measure to keep.
                                  No value means that all measures will be considered.
        """
        # pylint: disable=too-many-locals, too-many-branches, too-many-arguments

        concatenated_panda = pandas.DataFrame()
        result_context = None
        sub_bench = None
        concatenated_metadata = {}

        if not os.path.isdir(data_dir):
            print(('Cannot find ' + data_dir + ' directory'))  # pylint: disable=superfluous-parens
            exit(1)

        for (dirpath, dirnames, filenames) in os.walk(data_dir):  # pylint: disable=unused-variable
            for fname in filenames:
                metadata, current_panda, current_context, current_sub_bench \
                    = self.file_to_panda(os.path.join(dirpath, fname), \
                                          benchmark_name, date_interval, context)

                if current_panda.empty:
                    continue

                # Apply filter to results, usefull to avoid printing part of benchmark
                # results that would not be meaningfull.
                if result_filter:
                    if benchmark_name in result_filter:
                        if result_filter[benchmark_name]:
                            result_field_name = benchmark_name+"_results"
                            current_panda = current_panda[
                                current_panda[result_field_name].
                                isin(result_filter[benchmark_name])]

                if concatenated_panda.empty:
                    concatenated_panda = current_panda
                else:
                    concatenated_panda = pandas.concat(# pylint: disable=redefined-variable-type
                        [concatenated_panda, current_panda]
                    )

                for field, value in list(metadata.items()):
                    if not field in concatenated_metadata:
                        concatenated_metadata[field] = []
                    concatenated_metadata[field].append(value)

                if (result_context) and (result_context != current_context):
                    print('Different result files structure for benchmark {}.'
                          .format(benchmark_name))
                    print('Different context found : {} and {}'
                          .format(str(current_context), str(result_context)))
                else:
                    result_context = current_context

                if (sub_bench) and (sub_bench != current_sub_bench):
                    print('Different result files structure for benchmark {}.'
                          .format(benchmark_name))
                    print('Two different result_bench fields : {} and {}'
                          .format(current_sub_bench, sub_bench))
                else:
                    sub_bench = current_sub_bench

        if not result_context:
            result_context = (None, None)

        return concatenated_metadata, concatenated_panda, result_context, sub_bench



    def compaire_bench_runs(self, pre_result_file, post_result_file, result_filter, run_context):
        """Compute the diff between two benchmarks results
        run_context => string
        """

        metadata, df1, _, _ = self.file_to_panda(pre_result_file, "",
                                          context=(None,run_context),
                                          d_filter=result_filter)

        _, df2, _, _ = self.file_to_panda(post_result_file, "",
                                          context=(None,run_context),
                                          d_filter=result_filter)

        dfs = [df1, df2]

        for index, df in enumerate(dfs):
            df['result'] = df['result'].astype(float)
            df.rename(columns={'result':"result{}".format(index)}, inplace=True)

        merge_df = pandas.concat(dfs, axis=1)
        merge_df = merge_df.T.drop_duplicates().T
        merge_df['diff'] = 100*(merge_df['result0']-merge_df['result1'])/merge_df['result0']

        # we create a dictionary only with the name of the result column and its difference value
        result_column = metadata['Benchmark_name'] + '_results'
        result = {}
        for record in merge_df.to_dict(orient='records'):
            result[record[result_column]] = record['diff']

        return result


    def get_result_filter(self, run_selector, opts, result_file):
        """ Returns a filter

        - run_selector: dictionary it allows to select a benchmark run based
          on a variable which value is contained in the value of a given run.
          Example {'jube_wp_abspath' : '00000_execute' }  will select a run
          in which 'jube_wp_abspath' has a value 'benchmark_runs/000000/00000_execute/work'

        - opts: list of variables that have to be included in the filter

        - file: Benchmark data file
        """

        # load file
        _, run_info = self.load(result_file)
        s_run = {}
        for index, data in run_info.items():
            # the
            selected = {k : v for k, v in run_selector.items() if v in data[k]}
            if len(selected) == len(run_selector):
                s_run = data
                break

        if not opts:
            opts = {}

        columns = s_run['context_fields'] + opts.keys()

        return {k :s_run[k] for k in columns}
