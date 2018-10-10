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
import pandas
import ubench.data_management.data_store_yaml as dsy
import yaml
import matplotlib.pyplot as plt

class ReportWriter:

    def __init__(self, metadata_file, result_directory):
        self.result_directory=result_directory
        self.metadata={}
        self.read_metadata(metadata_file)
        return


    def read_metadata(self, metadata_file):
        with open(metadata_file, 'r') as mfile:
            try:
                self.metadata = yaml.load(mfile)
            except Exception as e:
                print "Cannot load metadata file:"+str(e)

    def write_report(self, output_file=None):
        print self.metadata

        dstore = dsy.DataStoreYAML()
#       context = (["nodes","tasks","variant_name"],"mpi_version")
        context = (["nodes","tasks"],"mpi_version")
        benchmark_name = "hpcc"
        panda, context, sub_bench = dstore._dir_to_pandas(self.result_directory, benchmark_name, \
                                                          None,context)

        print(str(panda))
        self._get_perf_array(panda, context, sub_bench)


    def _print_array_content(self, dataframe, context_list, array_line):
        """
        Recursive results array printing
        """
        if len(context_list)==1:
            for val_ctx in sorted(dataframe[context_list[-1]].unique()):
                result=dataframe[dataframe[context_list[-1]]==val_ctx].result.tolist()
                if len(result)==1:
                    array_line += "|{}".format(result[0])
                else:
                    array_line += "|["
                    for res in result:
                        array_line += "{} ".format(res)
                    array_line += "]"
            print(array_line)
            return
        try:
            sorted_ctx = sorted(int(x) for x in dataframe[context_list[0]].unique().tolist())
        except ValueError:
            sorted_ctx = sorted(dataframe[context_list[0]].unique().tolist())

        for ctx in sorted_ctx:
            sub_dataframe = dataframe[dataframe[context_list[0]]==str(ctx)]
            array_line_tmp = array_line + ("|{}").format(str(ctx))
            self._print_array_content(sub_dataframe,context_list[1:], array_line_tmp)


    def _get_perf_array(self, report_df, context, sub_bench_field=None):
        """
        Get a result array from a pand dataframe, a context and an optional
        sub_bench_field.
        """
        if report_df.empty:
            return []

        context_col = context[1]

        if not sub_bench_field:
            sub_bench_list=[None]
        else:
            sub_bench_list=report_df[sub_bench_field].unique().tolist()

        units=None #TODO
        print(sub_bench_list)
        for sub_bench in sub_bench_list:

            sub_bench_df=report_df
            if(sub_bench):
                print(".{0} results".format(sub_bench))
                sub_bench_df=report_df[report_df[sub_bench_field]==sub_bench]

            nb_cols=len(sub_bench_df[context[1]].unique())+len(context[0])

            print("[cols=\"{0}*\", options=\"header\"]".format(nb_cols))
            print("|===")
            field_names=''

            for ctx_f in context[0]:
                field_names+='|{}'.format(ctx_f)

            for ctx_c_val in sorted(sub_bench_df[context[1]].unique()):
                field_names += "|{}".format(ctx_c_val)
                if units:
                    field_names += " ()".format(units)
            print field_names

            self._print_array_content(sub_bench_df, context[0]+[context[1]], "")
            print("|===")

        return
