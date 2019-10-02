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
import os
import numpy as np
import pandas
import ubench.data_management.data_store_yaml as dsy

class ComparisonWriter:

    def __init__(self, threshold=None):
        """ Constructor """
        self.dstore = dsy.DataStoreYAML()
        self.threshold = threshold

    def print_comparison(self, benchmark_name, input_directories, context=(None,None)):
        """
        Print arrays comparating results found in different input directories
        """
        df_to_print = self.compare(benchmark_name, input_directories, context)

        for dframe in df_to_print:
            print("")
            with pandas.option_context('display.max_rows', None, 'display.max_columns', \
                                      None,'expand_frame_repr', False):
                print((dframe.to_string(index=False)))

    def compare_pandas(self, pandas_list, context, session_list=None):
        """
        Return a panda dataframe comparing multiple pandas with there result relative
        differences computed and added as a column.
        """
        panda_ref = pandas_list[0]
        # Check context
        for key_f in context[0]:
            if key_f not in panda_ref:
                print(('    '+str(key_f)+\
                      ' is not a valid context field, valid context fields for given directories are:'))
                for cfield in panda_ref:
                    print(('     - '+str(cfield)))
                    return "No result"

        result_columns_pre_merge = [ x for x in list(panda_ref.columns.values) if x not in context[0]]

        # Do all but last merges keeping the original result field name unchanged
        idx = 0
        pd_compare = panda_ref
        for pdr in pandas_list[1:-1]:
            pd_compare = pandas.merge(pd_compare, pdr, on=context[0], \
                                      suffixes=['', '_post_'+str(idx)])
            idx += 1


        # At last merge add a _pre suffix to reference result
        if len(pandas_list)>1:
            pd_compare = pandas.merge(pd_compare, pandas_list[-1], \
                                      on=context[0], suffixes=['_pre', '_post_'+str(idx)])
        else:
            pd_compare = panda_ref


        pd_compare_columns_list = list(pd_compare.columns.values)
        result_columns = [ x for x in pd_compare_columns_list if x not in context[0]]
        ctxt_columns_list = context[0]

        if "nodes" in ctxt_columns_list:
            ctxt_columns_list.insert(0, ctxt_columns_list.pop(ctxt_columns_list.index("nodes")))

        pd_compare = pd_compare[ctxt_columns_list+result_columns]

        pandas.options.mode.chained_assignment = None # avoid useless warning

        # Convert numeric columns to int or float
        for ccolumn in context[0]:
            try:
                pd_compare[ccolumn] = pd_compare[ccolumn].apply(lambda x: int(x))
            except:
                try:
                    pd_compare[ccolumn] = pd_compare[ccolumn].apply(lambda x: float(x))
                except:
                    continue

        # Add difference columns in % for numeric result columns
        diff_columns = []

        for rcolumn in result_columns_pre_merge:
            pre_column = rcolumn+'_pre'
            if session_list:
                pd_compare.rename(columns = {pre_column:session_list[0]}, inplace = True)
                pre_column = session_list[0]
            for i in range(0,len(pandas_list[1:])):
                post_column = rcolumn+'_post_'+str(i)
                if session_list:
                    pd_compare.rename(columns = {post_column:session_list[i+1]}, inplace = True)
                    post_column = session_list[i+1]
                try:
                    if session_list:
                        diff_column_name = session_list[i+1]+' vs '+session_list[0] + '(%)'
                    else:
                        diff_column_name = rcolumn+'_diff_'+str(i)+'(%)'

                    ref_col = pd_compare[pre_column].apply(ComparisonWriter._try_convert(np.nan,float))
                    post_col = pd_compare[post_column].apply(ComparisonWriter._try_convert(np.nan,float))
                    pd_compare[diff_column_name] = (post_col - ref_col)*100 / ref_col
                    pd_compare[diff_column_name] = pd_compare[diff_column_name].round(2)
                except Exception as Exc:
                    continue
                else:
                    diff_columns.append(diff_column_name)

        # Remove rows with no difference above given threshold
        if self.threshold:
            # Add a column with max :
            pd_compare['max_diff'] = pd_compare[diff_columns].max(axis=1).abs()
            # Use it as a filter :
            pd_compare = pd_compare[ pd_compare.max_diff > float(self.threshold)]
            pd_compare.drop('max_diff', 1,inplace=True)


        pandas.options.mode.chained_assignment = 'warn' #reactivate warning
        return(pd_compare.sort_values(by=ctxt_columns_list))

    @staticmethod
    def _try_convert(default,*types):
        def convert(value):
            for t in types:
                try:
                    return t(value)
                except ValueError as TypeError:
                    continue
            return default
        return convert


    def compare(self, benchmark_name, input_directories, date_interval_list=None, \
                context_in=(None,None), session_list = None):
        """
        Compare results of each input directory/date_interval combination,
        results from first combination are considered as the reference.
        :param input_directories: list of directories.
        :type input_directories: list of str
        :param benchmark_name: name of the benchmark
        :type input_directories: list of str
        :param date_interval_list: list of date intervals.
        :type data_interval_list: list of datetimes tuples.
        :type context: list of tuples of the following form ([ctx0_0,ctx0_1,..],ctx1)
        with ctx of str type.
        """
        pandas_list = []
        context = (None,None)
        sub_bench = None
        metadata = {}
        config_list = []

        if date_interval_list:
            for rdir, d_interval in zip(input_directories, date_interval_list):
                config_list.append((rdir, d_interval))
        else:
            for rdir in input_directories:
                config_list.append((rdir, (None,None)))

        for input_dir, date_interval in config_list:

            metadata, current_panda, current_context, current_sub_bench\
                = self.dstore._dir_to_pandas(input_dir, benchmark_name, \
                                             date_interval, context=context_in)
            if current_panda.empty:
                continue

            pandas_list.append(current_panda)

            # Get intesection of all context fields found in data files
            if not context[0]:
                context = (set(current_context[0]), current_context[1])
            else:
                context = (set(context[0]).intersection(set(current_context[0])), current_context[1])

            if sub_bench and current_sub_bench!=sub_bench:
                return("Different sub benchs found: {} and {}. Cannot compare results.")\
                    .format(current_sub_bench,sub_bench)
            else:
                sub_bench = current_sub_bench

        if not pandas_list:
            return("No ubench results data found in given directories or not well-formated data")

        if all(panda.empty for panda in pandas_list):
            return("")

        # List sub_benchs
        if not sub_bench:
            sub_bench_list = [None]
            context = (list(context[0]), context[1])
        else:
            context = (list(context[0])+[sub_bench], context[1])
            sub_bench_list = pandas_list[0][sub_bench].unique().tolist()

        # Do a comparison for each sub_bench
        pandas_result_list = []
        for s_bench in sub_bench_list:
            pandas_list_sub = []
            if(s_bench):
                for df in pandas_list:
                    pandas_list_sub.append(df[df[sub_bench]==s_bench])
            else:
                pandas_list_sub = pandas_list

            pandas_result_list.append(self.compare_pandas(pandas_list_sub,context,session_list))

        return pandas_result_list
