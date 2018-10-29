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
Define UbenchCmd class
"""
import os
import re
from subprocess import Popen
import ubench.core.ubench_config as uconfig
import ubench.benchmark_managers.benchmark_manager_set as bms

try:
    import ubench.scheduler_interfaces.slurm_interface as slurmi
except ImportError:
    pass

import ubench.benchmarking_tools_interfaces.jube_xml_parser as jube_xml_parser
import ubench.core.fetcher as fetcher
import ubench.data_management.comparison_writer as comparison_writer
import ubench.data_management.report_writer as report_writer
import pandas as pd


class UbenchCmd:
    """
    Class defining methods corresponding to unclebench commands
    """
    def __init__(self, platform, benchmark_list=None):
        """
        TOCOMMENT
        """
        self.uconf = uconfig.UbenchConfig()
        self.run_dir = os.path.join(self.uconf.run_dir, platform)
        self.platform = platform

        # Add benchmark managers for each benchmark in directory
        self.benchmark_list = benchmark_list
        self.bm_set = bms.BenchmarkManagerSet(benchmark_list, platform, self.uconf)


    def log(self, id_list=None):
        """ TOCOMMENT"""
        if not id_list:
            id_list = [-1]
        for idb in id_list:
            self.bm_set.print_log(int(idb))


    def list_parameters(self, default_values=False):
        """ TOCOMMENT"""
        self.bm_set.list_parameters(default_values)


    def result(self, id_list,debug_mode):
        """ TOCOMMENT """
        if not id_list:
            id_list = ['last']

        for idb in id_list:
            if idb == '-1':
                idb = 'last'
            self.bm_set.analyse(idb)
            self.bm_set.extract_results(idb)
            self.bm_set.print_result_array(debug_mode)

    def listb(self):
        """ Lists runs information"""
        self.bm_set.list_runs()

    def run(self, w_list=None, customp_list=None, raw_cli=None):
        """ TOCOMMENT """
        if w_list:
            try:
                w_list = self.translate_wlist_to_scheduler_wlist(w_list)
            except Exception as exc:
                print '---- Custom node configuration is not valid : {0}'.format(str(exc))
                return
        print ''
        print '-- Ubench platform name set to : {0}'.format(self.platform)

        if not os.path.isdir(self.uconf.resource_dir):
            print '---- The resource directory {0} does not exist.'.format(self.uconf.resource_dir)+\
                'Please run ubench fetch to retrieve sources and test cases.'
            return

        # Set custom parameters
        dict_options = {}
        for elem in customp_list:
            try:
                splitted_param = re.split(':', elem, 1)
                dict_options[splitted_param[0]] = splitted_param[1]
            except Exception as exc:
                print '---- {0} is not formated correctly'.format(elem)+\
                    ', please consider using : -c param:new_value'
        self.bm_set.set_parameter(dict_options)

        # Run each benchmarks
        self.bm_set.run(self.platform, w_list, raw_cli)


    def fetch(self):
        """ TOCOMMENT """
        for benchmark_name in self.benchmark_list:
            benchmark_dir = os.path.join(self.uconf.benchmark_dir, benchmark_name)
            benchmark_files = [file_b for  file_b in os.listdir(benchmark_dir) \
                               if file_b.endswith(".xml")]
            jube_xml_files = jube_xml_parser.JubeXMLParser(benchmark_dir, benchmark_files)
            multisource = jube_xml_files.get_bench_multisource()

            if multisource is None:
                print "ERROR !! : Multisource information for benchmark not found"
                return None

            fetch_bench = fetcher.Fetcher(resource_dir=self.uconf.resource_dir,\
                                          benchmark_name=benchmark_name)
            for source in multisource:

                if not source.has_key('do_cmds'):
                    source['do_cmds'] = None

                if source['protocol'] == 'https':
                    fetch_bench.https(source['url'], source['files'])
                elif source['protocol'] == 'svn' or source['protocol'] == 'git':
                    if not source.has_key('revision'):
                        source['revision'] = None
                    if not source.has_key('branch'):
                        source['branch'] = None

                    fetch_bench.scm_fetch(source['url'], source['files'], \
                                          source['protocol'], source['revision'], \
                                          source['branch'], source['do_cmds'])
                elif source['protocol'] == 'local':
                    fetch_bench.local(source['files'], source['do_cmds'])


    def compare(self, input_directories, benchmark_name , context=(None,None), \
                threshold=None):
        """
        Compare bencharks results from different directories.
        """
        cwriter = comparison_writer.ComparisonWriter(threshold)
        print "    comparing :"
        for rdir in input_directories:
            print "    - "+rdir
        print ""
        cwriter.print_comparison(benchmark_name, input_directories, context)


    def report(self, metadata_file, output_dir):
        """
        Build a performance report.
        """
        bench_template = os.path.join(self.uconf.templates_path, "bench.html")
        compare_template =  os.path.join(self.uconf.templates_path, "compare.html")
        report_template =  os.path.join(self.uconf.templates_path, "report.html")
        rwriter = report_writer.ReportWriter(metadata_file, bench_template,
                                             compare_template, report_template)
        report_name = "ubench_performance_report"

        print("    Writing report {} in {} directory".format(report_name+".html", output_dir))
        rwriter.write_report(output_dir, report_name)

        asciidoctor_cmd\
            = 'asciidoctor -a stylesheet=' + self.uconf.stylesheet_path + " "\
            + os.path.join(os.getcwd(),output_dir,report_name+".asc")

        Popen(asciidoctor_cmd, cwd=os.getcwd(), shell=True)


    def translate_wlist_to_scheduler_wlist(self, w_list_arg):
        """
        Translate ubench custom node list format to scheduler custome node list format
        TODO determine scheduler_interface from platform data.
        """
        try:
            scheduler_interface = slurmi.SlurmInterface()
        except:
            print "Warning!! Unable to load slurm module"
            scheduler_interface = None
            return

        w_list = list(w_list_arg)
        for sub_wlist in w_list:
            sub_wlist_temp = list(sub_wlist)
            stride = 0
        for idx, welem in enumerate(sub_wlist_temp):
            # Manage the all keyword that is meant to launch benchmarks on evry idle node
            catch = re.search(r'^all(\d+)$', str(welem))
            idxn = idx+stride
            if catch:
                slice_size = int(catch.group(1))
                available_nodes_list = scheduler_interface.get_available_nodes(slice_size)
                njobs = len(available_nodes_list)
                sub_wlist[idxn:idxn+1] = zip([slice_size]*njobs, available_nodes_list)
                stride += njobs-1
            else:
                # Manage the cn[10,13-17] notation
                catch = re.search(r'^(\D+.*)$', str(welem))
                if catch:
                    nnodes_list = [scheduler_interface.get_nnodes_from_string(catch.group(1))]
                    nodes_list = [catch.group(1)]
                    sub_wlist[idxn:idxn+1] = zip(nnodes_list, nodes_list)
                else:
                    # Manage the 2,4 notation that is needed to launch jobs
                    # without defined node targets.
                    catch = re.search(r'^([\d+,]*)([\d]+)$', str(welem))
                    if catch:
                        nnodes_list = [int(x) for x in re.split(',', str(welem))]
                        sub_wlist[idxn:idxn+1] = zip(nnodes_list, [None]*len(nnodes_list))
                        stride += len(nnodes_list)-1
                    else:
                        # Manage the 2,4,cn[200-205] notation that is used
                        # to get cn[200-201] cn[200-203]
                        catch = re.search(r'^([\d+,]*[\d+]),(.*)$', str(welem))
                        if catch:
                            nnodes_list = [int(x) for x in re.split(',', catch.group(1))]
                            nodes_list = str(catch.group(2))
                            sub_wlist[idxn:idxn+1]\
                                = zip(nnodes_list, \
                                      scheduler_interface.\
                                      get_truncated_nodes_lists(nnodes_list, nodes_list))

                            stride += len(nnodes_list)-1
                        else:
                            raise Exception(str(welem)+'format is not correct')

        # Flatten the w_list
        w_list = [item for sublist in w_list for item in sublist]
        return w_list
