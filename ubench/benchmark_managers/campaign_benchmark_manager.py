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
# pylint: disable=invalid-name, superfluous-parens, too-many-instance-attributes
# pylint: disable=no-member, no-self-use, redefined-builtin
''' Define CampaignManager class '''

import sys
import time
import os
from datetime import datetime
from shutil import copytree
from pydoc import locate
import collections
import multiprocessing as mp
import yaml

from ubench.scheduler_interfaces.slurm_interface import (wlist_to_scheduler_wlist,
                                                         SlurmInterface)
from ubench.data_management.publisher import Publisher
from ubench.data_management.data_store_yaml import DataStoreYAML
from ubench.config import CAMPAIGN_DATE_FORMAT, BENCHMARK_API_CLASS
from ubench.core.ubench_config import UbenchConfig
from ubench.data_management.comparison_writer import ComparisonWriter
from ubench.progress import Progress


class CampaignManager(object):
    ''' Campaign Manager for unclebench

    Class attributes:
        ref_results (str) - commit id for bench comparision
        campaign (dict)   - campaign file contents

        benchmarks  - ordered dict with (bench, JubeBenchmarkingAPI object)
        exec_info   - ordered dict with (bench, (JubeRun object, parameters list)))

        campaign_status - ordered dict for monitoring the execution of
                          each benchmark having the following information:

            Initially the following fields are created:

            { 'bench' : { status, jobs=[], pre-results } }

            > status        - 'INIT', 'CONFIGURING', 'COMPILING', 'PENDING', 'RUNNING', 'FINISHED'
              jobs          - list of all jobs for current bench
              pre_results   - path to current bench_results.yaml

              post_results  - path to previous bench_results.yaml (only)
              results       - current results or comparison results
              finished_jobs - finished jobs (for current bench)
              num_jobs      - total number of jobs (for current bench)

              In particular, `jobs` is a list of dicts contaning
              info about each job for the current bench:

            > jube_dir
              status
              job_id
              result

        data_campaign - date the campaign was launched
        campaign_dir - execution directory under UBENCH_RUN_DIR_BENCH
    '''

    def __init__(self, campaign_file, ref_results=None, campaign_freq=12):
        ''' Initialize CampaignManager object '''

        # compatibility with old Pyyaml versions
        self.campaign = self.campaign_parser(campaign_file)
        self.benchmarks = collections.OrderedDict()
        self.ref_results = ref_results
        self.exec_info = collections.OrderedDict()
        self.campaign_status = collections.OrderedDict()
        self.scheduler_interface = SlurmInterface()
        date_campaign = datetime.now().strftime(CAMPAIGN_DATE_FORMAT)
        self.campaign_dir = os.path.join(UbenchConfig().run_dir,
                                         'campaign-{}-{}'.format(self.campaign['name'],
                                                                 date_campaign))
        self.campaign_freq = campaign_freq
        self.pub_vcs = UbenchConfig().pub_vcs
        self.pub_local_dir = UbenchConfig().results_dir
        self.pub_repo_str = UbenchConfig().pub_repo
        self.results_table = {'update' : 0}

    def campaign_parser(self, campaign_file):
        ''' Basic parser for benchmark campaign specification file '''

        yaml_attrs = getattr(yaml, '__dict__', {})
        if 'FullLoader' in yaml_attrs:
            campaign_data = yaml.load(open(campaign_file, 'r'), Loader=yaml.FullLoader)
        else:
            campaign_data = yaml.load(open(campaign_file, 'r'))

        platform = campaign_data['platform']
        benchmarks = campaign_data['benchmarks']
        platform_avail = UbenchConfig().get_platform_list()
        benchmark_list = UbenchConfig().get_benchmark_list()
        # check platform
        if platform not in platform_avail:
            print('\nPlatform {} is not available.'
                  '\nPlatforms available {}'.format(platform, platform_avail))
            raise RuntimeError

        for bench in benchmarks:
            if bench not in benchmark_list:
                print('\nBenchmark {} is not available.'
                      '\nBenchmarks available {}'.format(bench, benchmark_list))
                raise RuntimeError

        # order has to be checked as well
        return campaign_data


    def init_campaign(self):
        ''' Initialize Campaign

        Creates directories for each benchmark;
        Populates `benchmarks` variable;
        Creates an entry in `campaign_status` for each benchmark.
        '''
        try:
            os.makedirs(self.campaign_dir)
        except (OSError) as e:
            print('Error: Campaign directory exist!!')
            print(e)
            raise

        # create benchmark objects
        benchmark_api = locate(BENCHMARK_API_CLASS)

        # we order the benchmark using order key
        def bench_order(elem):
            ''' helper function to guarantee benchmark order '''
            _, value = elem
            return value['order']

        c_benchmarks = sorted(self.campaign['benchmarks'].items(),
                              key=bench_order)

        platform = self.campaign['platform']

        publisher = Publisher(repo_str=self.pub_repo_str, local_dir=self.pub_local_dir,
                              vcs=self.pub_vcs)

        # If no reference given, bench_files will be an empty dict
        bench_files = publisher.get_files_from_ref(self.ref_results)

        for b_name, _ in c_benchmarks:
            print('Initializing benchmark {}'.format(b_name))
            benchmark_dir = self._init_bench_dir(b_name)
            self.benchmarks[b_name] = benchmark_api(b_name, platform)
            self.benchmarks[b_name].benchmark_path = benchmark_dir
            self.campaign_status[b_name] = {}
            self.campaign_status[b_name]['status'] = 'INIT'
            self.campaign_status[b_name]['jobs'] = []
            # Only when comparing results otherwise empty
            self.campaign_status[b_name]['pre_results'] = bench_files.get(b_name, None)

    def _init_bench_dir(self, benchmark):
        ''' Create and initialize run directory '''

        benchmark_dir = os.path.join(self.campaign_dir, benchmark)
        src_dir = os.path.join(UbenchConfig().benchmark_dir, benchmark)
        print('---- Copying {} to {}'.format(src_dir, benchmark_dir))
        try:
            copytree(src_dir, benchmark_dir, symlinks=True)
        except OSError:
            print('---- {} description files are already present in ' \
                  'run directory and will be overwritten.'.format(benchmark))

        return benchmark_dir


    def init_job_info(self, benchmark):
        """ Initialize campaign data structure"""

        if 'num_jobs' not in self.campaign_status[benchmark]:
            j_job, _ = self.exec_info[benchmark]
            job_ids = j_job.job_ids
            self.campaign_status[benchmark]['num_jobs'] = len(job_ids)
            self.campaign_status[benchmark]['finished_jobs'] = 0
            self.campaign_status[benchmark]['status'] = 'RUNNING'
            self.campaign_status[benchmark]['results'] = {}

    def get_diff_results(self, benchmark, exec_dir):
        ''' Returns the value obtained by comparing the
        current execution result with the previous one.

        This method will not work for benchmarks for which the test is
        repeated according to other parameter -> example: message length
        '''

        c_benchmarks = self.campaign['benchmarks']
        st_bench = self.campaign_status[benchmark]
        data_store = DataStoreYAML()

        # Reads previous execution parameters
        # print('Using result file: {}'.format(st_bench['post_results']))
        result_filter = data_store.get_result_filter({'jube_wp_abspath': exec_dir},
                                                     c_benchmarks[benchmark]['parameters'],
                                                     st_bench['post_results'])

        # Returns resulting value between both executions
        column_headers = ''
        result = data_store.compaire_bench_runs(st_bench['pre_results'],
                                                st_bench['post_results'],
                                                result_filter,
                                                column_headers)
        return result

    def update_campaign_status(self):
        ''' Update status for each benchmark

        Status is monitored by the variable campaign_status.
        Jube return code is used to check when COMPILING is finished.
        '''

        finish_states = ['COMPLETED', 'FAILED', 'CANCELLED']
        for b_name, values in self.exec_info.items():

            # Benchs marked with FINISHED are done!
            if self.campaign_status[b_name]['status'] != 'FINISHED':
                j_job, _ = values

                # No jube return code => still compiling
                if j_job.jube_returncode is None:
                    self.campaign_status[b_name]['status'] = 'COMPILING'

                # Benchs in execution will update `finished_jobs` and `post_results`
                elif j_job.jube_returncode == 0:
                    self.init_job_info(b_name)
                    job_req = self.scheduler_interface.get_jobs_state(j_job.job_ids)
                    finished_jobs = [j_n for j_n, j_s in job_req.items() if j_s in finish_states]
                    if len(finished_jobs) > self.campaign_status[b_name]['finished_jobs']:
                        self.benchmarks[b_name].result(0, output=False)
                        self.campaign_status[b_name]['finished_jobs'] = len(finished_jobs)
                        self.campaign_status[b_name]['post_results'] \
                                                  = self.benchmarks[b_name].results_file

                    # If all jobs for current bench have finished mark bench also as finished
                    if self.campaign_status[b_name]['finished_jobs'] \
                                                  == self.campaign_status[b_name]['num_jobs']:
                        self.campaign_status[b_name]['status'] = 'FINISHED'

                    # `jobs` list is reset everytime
                    # `result` will contain (current OR comparision) value
                    self.campaign_status[b_name]['jobs'] = []
                    for exec_dir, job_id in j_job.exec_dir.items():
                        result = {}
                        #if self.campaign_status[b_name]['pre_results'] and job_id in finished_jobs:
                        #    pass
                        #    #result = self.get_diff_results(b_name, exec_dir)
                        #else:
                        #    bench_results = self.benchmarks[b_name].results
                        #    result = bench_results.get(exec_dir, {})
                        status = {'jube_dir' : exec_dir,
                                  'status' : job_req.get(job_id, 'UNKNOWN'),
                                  'job_id' : job_id,
                                  'result': result}
                        self.campaign_status[b_name]['jobs'].append(status)


    def non_finished(self):
        ''' Return False if campaign has not finished yet '''
        for info in self.campaign_status.values():
            if info['status'] != 'FINISHED':
                return True
        return False

    def _run_progress_bar(self):
        ''' Shows progress bar '''
        usr_msg = mp.Process(target=Progress.blink, args=(Progress(msg=" RUNNING"),))
        usr_msg.start()
        time.sleep(self.campaign_freq)
        usr_msg.terminate()
        usr_msg.join()
        os.system('tput sgr0')
        os.system('tput cnorm')

    def run(self):
        ''' Run campaign workflow '''
        # Launch all benchmarks
        c_benchmarks = self.campaign['benchmarks']

        for b_name, b_obj in self.benchmarks.items():
            print('Executing benchmark: {}'.format(b_name))
            parameters = c_benchmarks[b_name]['parameters']
            if 'w' in parameters:
                parameters['w'] = wlist_to_scheduler_wlist(parameters['w'])

            parameters['custom_params'] = parameters
            self.exec_info[b_name] = b_obj.run(parameters)
            # Drop ubench parameters
            c_benchmarks[b_name]['parameters'].pop('w', None)
            c_benchmarks[b_name]['parameters'].pop('custom_params', None)

        while self.non_finished():
            self.update_campaign_status()
            self.print_campaign_status()
            self._run_progress_bar()

        print('\nEnd : {}\n'.format(datetime.now().time().strftime('%H:%M:%S')))

        # If -r option was passed at the command line show difference using
        # ubench compare otherwise show benchmark result using ubench result
        for bench in self.benchmarks.keys():
            print(bench)
            if self.campaign_status[bench]['pre_results']:
                bench_dirs = [self.campaign_status[bench]['pre_results'],
                              self.campaign_status[bench]['post_results']]
                bench_dirs = [os.path.split(dir)[0] for dir in bench_dirs]
                writer = ComparisonWriter()
                writer.print_comparison(bench, bench_dirs)
            else:
                self.benchmarks[bench].result(0, campaign=True, output=False)

        print('Campaign finished successfully')


    def print_campaign_status(self):
        ''' Print campaign status '''
        width = 20
        columns = 5
        print_format = '{{:^{0}s}} '.format(width)*columns

        table_rows = 0
        for b_name, values in self.campaign_status.items():
            if self.campaign_status[b_name]['jobs']:
                table_rows += len(self.campaign_status[b_name]['jobs'])
            else:
                table_rows += 1

        # Print table header (first time only)
        if self.results_table['update'] == 0:
            print('\nStart : {}'.format(datetime.now().time().strftime('%H:%M:%S')))
            print('\n{}'.format('-'*width*columns))
            print(print_format.format('Benchmark',
                                      'Bench status',
                                      'Jube_dir',
                                      'Job',
                                      'Status'))
            print('-'*width*columns)

        # Delete table rows (does not delete table header)
        if self.results_table['update'] > 0:
            sys.stdout.write("\033[F"*(self.results_table['rows']+2))

        # Print table rows
        for b_name, values in self.campaign_status.items():
            if values['jobs']:
                for job in values['jobs']:
                    print(print_format.format(b_name,
                                              self.campaign_status[b_name]['status'],
                                              job['jube_dir'],
                                              job['job_id'],
                                              job['status']))
            else:
                print(print_format.format(b_name,
                                          self.campaign_status[b_name]['status'],
                                          '',
                                          '',
                                          ''))

        print(' ' * 20)
        self.results_table['update'] += 1
        self.results_table['rows'] = table_rows - 1
