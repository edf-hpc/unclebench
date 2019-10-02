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
import pwd

# used to read ubench.conf ;
# In Python 3, ConfigParser has been renamed
# to configparser for PEP 8 compliance.
from sys import version_info
if version_info.major == 2:
    import configparser as configparser
else:
    import configparser as configparser

class UbenchConfig:
    
    def __init__(self):
        """
           Reads PATH variables    ╭   ·system environment (highest priority)
           from -<4>- different   ╱│   ·local config file (~/unclebench/.ubench.conf)
           locations and stores   ╲│   ·system config file (/etc/unclebench/.ubench.conf)
           their origin in dict    ╰   ·package defaults (lowest priority)
        """
        # settings_source will store the origin of each setting.
        self.settings_source = dict()
        
        self.var = [('INSTALL_DIR','UBENCH_PLUGIN_DIR'), ('INSTALL_DIR','UBENCH_PLATFORM_DIR'), 
               ('INSTALL_DIR','UBENCH_BENCHMARK_DIR'), ('INSTALL_DIR','UBENCH_CONF_DIR'), 
               ('INSTALL_DIR','UBENCH_CSS_PATH'), ('INSTALL_DIR','UBENCH_TEMPLATES_PATH'),
               ('WORK_DIR','UBENCH_RUN_DIR_BENCH'), ('WORK_DIR','UBENCH_RESOURCE_DIR'), 
               ('WORK_DIR','UBENCH_REPORT_DIR')]
        
        # the order of the following 4 calls define implicitly the settings priority.
        # environment defined settings will have highest priority.
        self.init_default('package')
        self.init_config_sys('system config')
        self.init_config_local('local config')
        self.init_environ('environment')
        self.set_environment_vars()

        
    def init_environ(self, origin):
        """ Init path with ENVIRONMENT settings """
        
        # Install directories
        if os.environ.get('UBENCH_PLUGIN_DIR') is not None:
            self.plugin_dir=os.environ.get('UBENCH_PLUGIN_DIR')
            self.settings_source['UBENCH_PLUGIN_DIR'] = {'origin' : origin, 'val' : self.plugin_dir}
        if os.environ.get('UBENCH_PLATFORM_DIR') is not None:
            self.platform_dir=os.environ.get('UBENCH_PLATFORM_DIR')
            self.settings_source['UBENCH_PLATFORM_DIR'] = {'origin' : origin, 'val' : self.platform_dir}
        if os.environ.get('UBENCH_BENCHMARK_DIR') is not None:
            self.benchmark_dir=os.environ.get('UBENCH_BENCHMARK_DIR')
            self.settings_source['UBENCH_BENCHMARK_DIR'] = {'origin' : origin, 'val' : self.benchmark_dir}
        if os.environ.get('UBENCH_CONF_DIR') is not None:
            self.conf_dir=os.environ.get('UBENCH_CONF_DIR')
            self.settings_source['UBENCH_CONF_DIR'] = {'origin' : origin, 'val' : self.conf_dir}
        if os.environ.get('UBENCH_CSS_PATH') is not None:
            self.stylesheet_path=os.environ.get('UBENCH_CSS_PATH')
            self.settings_source['UBENCH_CSS_PATH'] = {'origin' : origin, 'val' : self.stylesheet_path}
        if os.environ.get('UBENCH_TEMPLATES_PATH') is not None:
            self.templates_path=os.environ.get('UBENCH_TEMPLATES_PATH')
            self.settings_source['UBENCH_TEMPLATES_PATH'] = {'origin' : origin, 'val' : self.templates_path}

        # Working directories
        if os.environ.get('UBENCH_RUN_DIR_BENCH') is not None:
            self.run_dir=os.environ.get('UBENCH_RUN_DIR_BENCH')
            self.settings_source['UBENCH_RUN_DIR_BENCH'] = {'origin' : origin, 'val' : self.run_dir}
        if os.environ.get('UBENCH_RESOURCE_DIR') is not None:
            self.resource_dir=os.environ.get('UBENCH_RESOURCE_DIR')
            self.settings_source['UBENCH_RESOURCE_DIR'] = {'origin' : origin, 'val' : self.resource_dir}
        if os.environ.get('UBENCH_REPORT_DIR') is not None:
            self.report_dir=os.environ.get('UBENCH_REPORT_DIR')
            self.settings_source['UBENCH_REPORT_DIR'] = {'origin' : origin, 'val' : self.report_dir}


    def init_config_local(self, origin):
        """ Init path with LOCAL settings """
        
        config = configparser.ConfigParser()
        f = config.read('' + pwd.getpwuid(os.getuid()).pw_dir + '/.unclebench/ubench.conf')
        if len(f) > 0:
            self.load_config(config, origin)


    def init_config_sys(self, origin):
        """ Init path with SYSTEM settings """
        
        config = configparser.ConfigParser()
        f = config.read('/etc/unclebench/ubench.conf')
        if len(f) > 0:
            self.load_config(config, origin)


    def init_default(self, origin):
        """ Init path with PACKAGE settings """
        
        # Install directories
        self.plugin_dir='/usr/share/unclebench/lib/plugins'
        self.settings_source['UBENCH_PLUGIN_DIR'] = {'origin' : origin, 'val' : self.plugin_dir}
        self.platform_dir='/usr/share/unclebench/platform'
        self.settings_source['UBENCH_PLATFORM_DIR'] = {'origin' : origin, 'val' : self.platform_dir}
        #os.environ['UBENCH_PLATFORM_DIR']=self.platform_dir
        
        self.benchmark_dir='/usr/share/unclebench/benchmarks'
        self.settings_source['UBENCH_BENCHMARK_DIR'] = {'origin' : origin, 'val' : self.benchmark_dir}
        #os.environ['UBENCH_BENCHMARK_DIR']=self.benchmark_dir
        
        self.conf_dir='/etc/unclebench' 
        self.settings_source['UBENCH_CONF_DIR'] = {'origin' : origin, 'val' : self.conf_dir}
        self.stylesheet_path='/usr/share/unclebench/css/asciidoctor-bench-report.css'
        self.settings_source['UBENCH_CSS_PATH'] = {'origin' : origin, 'val' : self.stylesheet_path}
        self.templates_path='/usr/share/unclebench/templates'
        self.settings_source['UBENCH_TEMPLATES_PATH'] = {'origin' : origin, 'val' : self.templates_path}

        # Working directories
        if os.environ.get('SCRATCHDIR') is None:
            self.run_dir=pwd.getpwuid(os.getuid()).pw_dir + '/ubench/benchmarks'
        else:
            self.run_dir=os.environ.get('SCRATCHDIR') + '/ubench/benchmarks'
        self.settings_source['UBENCH_RUN_DIR_BENCH'] = {'origin' : origin, 'val' : self.run_dir}

        if os.environ.get('SCRATCHDIR') is None:
            self.resource_dir=pwd.getpwuid(os.getuid()).pw_dir + '/ubench/resource'
        else:
            self.resource_dir=os.environ.get('SCRATCHDIR') + '/ubench/resource'
        self.settings_source['UBENCH_RESOURCE_DIR'] = {'origin' : origin, 'val' : self.resource_dir}
        #os.environ['UBENCH_RESOURCE_DIR']=self.resource_dir
        
        self.report_dir=self.run_dir+'/reports'
        self.settings_source['UBENCH_REPORT_DIR'] = {'origin' : origin, 'val' : self.report_dir}


        
    def load_config(self, config_parser, origin):
        """ General procedure used to load variables found in ubench.conf
            and to update `settings_source` dictionary accordingly.
            This procedure is used by `init_config_local` and `init_config_sys`. """
        section = 'INSTALL_DIR'
        if config_parser.has_option(section, 'UBENCH_PLUGIN_DIR'):
            self.plugin_dir=config_parser.get(section, 'UBENCH_PLUGIN_DIR')
            self.settings_source['UBENCH_PLUGIN_DIR'] = {'origin' : origin, 'val' : self.plugin_dir}
        if config_parser.has_option(section, 'UBENCH_PLATFORM_DIR'):
            self.platform_dir=config_parser.get(section, 'UBENCH_PLATFORM_DIR')
            self.settings_source['UBENCH_PLATFORM_DIR'] = {'origin' : origin, 'val' : self.platform_dir}
        if config_parser.has_option(section, 'UBENCH_BENCHMARK_DIR'):
            self.benchmark_dir=config_parser.get(section, 'UBENCH_BENCHMARK_DIR')
            self.settings_source['UBENCH_BENCHMARK_DIR'] = {'origin' : origin, 'val' : self.benchmark_dir}
        if config_parser.has_option(section, 'UBENCH_CONF_DIR'):
            self.conf_dir=config_parser.get(section, 'UBENCH_CONF_DIR')
            self.settings_source['UBENCH_CONF_DIR'] = {'origin' : origin, 'val' : self.conf_dir}
        if config_parser.has_option(section, 'UBENCH_CSS_PATH'):
            self.stylesheet_path=config_parser.get(section, 'UBENCH_CSS_PATH')
            self.settings_source['UBENCH_CSS_PATH'] = {'origin' : origin, 'val' : self.stylesheet_path}
        if config_parser.has_option(section, 'UBENCH_TEMPLATES_PATH'):
            self.templates_path=config_parser.get(section, 'UBENCH_TEMPLATES_PATH')
            self.settings_source['UBENCH_TEMPLATES_PATH'] = {'origin' : origin, 'val' : self.templates_path}

        section = 'WORK_DIR'
        if config_parser.has_option(section, 'UBENCH_RUN_DIR_BENCH'):
            self.run_dir = config_parser.get(section, 'UBENCH_RUN_DIR_BENCH')
            self.settings_source['UBENCH_RUN_DIR_BENCH'] = {'origin' : origin, 'val' : self.run_dir}
        if config_parser.has_option(section, 'UBENCH_RESOURCE_DIR'):
            self.resource_dir = config_parser.get(section, 'UBENCH_RESOURCE_DIR')
            self.settings_source['UBENCH_RESOURCE_DIR'] = {'origin' : origin, 'val' : self.resource_dir}
        if config_parser.has_option(section, 'UBENCH_REPORT_DIR'):
            self.report_dir = config_parser.get(section, 'UBENCH_REPORT_DIR')
            self.settings_source['UBENCH_REPORT_DIR'] = {'origin' : origin, 'val' : self.report_dir}

    
    def set_environment_vars(self):
        """ Sets environment variables if         UBENCH_PLATFORM_DIR
            they were not previously set:         UBENCH_BENCHMARK_DIR
                                                  UBENCH_RESOURCE_DIR   
        """
        
        if os.environ.get('UBENCH_PLATFORM_DIR') is None:
            os.environ['UBENCH_PLATFORM_DIR'] = self.settings_source['UBENCH_PLATFORM_DIR']['val']
        
        if os.environ.get('UBENCH_BENCHMARK_DIR') is None:
            os.environ['UBENCH_BENCHMARK_DIR'] = self.settings_source['UBENCH_BENCHMARK_DIR']['val']
        
        if os.environ.get('UBENCH_RESOURCE_DIR') is None:
            os.environ['UBENCH_RESOURCE_DIR'] = self.settings_source['UBENCH_RESOURCE_DIR']['val']


    def print_config(self, pad = 30):
        """ Procedure used to display the origin of the settings loaded 
            and which can be invoked at the command line using `-log` flag """

        max_var = max([len(i) for i in list(self.settings_source.keys())])
        max_origin = max([len(k['origin']) for k in list(self.settings_source.values())])
        max_val = max([len(k['val']) for k in list(self.settings_source.values())])
        pad_var = max_var + 10
        pad_origin = max_origin + 10
        line_length = pad_var + pad_origin + max_val + 3
        
        print(('\n {:<{pad_var}} {:<{pad_origin}} {}'.format('Variable', 'Origin', 'Value', pad_var = pad_var, pad_origin = pad_origin)))
        print(('─'*line_length))
        for i in self.settings_source:
            print((' {:<{pad_var}} {:<{pad_origin}} {}'.format(i, self.settings_source[i]['origin'], self.settings_source[i]['val'], pad_var = pad_var, pad_origin = pad_origin)))
        print(('─'*line_length))
        print('')

        
    def get_platform_list(self):
        """ Get list of available platforms """
        platform_list=[]
        jube_xml = jube_xml_parser.JubeXMLParser("",[],"",self.platform_dir)
        root=jube_xml.load_platforms_xml()
        jube_xml.delete_platform_dir()
        for node in root.getiterator('path'):
            tags=node.get('tag')
            if tags:
                for tag in tags.split(','):
                    platform_list.append(tag)

        platform_list=list(set(platform_list))

        return sorted(platform_list, key=str.lower)


    def find_all_rec(node,node_name,node_name_attr,root):
        for step in node.findall(node_name):
            if(step.get('name')==node_name_attr):
                result.append()

        return result

    def find_rec(self,node, element,name):
        for item in node.findall(element):
            if(item.get('name')=='execute'):
                yield item
            for child in find_rec(item, element,name):
                yield child


    def get_benchmark_list(self):
        """ Get list of available benchmarks """

        bench_list=[f for f in os.listdir(self.benchmark_dir) \
                if os.path.isdir(os.path.join(self.benchmark_dir,f))]
        filtered_bench_list=[]

        # Only benchmarks that define an execute step are considered
        for bench_dir in bench_list:
            execute_step=False
            for filename in os.listdir(os.path.join(self.benchmark_dir,bench_dir)):
              if not filename.endswith('.xml'): continue
              try:
                  tree = ET.parse(os.path.join(self.benchmark_dir,bench_dir,filename))
              except ET.ParseError:
                  continue
                  
              root = tree.getroot()
              if self.find_rec(root,'step','execute'):
                  execute_step=True
                  break
            if(execute_step):
                filtered_bench_list.append(bench_dir.lower())

        return filtered_bench_list
