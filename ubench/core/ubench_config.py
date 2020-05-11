#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2019 EDF SA                                           #
#                                                                            #
#  UncleBench is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by      #
#  the Free Software Foundation, either version 3 of the License, or         #
#  (at your option) any later version.                                       #
#                                                                            #
#  UncleBench is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU General Public License for more details.                              #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with UncleBench. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                            #
##############################################################################
# pylint: disable=invalid-name, superfluous-parens, attribute-defined-outside-init
""" Defines UbenchConfig class """


import os
import pwd
import xml.etree.ElementTree as ET

# Used to read ubench.conf.
# In Python 3, ConfigParser has been renamed
# to configparser for PEP 8 compliance.

from sys import version_info
if version_info.major == 2:
    import ConfigParser as configparser  # pylint: disable=import-error
else:
    import configparser as configparser  # pylint: disable=import-error

import ubench.benchmarking_tools_interfaces.jube_xml_parser as jube_xml_parser  # pylint: disable=wrong-import-position


class UbenchConfig(object):  # pylint: disable=too-many-instance-attributes
    """ Defines Unclebench directories

    Reads PATH variables    ╭   ·system environment (highest priority)
    from -<4>- different   ╱│   ·local config file (~/unclebench/.ubench.conf)
    locations and stores   ╲│   ·system config file (/etc/unclebench/.ubench.conf)
    their origin in dict    ╰   ·package defaults (lowest priority)

    Attributes:
        print_config:
        get_platform_list:
        get_benchmark_list:
    """

    def __init__(self):
        """ Class constructor """

        # settings_source will store the origin of each setting.
        # this variable can later be used to search for any item
        # in unclebench configuration.
        self.settings_source = dict()

        self.var = [('INSTALL_DIR', 'UBENCH_PLUGIN_DIR'), ('INSTALL_DIR', 'UBENCH_PLATFORM_DIR'),
                    ('INSTALL_DIR', 'UBENCH_BENCHMARK_DIR'), ('INSTALL_DIR', 'UBENCH_CONF_DIR'),
                    ('INSTALL_DIR', 'UBENCH_CSS_PATH'), ('INSTALL_DIR', 'UBENCH_TEMPLATES_PATH'),
                    ('WORK_DIR', 'UBENCH_RUN_DIR_BENCH'), ('WORK_DIR', 'UBENCH_RESOURCE_DIR'),
                    ('WORK_DIR', 'UBENCH_REPORT_DIR'), ('WORK_DIR', 'UBENCH_RESULTS_DIR'),
                    ('PUBLISH', 'UBENCH_PUBLISH_VCS'), ('PUBLISH', 'UBENCH_PUBLISH_REPOSITORY'),
                    ('PUBLISH', 'UBENCH_PUBLISH_PROTOCOL'), ('PUBLISH', 'UBENCH_PUBLISH_SERVER'),
                    ('PUBLISH', 'UBENCH_PUBLISH_PATH')]

        # the order of the following 4 calls define implicitly the settings priority.
        # environment defined settings will have highest priority.
        self.init_default('package')
        self.init_config_sys('system config')
        self.init_config_local('local config')
        self.init_environ('environment')
        self.set_environment_vars()

    def init_environ(self, origin):
        """ Initializes path variables with values found in ENVIRONMENT variables """

        # Install directories
        if os.environ.get('UBENCH_PLUGIN_DIR') is not None:
            self.plugin_dir = os.environ.get('UBENCH_PLUGIN_DIR')
            self.settings_source['UBENCH_PLUGIN_DIR'] = {'origin' : origin,
                                                         'val' : self.plugin_dir}
        if os.environ.get('UBENCH_PLATFORM_DIR') is not None:
            self.platform_dir = os.environ.get('UBENCH_PLATFORM_DIR')
            self.settings_source['UBENCH_PLATFORM_DIR'] = {'origin' : origin,
                                                           'val' : self.platform_dir}
        if os.environ.get('UBENCH_BENCHMARK_DIR') is not None:
            self.benchmark_dir = os.environ.get('UBENCH_BENCHMARK_DIR')
            self.settings_source['UBENCH_BENCHMARK_DIR'] = {'origin' : origin,
                                                            'val' : self.benchmark_dir}
        if os.environ.get('UBENCH_CONF_DIR') is not None:
            self.conf_dir = os.environ.get('UBENCH_CONF_DIR')
            self.settings_source['UBENCH_CONF_DIR'] = {'origin' : origin,
                                                       'val' : self.conf_dir}
        if os.environ.get('UBENCH_CSS_PATH') is not None:
            self.stylesheet_path = os.environ.get('UBENCH_CSS_PATH')
            self.settings_source['UBENCH_CSS_PATH'] = {'origin' : origin,
                                                       'val' : self.stylesheet_path}
        if os.environ.get('UBENCH_TEMPLATES_PATH') is not None:
            self.templates_path = os.environ.get('UBENCH_TEMPLATES_PATH')
            self.settings_source['UBENCH_TEMPLATES_PATH'] = {'origin' : origin,
                                                             'val' : self.templates_path}

        # Working directories
        if os.environ.get('UBENCH_RUN_DIR_BENCH') is not None:
            self.run_dir = os.environ.get('UBENCH_RUN_DIR_BENCH')
            self.settings_source['UBENCH_RUN_DIR_BENCH'] = {'origin' : origin,
                                                            'val' : self.run_dir}
        if os.environ.get('UBENCH_RESOURCE_DIR') is not None:
            self.resource_dir = os.environ.get('UBENCH_RESOURCE_DIR')
            self.settings_source['UBENCH_RESOURCE_DIR'] = {'origin' : origin,
                                                           'val' : self.resource_dir}
        if os.environ.get('UBENCH_REPORT_DIR') is not None:
            self.report_dir = os.environ.get('UBENCH_REPORT_DIR')
            self.settings_source['UBENCH_REPORT_DIR'] = {'origin' : origin,
                                                         'val' : self.report_dir}
        if os.environ.get('UBENCH_RESULTS_DIR') is not None:
            self.results_dir = os.environ.get('UBENCH_RESULTS_DIR')
            self.settings_source['UBENCH_RESULTS_DIR'] = {'origin' : origin,
                                                          'val' : self.results_dir}

        # Repository configuration
        if os.environ.get('UBENCH_PUBLISH_VCS') is not None:
            self.pub_vcs = os.environ.get('UBENCH_PUBLISH_VCS')
            self.settings_source['UBENCH_PUBLISH_VCS'] = {'origin' : origin,
                                                          'val' : self.pub_vcs}
        if os.environ.get('UBENCH_PUBLISH_REPOSITORY') is not None:
            self.pub_repo = os.environ.get('UBENCH_PUBLISH_REPOSITORY')
            self.settings_source['UBENCH_PUBLISH_REPOSITORY'] = {'origin' : origin,
                                                                 'val' : self.pub_repo}
        if os.environ.get('UBENCH_PUBLISH_PROTOCOL') is not None:
            self.pub_protocol = os.environ.get('UBENCH_PUBLISH_PROTOCOL')
            self.settings_source['UBENCH_PUBLISH_PROTOCOL'] = {'origin' : origin,
                                                               'val' : self.pub_protocol}
        if os.environ.get('UBENCH_PUBLISH_SERVER') is not None:
            self.pub_server = os.environ.get('UBENCH_PUBLISH_SERVER')
            self.settings_source['UBENCH_PUBLISH_SERVER'] = {'origin' : origin,
                                                             'val' : self.pub_server}
        if os.environ.get('UBENCH_PUBLISH_PATH') is not None:
            self.pub_path = os.environ.get('UBENCH_PUBLISH_PATH')
            self.settings_source['UBENCH_PUBLISH_PATH'] = {'origin' : origin,
                                                           'val' : self.pub_path}


    def init_config_local(self, origin):
        """ Initializes path variables with values found in LOCAL configuration file """

        config = configparser.ConfigParser()
        f = config.read('' + pwd.getpwuid(os.getuid()).pw_dir + '/.unclebench/ubench.conf')
        if len(f) > 0:
            self.load_config(config, origin)


    def init_config_sys(self, origin):
        """ Initializes path variables with values found in GLOBAL configuration file """

        config = configparser.ConfigParser()
        f = config.read('/etc/unclebench/ubench.conf')
        if len(f) > 0:
            self.load_config(config, origin)


    def init_default(self, origin):
        """ Initializes path variables with DEFAULT values """

        # Install directories
        self.plugin_dir = '/usr/share/unclebench/lib/plugins'
        self.settings_source['UBENCH_PLUGIN_DIR'] = {'origin' : origin,
                                                     'val' : self.plugin_dir}
        self.platform_dir = '/usr/share/unclebench/platform'
        self.settings_source['UBENCH_PLATFORM_DIR'] = {'origin' : origin,
                                                       'val' : self.platform_dir}
        self.benchmark_dir = '/usr/share/unclebench/benchmarks'
        self.settings_source['UBENCH_BENCHMARK_DIR'] = {'origin' : origin,
                                                        'val' : self.benchmark_dir}
        self.conf_dir = '/etc/unclebench'
        self.settings_source['UBENCH_CONF_DIR'] = {'origin' : origin,
                                                   'val' : self.conf_dir}
        self.stylesheet_path = '/usr/share/unclebench/css/asciidoctor-bench-report.css'
        self.settings_source['UBENCH_CSS_PATH'] = {'origin' : origin,
                                                   'val' : self.stylesheet_path}
        self.templates_path = '/usr/share/unclebench/templates'
        self.settings_source['UBENCH_TEMPLATES_PATH'] = {'origin' : origin,
                                                         'val' : self.templates_path}

        # Working directories
        if os.environ.get('SCRATCHDIR') is None:
            self.run_dir = pwd.getpwuid(os.getuid()).pw_dir + '/ubench/benchmarks'
        else:
            self.run_dir = os.environ.get('SCRATCHDIR') + '/ubench/benchmarks'
        self.settings_source['UBENCH_RUN_DIR_BENCH'] = {'origin' : origin,
                                                        'val' : self.run_dir}

        if os.environ.get('SCRATCHDIR') is None:
            self.resource_dir = pwd.getpwuid(os.getuid()).pw_dir + '/ubench/resource'
        else:
            self.resource_dir = os.environ.get('SCRATCHDIR') + '/ubench/resource'
        self.settings_source['UBENCH_RESOURCE_DIR'] = {'origin' : origin,
                                                       'val' : self.resource_dir}
        self.report_dir = self.run_dir+'/reports'
        self.settings_source['UBENCH_REPORT_DIR'] = {'origin' : origin,
                                                     'val' : self.report_dir}

        if os.environ.get('SCRATCHDIR') is None:
            self.results_dir = pwd.getpwuid(os.getuid()).pw_dir + '/ubench/results'
        else:
            self.results_dir = os.environ.get('SCRATCHDIR') + '/ubench/results'
        self.settings_source['UBENCH_RESULTS_DIR'] = {'origin' : origin,
                                                       'val' : self.results_dir}

        # Repository configuration
        self.pub_vcs = 'undefined'
        self.settings_source['UBENCH_PUBLISH_VCS'] = {'origin' : origin,
                                                      'val' : self.pub_vcs}
        self.pub_repo = 'undefined'
        self.settings_source['UBENCH_PUBLISH_REPOSITORY'] = {'origin' : origin,
                                                             'val' : self.pub_repo}
        self.pub_protocol = 'undefined'
        self.settings_source['UBENCH_PUBLISH_PROTOCOL'] = {'origin' : origin,
                                                           'val' : self.pub_protocol}
        self.pub_server = 'undefined'
        self.settings_source['UBENCH_PUBLISH_SERVER'] = {'origin' : origin,
                                                         'val' : self.pub_server}
        self.pub_path = 'undefined'
        self.settings_source['UBENCH_PUBLISH_PATH'] = {'origin' : origin,
                                                       'val' : self.pub_path}

    def load_config(self, config_parser, origin):
        """ Loads values from ubench.conf.

        General procedure used to load variables found in ubench.conf
        and to update `settings_source` dictionary accordingly.
        This procedure is used by `init_config_local` and `init_config_sys`.

        Args:
            config_parser: config parser object
            origin: wether local file or system file (this is the value that will apear
                    to user when ubench info is executed. It is just an information value and
                    has no effect on program behaviour.
        """

        section = 'INSTALL_DIR'
        if config_parser.has_option(section, 'UBENCH_PLUGIN_DIR'):
            self.plugin_dir = config_parser.get(section, 'UBENCH_PLUGIN_DIR')
            self.settings_source['UBENCH_PLUGIN_DIR'] = {'origin' : origin,
                                                         'val' : self.plugin_dir}
        if config_parser.has_option(section, 'UBENCH_PLATFORM_DIR'):
            self.platform_dir = config_parser.get(section, 'UBENCH_PLATFORM_DIR')
            self.settings_source['UBENCH_PLATFORM_DIR'] = {'origin' : origin,
                                                           'val' : self.platform_dir}
        if config_parser.has_option(section, 'UBENCH_BENCHMARK_DIR'):
            self.benchmark_dir = config_parser.get(section, 'UBENCH_BENCHMARK_DIR')
            self.settings_source['UBENCH_BENCHMARK_DIR'] = {'origin' : origin,
                                                            'val' : self.benchmark_dir}
        if config_parser.has_option(section, 'UBENCH_CONF_DIR'):
            self.conf_dir = config_parser.get(section, 'UBENCH_CONF_DIR')
            self.settings_source['UBENCH_CONF_DIR'] = {'origin' : origin,
                                                       'val' : self.conf_dir}
        if config_parser.has_option(section, 'UBENCH_CSS_PATH'):
            self.stylesheet_path = config_parser.get(section, 'UBENCH_CSS_PATH')
            self.settings_source['UBENCH_CSS_PATH'] = {'origin' : origin,
                                                       'val' : self.stylesheet_path}
        if config_parser.has_option(section, 'UBENCH_TEMPLATES_PATH'):
            self.templates_path = config_parser.get(section, 'UBENCH_TEMPLATES_PATH')
            self.settings_source['UBENCH_TEMPLATES_PATH'] = {'origin' : origin,
                                                             'val' : self.templates_path}

        section = 'WORK_DIR'
        if config_parser.has_option(section, 'UBENCH_RUN_DIR_BENCH'):
            self.run_dir = config_parser.get(section, 'UBENCH_RUN_DIR_BENCH')
            self.settings_source['UBENCH_RUN_DIR_BENCH'] = {'origin' : origin,
                                                            'val' : self.run_dir}
        if config_parser.has_option(section, 'UBENCH_RESOURCE_DIR'):
            self.resource_dir = config_parser.get(section, 'UBENCH_RESOURCE_DIR')
            self.settings_source['UBENCH_RESOURCE_DIR'] = {'origin' : origin,
                                                           'val' : self.resource_dir}
        if config_parser.has_option(section, 'UBENCH_REPORT_DIR'):
            self.report_dir = config_parser.get(section, 'UBENCH_REPORT_DIR')
            self.settings_source['UBENCH_REPORT_DIR'] = {'origin' : origin,
                                                         'val' : self.report_dir}
        if config_parser.has_option(section, 'UBENCH_RESULTS_DIR'):
            self.results_dir = config_parser.get(section, 'UBENCH_RESULTS_DIR')
            self.settings_source['UBENCH_RESULTS_DIR'] = {'origin' : origin,
                                                         'val' : self.results_dir}

        section = 'PUBLISH'
        if config_parser.has_option(section, 'UBENCH_PUBLISH_VCS'):
            self.pub_vcs = config_parser.get(section, 'UBENCH_PUBLISH_VCS')
            self.settings_source['UBENCH_PUBLISH_VCS'] = {'origin' : origin,
                                                          'val' : self.pub_vcs}
        if config_parser.has_option(section, 'UBENCH_PUBLISH_REPOSITORY'):
            self.pub_repo = config_parser.get(section, 'UBENCH_PUBLISH_REPOSITORY')
            self.settings_source['UBENCH_PUBLISH_REPOSITORY'] = {'origin' : origin,
                                                           'val' : self.pub_repo}
        if config_parser.has_option(section, 'UBENCH_PUBLISH_PROTOCOL'):
            self.pub_protocol = config_parser.get(section, 'UBENCH_PUBLISH_PROTOCOL')
            self.settings_source['UBENCH_PUBLISH_PROTOCOL'] = {'origin' : origin,
                                                               'val' : self.pub_protocol}
        if config_parser.has_option(section, 'UBENCH_PUBLISH_SERVER'):
            self.pub_server = config_parser.get(section, 'UBENCH_PUBLISH_SERVER')
            self.settings_source['UBENCH_PUBLISH_SERVER'] = {'origin' : origin,
                                                             'val' : self.pub_server}
        if config_parser.has_option(section, 'UBENCH_PUBLISH_PATH'):
            self.pub_path = config_parser.get(section, 'UBENCH_PUBLISH_PATH')
            self.settings_source['UBENCH_PUBLISH_PATH'] = {'origin' : origin,
                                                           'val' : self.pub_path}

    def set_environment_vars(self):
        """ Sets proper environment variables.

        Sets environment variables if         UBENCH_PLATFORM_DIR
        they were not previously set:         UBENCH_BENCHMARK_DIR
                                              UBENCH_RESOURCE_DIR
        """

        if os.environ.get('UBENCH_PLATFORM_DIR') is None:
            os.environ['UBENCH_PLATFORM_DIR'] = self.settings_source['UBENCH_PLATFORM_DIR']['val']

        if os.environ.get('UBENCH_BENCHMARK_DIR') is None:
            os.environ['UBENCH_BENCHMARK_DIR'] = self.settings_source['UBENCH_BENCHMARK_DIR']['val']

        if os.environ.get('UBENCH_RESOURCE_DIR') is None:
            os.environ['UBENCH_RESOURCE_DIR'] = self.settings_source['UBENCH_RESOURCE_DIR']['val']

    def clear_info(self):
        """ Variables listed here will not appear in ubench `info command` """

        clear_list = [
                      'UBENCH_PUBLISH_PROTOCOL',
                      'UBENCH_PUBLISH_SERVER',
                      'UBENCH_PUBLISH_PATH',
                     ]
        for var in clear_list:
            self.settings_source[var]['clear'] = True

    def print_config(self, verbose=False, pad=30):  # pylint: disable=unused-argument
        """ Prints origin and value of variables.

        Procedure used to display the origin of the settings loaded
        and which can be invoked at the command line using the info command.

        Args:
            pad (int): sets the padding level (not in use)
        """

        max_var = max([len(i) for i in list(self.settings_source.keys())])
        max_origin = max([len(k['origin']) for k in list(self.settings_source.values())])
        max_val = max([len(k['val']) for k in list(self.settings_source.values())])
        pad_var = max_var + 10
        pad_origin = max_origin + 10
        line_length = pad_var + pad_origin + max_val + 3

        print('\n {:<{pad_var}} {:<{pad_origin}} {}'.
              format('Variable', 'Origin', 'Value', pad_var=pad_var, pad_origin=pad_origin))
        print('─'*line_length)

        sorted_keys = self.settings_source.keys()
        sorted_keys.sort()

        if verbose == False:
            self.clear_info()

        for i in sorted_keys:
            if 'clear' not in self.settings_source[i]:
                print(' {:<{pad_var}} {:<{pad_origin}} {}'.
                      format(i, self.settings_source[i]['origin'],
                             self.settings_source[i]['val'],
                             pad_var=pad_var, pad_origin=pad_origin))
        print('─'*line_length)
        print('')

    def get_platform_list(self):
        """ Get list of available platforms """

        platform_list = []
        jube_xml = jube_xml_parser.JubeXMLParser('', [], '', self.platform_dir)
        root = jube_xml.load_platforms_xml()
        for node in root.getiterator('path'):
            tags = node.get('tag')
            if tags:
                for tag in tags.split(','):
                    platform_list.append(tag)

        platform_list = list(set(platform_list))

        return sorted(platform_list, key=str.lower)


    def find_all_rec(node, node_name, node_name_attr, root):  # pylint: disable=no-self-argument, unused-argument
        """ Internal method """

        for step in node.findall(node_name):  # pylint: disable=no-member
            if step.get('name') == node_name_attr:
                result.append()  # pylint: disable=undefined-variable

        return result  # pylint: disable=undefined-variable


    def find_rec(self, node, element, name):  # pylint: disable=no-self-use
        """ Internal method"""

        for item in node.findall(element):
            if item.get('name') == 'execute':
                yield item
            for child in find_rec(item, element, name):  # pylint: disable=undefined-variable
                yield child


    def get_benchmark_list(self):
        """ Get list of available benchmarks """

        bench_list = [f for f in os.listdir(self.benchmark_dir)
                      if os.path.isdir(os.path.join(self.benchmark_dir, f))]
        filtered_bench_list = []

        # Only benchmarks that define an execute step are considered
        for bench_dir in bench_list:
            execute_step = False
            for filename in os.listdir(os.path.join(self.benchmark_dir, bench_dir)):
                if not filename.endswith('.xml'): continue  # pylint: disable=multiple-statements
                try:
                    tree = ET.parse(os.path.join(self.benchmark_dir, bench_dir, filename))
                except ET.ParseError:
                    continue

                root = tree.getroot()
                if self.find_rec(root, 'step', 'execute'):
                    execute_step = True
                    break
            if(execute_step):
                filtered_bench_list.append(bench_dir.lower())

        return filtered_bench_list
