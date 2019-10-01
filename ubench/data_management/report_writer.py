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
import datetime
import jinja2
import os
import pandas
import sys
import time
import yaml
import ubench.data_management.data_store_yaml as dsy
import ubench.data_management.comparison_writer as comparison_writer

class ReportWriter:
    """
    Class providing performance reporting methods
    """
    def __init__(self, metadata_file, bench_template, \
                 compare_template, report_template):
        """
        ReportWriter constructor.
        """
        self.metadata = {}
        self.read_metadata(metadata_file)
        self.bench_template = bench_template
        self.compare_template = compare_template
        self.report_template = report_template
        return

    def read_metadata(self, metadata_file):
        """
        Read report metadata file. Those data drive the reporting.
        """
        with open(metadata_file, 'r') as mfile:
            try:
                self.metadata = yaml.load(mfile)
            except Exception as e:
                print "Cannot load metadata file:"+str(e)

    @staticmethod
    def _read_date(date_str):
        """
        Read date from string.
        Tue May 15 17:15:08 2018
        """
        try:
            date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError as verr:
            printf("Wrong date format : {} : {}".format(date_str,str(verr)))
            return None

        return date_time

    @staticmethod
    def _dic_to_tuple(one_el_dictionnary):
        """
        Translate a single element dictionnary to a two element tuple key, value
        """
        return one_el_dictionnary.items()[0]

    @staticmethod
    def _get_default_dic(main_dic):
        """
        Get sub dictionnary corresponding to 'default' key
        """
        for dic_el in main_dic:
            key, sub_dic = ReportWriter._dic_to_tuple(dic_el)
            if key == 'default':
                return sub_dic
        return {}


    def write_report(self, output_dir, report_name):
        """
        Write a report in output file according to report_writer metadata.
        """
        required_fields = set(['tester','platform','date_start','date_end','dir','comment', \
                               'result'])
        context_fields = set(['compare','compare_threshold','compare_comment','row_headers','column_headers'])
        report_files = {}
        session_list = []

        # Get default parameters dictionnaries
        dic_sessions_default = ReportWriter._get_default_dic(self.metadata['sessions'])
        dic_contexts_default = ReportWriter._get_default_dic(self.metadata['contexts'])
        dic_benchmarks_default = ReportWriter._get_default_dic(self.metadata['benchmarks'])


        # Dictionnary to store main report data
        dic_report_main = {}
        # Required global parameters
        global_parameters = set(['author','title','version','introduction','conclusion'])
        for gp_key in global_parameters:
            if not gp_key:
                print("Warning: {} field is missing",gp_key)
                dic_report_main[gp_key] = ''
            else:
                dic_report_main[gp_key] = self.metadata[gp_key]
        dic_report_main['sessions'] = []
        dic_report_main["benchmarks"] = []

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError:
                print("Error: cannot mkdir {}".format(output_dir))
                return

        # Parse benchmarks
        for bench_item in self.metadata['benchmarks']:

            bench_name, bench_dic = ReportWriter._dic_to_tuple(bench_item)

            if bench_name == 'default':
                continue
            dic_report_main['benchmarks'].append(bench_name)

            common_dic_report_bench = {}
            common_dic_report_bench["benchmark_name"] = bench_name
            fields_to_find = required_fields.union(context_fields)

            dic_contexts = {}
            for ctx_el in self.metadata['contexts']:
                ctx_bench_name, ctx_dic = ReportWriter._dic_to_tuple(ctx_el)
                if ctx_bench_name == bench_name:
                    dic_contexts = ctx_dic

            # Check context parameters ( same for all sessions)
            for r_field in context_fields.intersection(fields_to_find):
                if r_field in dic_contexts:
                    common_dic_report_bench[r_field] = dic_contexts[r_field]
                elif r_field in dic_contexts_default:
                    common_dic_report_bench[r_field] = dic_contexts_default[r_field]
                else:
                    print("Please precise {} for benchmark {}".format(r_field, bench_name))
                    return

            for r_field in context_fields:
                fields_to_find.remove(r_field)

            context_in = (common_dic_report_bench['row_headers'], common_dic_report_bench['column_headers'])
            context_out = None
            date_interval_list = []
            dir_list = []
            # Parse sessions
            for session_item in self.metadata['sessions']:

                local_fields_to_find = fields_to_find.copy()

                session, dic_session = ReportWriter._dic_to_tuple(session_item)

                if session == 'default':
                    continue
                if not session in dic_report_main['sessions']:
                    dic_report_main['sessions'].append(session)
                    session_list.append(session)

                fields_found = []
                dic_report_bench = common_dic_report_bench.copy()

                # Check benchmark parameters
                for r_field in local_fields_to_find:
                    if not bench_dic[session]:
                        bench_dic[session]={}
                    if r_field in bench_dic[session]:
                        dic_report_bench[r_field] = bench_dic[session][r_field]
                        fields_found.append(r_field)
                    elif r_field in dic_benchmarks_default:
                        dic_report_bench[r_field] = dic_benchmarks_default[r_field]
                        fields_found.append(r_field)

                for r_field in fields_found:
                    local_fields_to_find.remove(r_field)

                # Check session parameters
                for r_field in local_fields_to_find:
                    if r_field in dic_session:
                        dic_report_bench[r_field] = dic_session[r_field]
                    elif r_field in dic_sessions_default:
                        dic_report_bench[r_field] = dic_sessions_default[r_field]
                    else:
                        print("Please precise {} for benchmark {}".format(r_field, bench_name))
                        return

                # Get performance array
                dstore = dsy.DataStoreYAML()
                date_interval = (ReportWriter._read_date(dic_report_bench['date_start']),
                                  ReportWriter._read_date(dic_report_bench['date_end']))

                date_interval_list.append(date_interval)
                dir_list.append(dic_report_bench['dir'])

                run_metadata, bench_dataframe, context_out, sub_bench \
                    = dstore._dir_to_pandas(dic_report_bench['dir'], bench_name, \
                                            date_interval, context_in)

                if bench_dataframe.empty:
                    print("Error : no value found for session {} and benchmark {}".\
                          format(session,bench_name))
                    return

                perf_array_list, sub_bench_list \
                    = self._get_perf_array(bench_dataframe, context_out, sub_bench)

                if sub_bench_list[0] == None:
                    sub_bench_list[0] = bench_name

                # Complete benchmark informations
                if "cmdline" in run_metadata:
                    dic_report_bench['cmdline'] = list(set(run_metadata['cmdline']))
                else:
                    dic_report_bench['cmdline'] = ["N/A"]
                dic_report_bench['perf_array_list'] = zip(perf_array_list, sub_bench_list)
                dic_report_bench['sub_bench_list'] = sub_bench_list
                dic_report_bench['ncols'] = len(perf_array_list[-1][-1])

                # Write current benchmark report using a template
                out_filename = bench_name+"_"+session+".asc"

                if not session in report_files:
                    report_files[session] = {}
                report_files[session][bench_name] = out_filename
                self.jinja_templated_write(dic_report_bench, self.bench_template,\
                                           os.path.join(output_dir,out_filename))

            # Write performance comparison across sessions
            if bool(dic_report_bench['compare']):
                if not 'compare' in report_files:
                    report_files['compare'] = {}

                report_files['compare'][bench_name]\
                    = self.write_comparison(output_dir,bench_name, sub_bench, sub_bench_list,
                                            date_interval_list, dir_list,
                                            context_out,dic_report_bench['compare_threshold'],
                                            session_list)

        # Write full report
        dic_report_main['report_files'] = report_files
        self.jinja_templated_write(dic_report_main, self.report_template, \
                                   os.path.join(output_dir,report_name+".asc"))


    def write_comparison(self, output_dir, bench_name, sub_bench, sub_bench_list, \
                         date_interval_list, dir_list, context, threshold, session_list):
        """
        Write performance comparison report section
        """
        dic_compare = {}
        cwriter = comparison_writer.ComparisonWriter(threshold)
        c_list = cwriter.compare(bench_name, dir_list, \
                                 date_interval_list, (context[0]+[context[1]], None),
                                 session_list)
        if(sub_bench):
            for df_comp in c_list:
                df_comp.drop(sub_bench, 1, inplace=True)

        dic_compare['dataframe_list'] = zip(c_list,sub_bench_list)
        dic_compare['ncols'] = len(c_list[-1].columns)
        out_filename = bench_name+"_comparison.asc"

        self.jinja_templated_write(dic_compare, self.compare_template, \
                                   os.path.join(output_dir, out_filename))

        return out_filename


    def jinja_templated_write(self, report_dic, template_file, out_filename):

        templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(template_file))
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(os.path.basename(template_file))
        outputText = template.render(report_dic)
        with open(out_filename, "wb") as report_file:
            report_file.write(outputText.encode('utf-8'))
        return

    def _set_array_content(self, dataframe, columns, context_list, array_line, perf_array):
        """
        Recursive results array printing
        """
        if len(context_list) == 1:
            for col in columns:
                if col in sorted(dataframe[context_list[-1]].unique()):
                    result = dataframe[dataframe[context_list[-1]]==col].result.tolist()
                    if len(result) == 1:
                        array_line.append(result[0])
                    else:
                        res_list = []
                        for res in result:
                            res_list.append(res)
                        array_line.append(res_list)
                else:
                    array_line.append("N/A")
            perf_array.append(array_line)
            return
        try:
            sorted_ctx = sorted(int(x) for x in dataframe[context_list[0]].unique().tolist())
        except ValueError:
            sorted_ctx = sorted(dataframe[context_list[0]].unique().tolist())

        for ctx in sorted_ctx:
            sub_dataframe = dataframe[dataframe[context_list[0]] == str(ctx)]
            array_line_tmp = array_line+[str(ctx)]
            self._set_array_content(sub_dataframe, columns, context_list[1:], \
                                    array_line_tmp, perf_array)


    def _get_perf_array(self, report_df, context, sub_bench_field=None):
        """
        Get a result array from a pand dataframe, a context and an optional
        sub_bench_field.
        """
        if report_df.empty:
            return [], []

        context_col = context[1]

        if not sub_bench_field:
            sub_bench_list = [None]
        else:
            sub_bench_list = report_df[sub_bench_field].unique().tolist()

        units = None #TODO
        perf_array_list = []
        for sub_bench in sub_bench_list:
            perf_array_list.append([])
            sub_bench_df = report_df
            if(sub_bench):
                sub_bench_df = report_df[report_df[sub_bench_field] == sub_bench]

            nb_cols = len(sub_bench_df[context[1]].unique())+len(context[0])

            perf_array_list[-1].append([])
            columns = []

            for ctx_f in context[0]:
                perf_array_list[-1][-1].append(ctx_f)

            for ctx_c_val in sorted(sub_bench_df[context[1]].unique()):
                perf_array_list[-1][-1].append(ctx_c_val)
                columns.append(ctx_c_val)
                if units:
                    perf_array_list[-1][-1][-1] += " ()".format(units)

            self._set_array_content(sub_bench_df, columns, context[0]+[context[1]], \
                                    [],perf_array_list[-1])


        return perf_array_list, sub_bench_list
