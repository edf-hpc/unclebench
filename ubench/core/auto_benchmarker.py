#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright (C) 2015 EDF SA                                                 #
#                                                                            #
#  This file is part of UncleBench                                           #
#                                                                            #
#  This software is governed by the CeCILL license under French law and      #
#  abiding by the rules of distribution of free software. You can use,       #
#  modify and/ or redistribute the software under the terms of the CeCILL    #
#  license as circulated by CEA, CNRS and INRIA at the following URL         #
#  "http://www.cecill.info".                                                 #
#                                                                            #
#  As a counterpart to the access to the source code and rights to copy,     #
#  modify and redistribute granted by the license, users are provided only   #
#  with a limited warranty and the software's author, the holder of the      #
#  economic rights, and the successive licensors have only limited           #
#  liability.                                                                #
#                                                                            #
#  In this respect, the user's attention is drawn to the risks associated    #
#  with loading, using, modifying and/or developing or reproducing the       #
#  software by the user in light of its specific status of free software,    #
#  that may mean that it is complicated to manipulate, and that also         #
#  therefore means that it is reserved for developers and experienced        #
#  professionals having in-depth computer knowledge. Users are therefore     #
#  encouraged to load and test the software's suitability as regards their   #
#  requirements in conditions enabling the security of their systems and/or  #
#  data to be ensured and, more generally, to use and operate it in the      #
#  same conditions as regards security.                                      #
#                                                                            #
#  The fact that you are presently reading this means that you have had      #
#  knowledge of the CeCILL license and that you accept its terms.            #
#                                                                            #
##############################################################################
import sys
import os
import traceback
import re
import pdb

import ubench.benchmark_managers.benchmark_manager as bm
from subprocess import call, Popen, PIPE
from shutil import copy,copytree,move,ignore_patterns

class AutoBenchmarker:

    def __init__(self,platform_name):
        """ Constructor.
        platform_name -- name of the platform, needed when autobenchmarker run benchmarks.
        """
        self.benchmark_manager_list=[]
        self.platform=platform_name


    def init_run_dir(self,benchmark_dir,run_dir,benchmark_list):
        """ Copy benchmarks tests cases to a directory where they should be run.
        benchmark_dir  -- Directory from where the benchmarks files should be copied.
        run_dir        -- Directory where the benchmarks files will be copied.
        benchmark_list -- List of benchmarks to copy.
        """
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)

        for bench_dir in benchmark_list:
            src_dir=os.path.join(benchmark_dir,bench_dir)
            dest_dir=os.path.join(run_dir,bench_dir)
            try:
                copytree(src_dir,dest_dir,symlinks=True)
            except OSError:
                print '---- '+bench_dir+' description files are already present in run directory and will be overwritten.'
            else:
                print '---- Copying '+benchmark_dir+'/'+bench_dir+' to '+run_dir+'/'+bench_dir

            for f in os.listdir(src_dir):
                copy(os.path.join(src_dir,f),dest_dir)


    def add_benchmark_managers_from_path(self,plugin_dir,benchmark_list,platform):
        """ Add benchmark manager for each benchmark in benchmark_list. If a plugin is available
        use the class it defines instead of a standard benchmark manager """

        for benchmark_name in benchmark_list:
            if benchmark_name in os.listdir(plugin_dir):
                plugin_files=os.listdir(plugin_dir+'/'+benchmark_name)
                pdb
                sys.path.append(plugin_dir+'/'+benchmark_name)
                for benchmark_manager_file in [fi for fi in plugin_files if (fi.endswith(".py")) and ('manager' in fi)]:
                    benchmark_manager_name=os.path.splitext(benchmark_manager_file)[0]
                    try :
                        current_module= __import__ (benchmark_manager_name)
                        benchmark_manager_class = getattr(current_module,'LocalBenchmarkManager')
                        self.benchmark_manager_list.append(benchmark_manager_class(benchmark_name,platform))

                    except Exception as e:
                        print 'A plugin dir exists for '+benchmark_name+' but ubench cannot import LocalBenchmarkManager class definition'
                        print str(e)
            else:
                self.benchmark_manager_list.append(bm.BenchmarkManager(benchmark_name,platform))

    def run_benchmark(self,benchmark_name):
        """ Run a benchmark from its name """
        for bm in self.benchmark_manager_list:
            if bm.benchmark_name==benchmark_name:
                benchmark_manager=bm
                break
        bm.run_benchmark(self.platform)

    def get_benchmark_manager(self,benchmark_name):
        for bm in self.benchmark_manager_list:
            if bm.benchmark_name==benchmark_name:
                return bm
        return None

    def write_report(self,global_report_path,benchmark_name,template_env):
        """ Write an asciidoc file with performance of the last execution of benchmark benchmark_name and return its path """
        doc_filename=None
        for bm in self.benchmark_manager_list:
            if bm.benchmark_name==benchmark_name:
                benchmark_manager=bm
                break

        print 'Processing '+benchmark_name+' benchmark :'

        # Analyse raw results from benchmark
        try:
            print '----analysing results'
            benchmark_manager.analyse_last_benchmark()
        except IOError:
            print '----no benchmark run found'
            return

        # Get formated results and build associated documentation

        try:
            print '----extracting analysis'
            benchmark_manager.extract_result_from_last_benchmark()
        except IOError:
            print '----no result analyzer found, only raw results will be copied to the report directory'
        else:
            print '----building asciidoc file'
            doc_filename=benchmark_name+'_doc.txt'
            try:
              benchmark_manager.build_doc(os.path.join(global_report_path,doc_filename),template_env)
            except Exception as e:
                 print '----Error while trying to build report :'
                 for frame in traceback.extract_tb(sys.exc_info()[2]):
                     fname,lineno,fn,text = frame
                     print '    Error in %s on line %d' % (fname, lineno)
                 print '      '+str(e)

                 return

            #global_report_file.write('include::'+doc_filename+'[]\n')

        # Copy images to global report directory

        doc_files=os.listdir(benchmark_manager.benchmark_path)
        try:
            for image_file in [fi for fi in doc_files if (fi.endswith(".png"))]:
                move(image_file,global_report_path)
                print '----image '+image_file+' found'
        except IOError:
            print '----no image found'

        # Copy raw results in global report directory
        # dest_path=os.path.join(global_report_path,'raw_results_'+benchmark_name)

        # copytree(bm.benchmark_results_path,dest_path,\
        #         symlinks=True,ignore=ignore_patterns("*compile"))

        print ''

        return doc_filename
