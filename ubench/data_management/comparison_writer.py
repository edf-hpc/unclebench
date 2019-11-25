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
""" This module provides ComparisionWriter class """


import logging
import numpy as np
import pandas  # pylint: disable=import-error
from matplotlib import pyplot as plt

import ubench.data_management.data_store_yaml as dsy


class ComparisonWriter(object):
    """ ComparisionWriter class """


    def __init__(self, threshold=None):
        """ Class constructor

        Args:
            threshold
        """

        self.dstore = dsy.DataStoreYAML()
        self.threshold = threshold


    def write_cplot(self, c_list, sub_bench, sub_bench_list, context, output_filename):
        """ Plots comparision dataframes.

        Plot comparison dataframes in c_list, each dataframe corresponding to a sub
        benchmark listed in sub_bench_list.

        Args:
            c_list:
            sub_bench_list:
            context:
            output_filename:
        """
        # pylint: disable=too-many-arguments, too-many-locals, no-self-use

        try:
            import seaborn as sns
        except ImportError:
            logging.warning('seaborn failed to import graphs will not be generated', exc_info=True)
            return

        df_toplot = pandas.concat(c_list)
        column_headers = context[1]
        row_headers = context[0]

        # Choose facetgrid parameters according to row_headers and column_headers
        # defined with context variable.

        if [eld for eld in df_toplot[column_headers] if str(eld).isdigit()]:

            # column_headers are numeric, use them as x_axis
            x_data = column_headers
            if len(row_headers) > 1:

                # two row_headers are given
                # use the second one as row_label if it exists.
                row_label = row_headers[-1]
            else:
                row_label = row_headers[0]
        else:

            # column_headers are not numeric, probably a limited number
            # of possibility, use it as row labels for facets.
            x_data = row_headers[0]
            row_label = column_headers

        if len(sub_bench_list) > 1:
            # If benchmark is composed of sub benchmarks
            # use their names as hue label
            hue_label = sub_bench

            # If there are multiple row_headers use the last one
            # if not already used as row_label
            if len(row_headers) > 1:
                if (row_label != row_headers[-1]):
                    col_label = row_headers[-1]
                else:
                    col_label = row_headers[-2]
                    if len(row_headers) > 2:
                        col_label = row_headers[0]
                        row_label = row_headers[1]
                        hue_label = row_headers[2]
            else:
                col_label = None
        else:
            if len(row_headers) > 1:
                hue_label = row_headers[-1]
            else:
                hue_label = None
            col_label = None

        # pylint: disable=logging-format-interpolation
        logging.debug('row_label: {}\n col_label: {}\n hue_label: {}\n x_data: {}\n'
                      .format(row_label, col_label, hue_label, x_data))

        # Build FacetGrid graph
        facetg = sns.FacetGrid(data=df_toplot, row=row_label,
                               col=col_label, hue=hue_label, height=5,
                               aspect=1.2, sharex=True, sharey=False)

        # Choose base 2 log scale as this axis often represents bytes or
        # number of nodes
        plt.xscale('symlog', basex=2)

        facetg = facetg.map(plt.grid, linewidth=0.5,linestyle=':',color='k')
        facetg = facetg.map(plt.scatter, x_data, df_toplot.columns[-1]).add_legend()
        plt.savefig(output_filename)


    def print_comparison(self, benchmark_name, input_directories, context=(None, None)):
        """ Print arrays comparating results found in different input directories
        """

        df_to_print = self.compare(benchmark_name, input_directories, context)

        for dframe in df_to_print:
            print('')  # pylint: disable=superfluous-parens
            with pandas.option_context('display.max_rows', None, 'display.max_columns',
                                       None, 'expand_frame_repr', False):
                print((dframe.to_string(index=False)))  # pylint: disable=superfluous-parens

    def compare_pandas(self, pandas_list, context, session_list=None):
        """ Computes relative differences.

        Return a panda dataframe comparing multiple pandas with there result relative
        differences computed and added as a column.

        Args:
            pandas_list
            context
            session_list

        Returns:
            Pandas dataframe
        """
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements

        panda_ref = pandas_list[0]

        # Check context
        for key_f in context[0]:
            if key_f not in panda_ref:
                print(('    ' + str(key_f) +
                       ' is not a valid context field, valid context fields'
                       ' for given directories are:'))  # pylint: disable=superfluous-parens

                for cfield in panda_ref:
                    print(('     - '+str(cfield)))
                    return 'No result'

        result_columns_pre_merge = [x for x in list(panda_ref.columns.values)
                                    if x not in context[0]]

        # Do all but last merges keeping the original result field name unchanged
        idx = 0
        pd_compare = panda_ref
        for pdr in pandas_list[1:-1]:
            pd_compare = pandas.merge(pd_compare, pdr, on=context[0],
                                      suffixes=['', '_post_'+str(idx)])
            idx += 1

        # At last merge add a _pre suffix to reference result
        if len(pandas_list) > 1:
            pd_compare = pandas.merge(pd_compare, pandas_list[-1],
                                      on=context[0], suffixes=['_pre', '_post_' + str(idx)])
        else:
            pd_compare = panda_ref

        pd_compare_columns_list = list(pd_compare.columns.values)
        result_columns = [x for x in pd_compare_columns_list if x not in context[0]]
        ctxt_columns_list = context[0]

        if 'nodes' in ctxt_columns_list:
            ctxt_columns_list.insert(0, ctxt_columns_list.pop(ctxt_columns_list.index('nodes')))

        pd_compare = pd_compare[ctxt_columns_list+result_columns]

        pandas.options.mode.chained_assignment = None # Avoid useless warning

        # Convert numeric columns to int or float
        # pylint: disable=unnecessary-lambda
        for ccolumn in context[0]:
            try:
                pd_compare[ccolumn] = pd_compare[ccolumn].apply(lambda x: int(x))
            except: # pylint: disable=bare-except
                try:
                    pd_compare[ccolumn] = pd_compare[ccolumn].apply(lambda x: float(x))
                except:
                    continue

        # Add difference columns in % for numeric result columns
        diff_columns = []

        for rcolumn in result_columns_pre_merge:
            pre_column = rcolumn + '_pre'
            if session_list:
                pd_compare.rename(columns={pre_column:session_list[0]}, inplace=True)
                pre_column = session_list[0]
            for i in range(0, len(pandas_list[1:])):
                post_column = rcolumn + '_post_' + str(i)
                if session_list:
                    pd_compare.rename(columns={post_column:session_list[i+1]}, inplace=True)
                    post_column = session_list[i+1]
                try:
                    if session_list:
                        diff_column_name = session_list[i+1] + ' vs ' + session_list[0] + '(%)'
                    else:
                        diff_column_name = rcolumn + '_diff_' + str(i) + '(%)'

                    ref_col = pd_compare[pre_column].apply(ComparisonWriter._try_convert(np.nan,
                                                                                         float))
                    post_col = pd_compare[post_column].apply(ComparisonWriter._try_convert(np.nan,
                                                                                           float))
                    pd_compare[diff_column_name] = (post_col - ref_col) * 100 / ref_col
                    pd_compare[diff_column_name] = pd_compare[diff_column_name].round(2)

                except Exception: # pylint: disable=broad-except
                    continue
                else:
                    diff_columns.append(diff_column_name)

        # Remove rows with no difference above given threshold
        if self.threshold:

            # Add a column with max :
            pd_compare['max_diff'] = pd_compare[diff_columns].max(axis=1).abs()

            # Use it as a filter :
            pd_compare = pd_compare[pd_compare.max_diff > float(self.threshold)]
            pd_compare.drop('max_diff', 1, inplace=True)

        pandas.options.mode.chained_assignment = 'warn'  # Reactivate warning
        return pd_compare.sort_values(by=ctxt_columns_list)


    @staticmethod
    def _try_convert(default, *types):
        """ Internal method """

        def convert(value):  # pylint: disable=missing-docstring
            for t in types:  # pylint: disable=invalid-name
                try:
                    return t(value)
                except ValueError as TypeError: # pylint: disable=unused-variable, redefine-in-handler
                    continue
            return default
        return convert


    def compare(self, benchmark_name, input_directories, date_interval_list=None,
                context_in=(None, None), session_list=None, result_filter=None):
        """ Compare results of each input directory/date_interval combination,
        results from first combination are considered as the reference.

        Args:
            benchmark_name (str): name of the benchmark
            input_directories (list of str): list of directories
            date_interval_list (list of datetimes tuples): list of date intervals.
            context_in (list): list of tuples of the following form ([ctx0_0,ctx0_1,..],ctx1)
                        with ctx of str type.
            session_list (list):
            result_filter (dic): keys are benchmark name, values are names of the measure to keep.
                                  No value means that all measures will be considered.
        """
        # pylint: disable=too-many-arguments, too-many-locals, too-many-branches

        pandas_list = []
        context = (None, None)
        sub_bench = None
        metadata = {}  # pylint: disable=unused-variable
        config_list = []

        if date_interval_list:
            for rdir, d_interval in zip(input_directories, date_interval_list):
                config_list.append((rdir, d_interval))
        else:
            for rdir in input_directories:
                config_list.append((rdir, (None, None)))

        for input_dir, date_interval in config_list:

            metadata, current_panda, current_context, current_sub_bench \
                = self.dstore.dir_to_pandas(input_dir, benchmark_name,
                                            date_interval, context_in,
                                            result_filter)
            if current_panda.empty:
                continue

            pandas_list.append(current_panda)

            # Get intesection of all context fields found in data files
            if not context[0]:
                context = (set(current_context[0]), current_context[1])
            else:
                context = (set(context[0]).intersection(set(current_context[0])),
                           current_context[1])

            if sub_bench and current_sub_bench != sub_bench:
                print('Different sub benchs found: {} and {}. Cannot compare results.'
                      .format(current_sub_bench, sub_bench))
                return []
            else:
                sub_bench = current_sub_bench

        if not pandas_list:
            print('No ubench results data found in given'
                  ' directories or not well-formated data')  # pylint: disable=superfluous-parens
            return []

        if all(panda.empty for panda in pandas_list):
            return []  # pylint: disable=superfluous-parens

        # List sub_benchs
        if not sub_bench:
            sub_bench_list = [None]
            context = (list(context[0]), context[1])
        else:
            context = (list(context[0]) + [sub_bench], context[1])
            sub_bench_list = pandas_list[0][sub_bench].unique().tolist()

        # Do a comparison for each sub_bench
        pandas_result_list = []
        for s_bench in sub_bench_list:
            pandas_list_sub = []
            if s_bench:
                for df in pandas_list:  # pylint: disable=invalid-name
                    pandas_list_sub.append(df[df[sub_bench] == s_bench])
            else:
                pandas_list_sub = pandas_list

            pandas_result_list.append(self.compare_pandas(pandas_list_sub, context, session_list))

        return pandas_result_list
