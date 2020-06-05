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
# pylint: disable=superfluous-parens, fixme, invalid-name
''' Define UbenchCmd class '''


import os
from subprocess import Popen
import yaml

from ubench.core.ubench_config import UbenchConfig
import ubench.benchmark_managers.benchmark_manager_set as bms
from ubench.benchmark_managers.campaign_benchmark_manager import CampaignManager
import ubench.benchmarking_tools_interfaces.jube_xml_parser as jube_xml_parser
import ubench.core.fetcher as fetcher
import ubench.data_management.comparison_writer as comparison_writer
import ubench.data_management.report as report
from ubench.scheduler_interfaces.slurm_interface import wlist_to_scheduler_wlist
from ubench.data_management.publisher import Campaign, Benchmark, Publisher
import ubench.utils as utils


class UbenchCmd(object):
    ''' Implements Unclebench commands.

    Each Unclebench command that can be calld from the command
    line is defined in this class.

    Attributes:
        run_dir
        platform
        benchmark_list
        bm_set
        pub_vcs : which vcs to use
        pub_repo_str : string used to clone repository
        pub_dir : local repository directory

    Methods:
        log
        list_parameters
        result
        run
        fetch
        compare
        report
        campaign
        publish
    '''

    def __init__(self, platform, benchmark_list=None):
        ''' Class constructor '''

        self.run_dir = os.path.join(UbenchConfig().run_dir, platform)
        self.platform = platform

        # Add benchmark managers for each benchmark in directory
        self.benchmark_list = benchmark_list
        self.bm_set = bms.BenchmarkManagerSet(benchmark_list, platform)

        # Attributs for Publisher class
        self.pub_vcs = UbenchConfig().pub_vcs
        self.pub_repo_str = UbenchConfig().pub_repo
        self.pub_dir = UbenchConfig().results_dir

    def log(self, id_list): # pylint: disable=dangerous-default-value
        ''' Provides information about benchmark execution

        Args:
            id_list (optional): by default, it will print information on last
                                execution for the instance benchmark and platform.
        '''
        if id_list is None:
            id_list = [-1]

        for idb in id_list:
            self.bm_set.print_log(int(idb))


    def list_parameters(self, default_values=False):
        ''' Lists benchmark parameters '''

        self.bm_set.list_parameters(default_values)


    def result(self, id_list): # pylint: disable=dangerous-default-value
        ''' Prints benchmark results '''

        if id_list is None:
            id_list = ['last']

        for idb in id_list:
            self.bm_set.result(idb)
            # self.bm_set.analyse(idb)
            # self.bm_set.extract_results(idb)
            self.bm_set.print_result_array()


    def listb(self):
        ''' Lists runs information '''

        self.bm_set.list_runs()


    def run(self, opt_dict={}):  # pylint: disable=dangerous-default-value
        '''  Run benchmark

        Args:
            dict_options:

        Returns:
            Bool: True if an error is raised, False otherwise
        '''

        if opt_dict['w']:

            try:
                opt_dict['w'] = wlist_to_scheduler_wlist(opt_dict['w'])
            except Exception as exc:  # pylint: disable=broad-except
                print('---- Custom node configuration is not valid : {0}'.format(str(exc)))
                return False
        print('')
        print('-- Ubench platform name set to : {0}'.format(self.platform))

        if not os.path.isdir(UbenchConfig().resource_dir):
            print('---- The resource directory {0} does not exist.'.
                  format(UbenchConfig().resource_dir) +
                  'Please run ubench fetch to retrieve sources and test cases.')
            return False

        # Set custom parameters
        dict_options = {}

        if opt_dict['custom_params']:
            for elem in opt_dict['custom_params']:
                try:
                    param, value = elem.split(':', 1)
                    dict_options[param] = value
                except ValueError:
                    print('---- {0} is not formated correctly'.format(elem) +
                          ', please consider using : -c param:new_value')

        # we read a file which contains a dictionary with the options
        if opt_dict['file_params']:
            with open(opt_dict['file_params'], 'r') as params_file:
                dict_options = yaml.load(params_file)

        # we redefine custom params
        opt_dict['custom_params'] = dict_options

        # Run each benchmarks
        try:
            self.bm_set.run(opt_dict)
        except (RuntimeError, OSError):
            return False

        return True

    def campaign(self, campaign_file, result_ref=None,
                 publish_dir=None, commit_msg=None):
        ''' Executes campaign '''
        campaign = CampaignManager(campaign_file, result_ref)
        campaign.init_campaign()
        campaign.run()
        if publish_dir is not None:
            c = Campaign(local_dir=self.pub_dir, publish_dir=publish_dir,
                         campaign_dir=campaign.campaign_dir, run_dir=self.run_dir)
            c.publish(commit_msg)

    def fetch(self):
        ''' Fetches benchmarks sources '''

        for benchmark_name in self.benchmark_list:
            benchmark_dir = os.path.join(UbenchConfig().benchmark_dir, benchmark_name)
            benchmark_files = [file_b for file_b in os.listdir(benchmark_dir)
                               if file_b.endswith('.xml')]
            jube_xml_files = jube_xml_parser.JubeXMLParser(benchmark_dir, benchmark_files)
            multisource = jube_xml_files.get_bench_multisource()

            if multisource is None:
                print('ERROR !! : Multisource information for benchmark not found')
                exit(1)

            fetch_bench = fetcher.Fetcher(resource_dir=UbenchConfig().resource_dir,
                                          benchmark_name=benchmark_name)
            for source in multisource:

                if 'do_cmds' not in source:
                    source['do_cmds'] = None

                if source['protocol'] == 'https':
                    fetch_bench.https(source['url'], source['files'])

                elif source['protocol'] == 'svn' or source['protocol'] == 'git':
                    if 'revision' not in source:
                        source['revision'] = [None]
                    if 'branch' not in source:
                        source['branch'] = None
                    fetch_bench.scm_fetch(source['url'], source['files'],
                                          source['protocol'], source['revision'],
                                          source['branch'], source['do_cmds'])

                elif source['protocol'] == 'local':
                    fetch_bench.local(source['files'], source['do_cmds'])

    def _return_dirs(self, ref):
        ''' Returns directory from commit hash

        This function receives a reference as argument
        which can be a directory or a commit hash.

        If this function is called with a directory as its
        argument it will return the same thing it received.
        That is, nothing to be done. On the other hand if
        it was called with a commit hash, it will return
        the list of directories regarding that commit.

        Args:
            ref (string) can be a directory or a commit hash
        Returns:
            directory or list of directories related to commit hash
        '''
        if os.path.isdir(ref):
            directory_ref = ref
        else:
            publisher = Publisher(repo_str=self.pub_repo_str,
                                  local_dir=self.pub_dir, vcs=self.pub_vcs)
            bench_files = publisher.get_files_from_ref(ref)
            directory_ref = os.path.dirname(bench_files.values()[0])

        return directory_ref

    # pylint: disable=no-self-use
    def compare(self, input_directories, benchmark_name, context=(None, None),
                threshold=None):
        ''' Compare benchmark results from different directories.

        Args:
            input_directories:
            benchmark_name:
            context:
        '''
        # pylint: disable=bad-whitespace
        input_directories = [ self._return_dirs(ref) for ref in input_directories ]

        cwriter = comparison_writer.ComparisonWriter(threshold)
        print('    comparing :')
        for rdir in input_directories:
            print('    - '+rdir)
        print('')
        cwriter.print_comparison(benchmark_name, input_directories, context)


    def report(self, metadata_file, output_dir):
        ''' Build a performance report.

        Args:
            metadata_file: file containing parameters for report build
            outpit_dir: where to store the report
        '''
        bench_template = os.path.join(UbenchConfig().templates_path, 'bench.html')
        compare_template = os.path.join(UbenchConfig().templates_path, 'compare.html')
        report_template = os.path.join(UbenchConfig().templates_path, 'report.html')
        perf_report = report.Report(metadata_file, bench_template,
                                    compare_template, report_template)
        report_name = 'ubench_performance_report'

        print(('    Writing report {} in {} directory'.format(report_name+'.html', output_dir)))
        perf_report.write(output_dir, report_name)

        asciidoctor_cmd = ('asciidoctor -a stylesheet=' + UbenchConfig().stylesheet_path
                           + ' ' + os.path.join(os.getcwd(), output_dir, report_name + '.asc'))

        Popen(asciidoctor_cmd, cwd=os.getcwd(), shell=True, universal_newlines=True)


    def publish(self, options):
        ''' Guide method to Publish class functionality

        This method will read the variables needed to execute
        each command and then execute it.

        '''
        if (self.pub_vcs == 'undefined' or self.pub_repo_str == 'undefined'
          or self.pub_dir == 'undefined'):
            print('Some or all of the parameters needed by the publish method are missing.\n'
                  'Please fill in the following parameters using ubench.conf'
                  ' file or environment variables: UBENCH_PUBLISH_VCS,'
                  ' UBENCH_PUBLISH_REPOSITORY, UBENCH_RESULTS_DIR')
            exit(1)

        if options['command'] == 'campaign':
            campaign = Campaign(local_dir=self.pub_dir, publish_dir=options['dest_dir'],
                                campaign_dir=options['campaign_dir'], run_dir=self.run_dir)
            campaign.publish(options['commit_msg'])

        if options['command'] == 'benchmark':
            benchmark = Benchmark(local_dir=self.pub_dir, publish_dir=options['dest_dir'],
                                  benchmark=options['benchmark'], platform=options['platform'],
                                  run_dir=self.run_dir)
            benchmark.publish(options['commit_msg'])

        if options['command'] == 'download':
            if os.path.isdir(self.pub_dir):
                print('Error: {} already exists. Please remove it or setup UBENCH_RESULTS_DIR'
                      ' to point to another directory.'.format(self.pub_dir))
                exit(1)
            repository = Publisher(repo_str=self.pub_repo_str, vcs=self.pub_vcs,
                                   local_dir=utils.trim_tail(self.pub_dir))
            repository.download()

        if options['command'] == 'update-remote':
            repository = Publisher(vcs=self.pub_vcs, local_dir=self.pub_dir)
            repository.update_remote()
