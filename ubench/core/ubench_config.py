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

import getpass
import os
import xml.etree.ElementTree as ET
import ubench.benchmarking_tools_interfaces.jube_xml_parser as jube_xml_parser

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
            os.environ['UBENCH_BENCHMARK_DIR']=self.benchmark_dir

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
        jube_xml = jube_xml_parser.JubeXMLParser("",[],"",self.platform_dir)
        platform_dir = jube_xml.get_platform_dir()
        root=ET.parse(os.path.join(platform_dir,'platforms.xml')).getroot()
        jube_xml.delete_platform_dir()
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
