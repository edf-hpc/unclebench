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
import getpass
import os
import xml.etree.ElementTree as ET

class UbenchConfig:

    def __init__(self):
        """ Constructor """
        # Install directories
        self.plugin_dir=os.environ.get('UBENCH_PLUGIN_DIR')
        self.platform_dir=os.environ.get('UBENCH_PLATFORM_DIR')
        self.benchmark_dir=os.environ.get('UBENCH_BENCHMARK_DIR')
        self.conf_dir=os.environ.get('UBENCH_CONF_DIR')
        self.stylesheet_path=os.environ.get('UBENCH_CSS_PATH')
        self.templates_path=os.environ.get('UBENCH_TEMPLATES_PATH')

        # Working directories
        self.run_dir=os.environ.get('UBENCH_RUN_DIR_BENCH')
        self.resource_dir=os.environ.get('UBENCH_RESOURCE_DIR')
        self.report_dir=os.environ.get('UBENCH_REPORT_DIR')

        self.init_default()

    def init_default(self):
        """ Init path with package settings """
        # Install directories
        if not self.plugin_dir:
            self.plugin_dir='/usr/share/unclebench/lib/plugins'

        if not self.platform_dir:
            self.platform_dir='/usr/share/unclebench/platform'
            os.environ['UBENCH_PLATFORM_DIR']=self.platform_dir

        if not self.conf_dir:
            self.conf_dir='/etc/unclebench/'

        if not self.benchmark_dir:
            self.benchmark_dir='/usr/share/unclebench/benchmarks'

        if not self.stylesheet_path:
            self.stylesheet_path='/usr/share/unclebench/css/asciidoctor-bench-report.css'

        if not self.templates_path:
            self.stylesheet_path='/usr/share/unclebench/templates'
            

        # Working directories
        if not self.run_dir:
            self.run_dir='/scratch/'+getpass.getuser()+'/Ubench/benchmarks'

        if not self.resource_dir:
            self.resource_dir='/scratch/'+getpass.getuser()+'/Ubench/resource'
            os.environ['UBENCH_RESOURCE_DIR']=self.resource_dir

        if not self.report_dir:
            self.report_dir=self.run_dir+'/reports'


    def get_platform_list(self):
        """ Get list of available platforms """
        platform_list=[]
        root=ET.parse(os.path.join(self.platform_dir,'platforms.xml')).getroot()
        for node in root.getiterator('path'):
            tags=node.get('tag')
            if tags:
                for tag in tags.split(','):
                    platform_list.append(tag)

        platform_list=list(set(platform_list))
        
        return sorted(platform_list, key=str.lower) 
            
    def get_benchmark_list(self):
        """ Get list of available benchmarks """
        bench_list=[f for f in os.listdir(self.plugin_dir) \
                if os.path.isdir(os.path.join(self.plugin_dir,f))]
        return [bench.lower() for bench in bench_list]


    
