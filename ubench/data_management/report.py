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
import os
import yaml
import jinja2
import ubench.data_management.data_store_yaml as dsy
import ubench.data_management.comparison_writer as comparison_writer


def _dic_to_tuple(one_el_dictionnary):
    """
    Translate a single element dictionnary to a two element tuple key, value
    """
    return list(one_el_dictionnary.items())[0]


def _get_default_dic(main_dic):
    """
    Get sub dictionnary corresponding to 'default' key
    """
    for dic_el in main_dic:
        key, sub_dic = _dic_to_tuple(dic_el)
        if key == 'default':
            return sub_dic
    return {}

class Report:
    """
    Performance report class.
    """
    def __init__(self, metadata_file, bench_template, \
                 compare_template, report_template):
        """
        Report constructor.
        """
        self.bench_template = bench_template
        self.compare_template = compare_template
        self.report_template = report_template
        self.required_fields = set(['tester', 'platform', 'date_start',
                                    'date_end', 'dir', 'comment',
                                    'result'])
        self.context_fields = set(['row_headers','column_headers','compare_array','compare_graph','compare_comment'])
        self.metadata = {}
        self.initialize(metadata_file)

        return

    def initialize(self, metadata_file=None):
        """
        Initialize empty report with header and conclusion and read
        report metadata from metadata_file.
        """
        self.report_dictionnary = {}
        self.report_dictionnary['compare_comment'] = {}
        self.report_files = {}
        self.report_files['compare'] = {}

        self.date_interval_list = []
        self.session_list = []
        self.directory_list = []
        if metadata_file:
            self.read_metadata(metadata_file)

        self.set_common_fields(set(['author', 'title', 'version',
                                    'introduction', 'conclusion']))


    def read_metadata(self, metadata_file):
        """
        Read report metadata file. Those data drive the reporting.
        """
        with open(metadata_file, 'r') as mfile:
            try:
                self.metadata = yaml.load(mfile)
            except Exception as e:
                print("Cannot load metadata file:"+str(e))

    @staticmethod
    def _read_date(date_str):
        """
        Read date from string.
        Tue May 15 17:15:08 2018
        """
        try:
            date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError as verr:
            print("Wrong date format : {} : {}".format(date_str, str(verr)))
            return None

        return date_time


    def set_common_fields(self, field_names):
        """
        Set common fields fields_names with values found
        in metadata dictionnary. these fields are common
        to all benchmarks and sessions.
        """
        for sec_key in field_names:
            if not sec_key in self.metadata:
                print('Warning: {} field is missing'.format(sec_key))
                self.report_dictionnary[sec_key] = ''
            else:
                self.report_dictionnary[sec_key] = self.metadata[sec_key]

        self.report_dictionnary['sessions'] = []
        self.report_dictionnary['benchmarks'] = []

    def set_fields_from_sessions(self,
                                 session_name,
                                 session_data,
                                 benchmark_name,
                                 benchmark_data,
                                 current_benchmark_report,
                                 fields_to_find,
                                 default_fields):
        """
        Given a current_benchmark_report, extend it with fields fields_to_find found
        in benchmark and session sections.
        """
        if not session_name in self.report_dictionnary['sessions']:
            self.report_dictionnary['sessions'].append(session_name)

        fields_found = []
        extended_report = current_benchmark_report.copy()

        # Get fields from benchmarks section
        for r_field in fields_to_find:
            if not benchmark_data[session_name]:
                benchmark_data[session_name] = {}
            if r_field in benchmark_data[session_name]:
                extended_report[r_field] = benchmark_data[session_name][r_field]
                fields_found.append(r_field)
            elif r_field in default_fields['benchmarks']:
                extended_report[r_field] = default_fields['benchmarks'][r_field]
                fields_found.append(r_field)

        # Fields not found are set from session sections
        for r_field in fields_found:
            fields_to_find.remove(r_field)

        for r_field in fields_to_find:
            if r_field in session_data:
                extended_report[r_field] = session_data[r_field]
            elif r_field in default_fields['sessions']:
                extended_report[r_field] = default_fields['sessions'][r_field]
            else:
                print(("Please precise {} for benchmark {}".
                       format(r_field, benchmark_name)))
                exit

        return extended_report


    def set_fields_from_contexts_section(self,
                                         benchmark_name,
                                         fields_to_find,
                                         default_fields):
        """
        """
        # Dictionnary that will contain fields retrieved from context sections
        # This will be extended by benchmarks and session sections
        report_from_contexts = {}
        report_from_contexts['benchmark_name'] = benchmark_name

        # Set default values for some common fields
        report_from_contexts['compare_threshold'] = 0.0
        report_from_contexts['compare_array'] = False
        report_from_contexts['compare_graph'] = True
        report_from_contexts['compare_comment'] = ''
        report_from_contexts['results_filter'] = []


        dic_contexts = {}
        for ctx_el in self.metadata['contexts']:
            ctx_bench_name, ctx_dic = _dic_to_tuple(ctx_el)
            if ctx_bench_name == benchmark_name:
                dic_contexts = ctx_dic

        # Get fields from contexts section (same for all sessions)
        for r_field in self.context_fields.intersection(fields_to_find):
            if r_field in dic_contexts:
                report_from_contexts[r_field] = dic_contexts[r_field]
            elif r_field in default_fields['contexts']:
                report_from_contexts[r_field] = default_fields['contexts'][r_field]
            else:
                print(("Please precise {} for benchmark {}".format(r_field, benchmark_name)))
                exit
        for r_field in self.context_fields:
            fields_to_find.remove(r_field)

        return report_from_contexts, fields_to_find

    def add_session_to_report(self,
                              benchmark_name,
                              session_name,
                              session_report,
                              row_headers,
                              column_headers,
                              output_dir):
        """
        Add to report a benchmark session.

        Args:
            benchmark_name: name of the benchmark
            session_name: name of the session
            session_report: dictionnary from which the report section
                            concerning benchmark_name and session_name
                            will be built.
            row_headers: labels used to identify rows in report
            column_headers: label used to to identify columns in report
            output_dir: report output directory

        Returns:
            TODO
        """
        self.session_list.append(session_name)

        dstore = dsy.DataStoreYAML()
        date_interval = (Report._read_date(session_report['date_start']),
                         Report._read_date(session_report['date_end']))
        self.date_interval_list.append(date_interval)
        self.directory_list.append(session_report['dir'])

        context_out = None
        run_metadata, bench_dataframe, context_out, sub_bench \
            = dstore.dir_to_pandas(session_report['dir'], benchmark_name, \
                                   date_interval, (row_headers, column_headers))

        if bench_dataframe.empty:
            print(("Error : no value found for session {} and benchmark {}".\
                   format(session_name, benchmark_name)))
            exit

        perf_array_list, sub_bench_list \
            = self._get_perf_array(bench_dataframe, context_out, sub_bench)

        if sub_bench_list[0] == None:
            sub_bench_list[0] = benchmark_name

        # Complete benchmark informations
        if "cmdline" in run_metadata:
            session_report['cmdline'] = list(set(run_metadata['cmdline']))
        else:
            session_report['cmdline'] = ["N/A"]
        session_report['perf_array_list'] = list(zip(perf_array_list, sub_bench_list))
        session_report['sub_bench_list'] = sub_bench_list
        session_report['ncols'] = len(perf_array_list[-1][-1])

        # Write current benchmark report using a template
        out_filename = benchmark_name+"_"+session_name+".asc"

        if not session_name in self.report_files:
            self.report_files[session_name] = {}

        self.report_files[session_name][benchmark_name] = out_filename
        self.jinja_templated_write(session_report, self.bench_template,
                                   os.path.join(output_dir, out_filename))

        return sub_bench, sub_bench_list, context_out


    def write(self, output_dir, report_name):
        """
        Write a report in output file according to report metadata.

        output_dir: directory where report files will be saved
        report_name: name of the report
        """

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError:
                print(("Error: cannot mkdir {}".format(output_dir)))
                return

        # Initialize Report
        self.initialize()

        # Get default parameters dictionnaries
        default_fields = self.get_default_fields(['sessions',
                                                  'contexts',
                                                  'benchmarks'])

        # Write a section for each benchmark/session
        for benchmark_item in self.metadata['benchmarks']:
            benchmark_name, benchmark_data = _dic_to_tuple(benchmark_item)

            if benchmark_name == 'default':
                continue

            self.report_dictionnary['benchmarks'].append(benchmark_name)
            fields_to_find = self.required_fields.union(self.context_fields)

            # For each benchmark look for report fields in context, sessions
            # and benchmark sections
            common_report_data, fields_not_found = \
                self.set_fields_from_contexts_section(
                    benchmark_name,
                    fields_to_find,
                    default_fields)

            # For each session add corresponding report information
            # according to parameters retrieved from metadata
            for session_item in self.metadata['sessions']:
                fields_to_find_in_sessions = fields_not_found.copy()
                session_name, session_data = _dic_to_tuple(session_item)

                if session_name != 'default':
                    session_report \
                        = self.set_fields_from_sessions(session_name,
                                                        session_data,
                                                        benchmark_name,
                                                        benchmark_data,
                                                        common_report_data,
                                                        fields_to_find_in_sessions,
                                                        default_fields)
                    sub_bench, sub_bench_list, context =\
                        self.add_session_to_report(benchmark_name,
                                                   session_name,
                                                   session_report,
                                                   common_report_data['row_headers'],
                                                   common_report_data['column_headers'],
                                                   output_dir)

            # Write performance comparison across sessions

            compare_file = \
                self.write_comparison(benchmark_name,
                                      sub_bench,
                                      sub_bench_list,
                                      context,
                                      common_report_data['compare_threshold'],
                                      common_report_data['compare_array'],
                                      common_report_data['compare_graph'],
                                      output_dir)

            self.report_dictionnary['compare_comment'][benchmark_name] =\
                common_report_data['compare_comment']

            if compare_file:
                self.report_files['compare'][benchmark_name] = compare_file

        # Write full report
        self.report_dictionnary['report_files'] = self.report_files

        self.jinja_templated_write(self.report_dictionnary, self.report_template, \
                                   os.path.join(output_dir, report_name+".asc"))



    def write_comparison(self,
                         benchmark_name,
                         sub_bench,
                         sub_bench_list,
                         context,
                         compare_threshold,
                         compare_array,
                         compare_graph,
                         output_dir):
        """
        Write performance comparison report section
        """
        dic_compare = {}
        cwriter = comparison_writer.ComparisonWriter(compare_threshold)
        c_list = cwriter.compare(benchmark_name, self.directory_list, \
                                 self.date_interval_list, (context[0]+[context[1]], None),
                                 self.session_list)
        if(compare_array):
            dic_compare['dataframe_list'] = list(zip(c_list, sub_bench_list))
            dic_compare['ncols'] = len(c_list[-1].columns)

        dic_compare['figure_list'] = []
        if(compare_graph):
            # Plot a comparison graph
            cwriter.write_cplot(c_list, sub_bench, sub_bench_list,
                                context, os.path.join(output_dir, benchmark_name+'.png'))
            dic_compare['figure_list'].append(benchmark_name+'.png')

        out_filename = benchmark_name+"_comparison.asc"

        self.jinja_templated_write(dic_compare, self.compare_template, \
                                   os.path.join(output_dir, out_filename))
        return out_filename

    def get_default_fields(self, parameter_list):
        """
        Get default dictionnaries for given metadata sections
        """
        default_fields = {}
        for key_p in parameter_list:
            default_fields[key_p] = _get_default_dic(self.metadata[key_p])

        return default_fields


    def jinja_templated_write(self, report_dic, template_file, out_filename):

        template_loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(template_file))
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(os.path.basename(template_file))
        output_text = template.render(report_dic)
        with open(out_filename, "wb") as report_file:
            report_file.write(output_text.encode('utf-8'))
        return

    def _set_array_content(self, dataframe, columns, context_list, array_line, perf_array):
        """
        Recursive results array printing
        """
        # When there is only one context left, line can be added to the result array.
        if len(context_list) == 1:
            empty_line = True # If evry result found is empty do not append current_line.
            for col in columns:
                if col in sorted(dataframe[context_list[-1]].unique()):
                    result = dataframe[dataframe[context_list[-1]] == col].result.tolist()
                    if len(result) == 1:
                        array_line.append(result[0])
                        if result[0]:
                            empty_line = False
                    else:
                        res_list = []
                        for res in result:
                            if res:
                                empty_line = False
                            res_list.append(res)
                        array_line.append(res_list)
                else:
                    array_line.append("N/A")
            if not empty_line:
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
                                    [], perf_array_list[-1])


        return perf_array_list, sub_bench_list
