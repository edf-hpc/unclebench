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
            sys.path.append(plugin_dir+'/'+benchmark_name)

            plugin_files=[fi for fi in os.listdir(plugin_dir+'/'+benchmark_name) if (fi.endswith(".py")) and ('manager' in fi)]

            if plugin_files:
              for benchmark_manager_file in plugin_files:
                benchmark_manager_name=os.path.splitext(benchmark_manager_file)[0]
                try :
                  current_module= __import__ (benchmark_manager_name)
                  benchmark_manager_class = getattr(current_module,'LocalBenchmarkManager')
                  self.benchmark_manager_list.append(benchmark_manager_class(benchmark_name,platform))

                except Exception as e:
                  print 'A plugin dir exists for '+benchmark_name+' but ubench cannot import LocalBenchmarkManager class definition'
                  print str(e)
            else:
              raise RuntimeError('A plugin dir exists but the file '+benchmark_name+'_benchmark_manager.py cannot be found')
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

        print ''

        return doc_filename
