# -*- coding: utf-8 -*-
##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2020 EDF SA                                           #
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
''' Implements Publisher class '''

from __future__ import print_function

# Enables having file names with a single letter and using members from sub-classes
# pylint: disable=invalid-name, no-member, super-init-not-called

import re
import os
import glob
import shutil
from ubench.data_management.vcs.git import Git
from ubench.data_management.data_store_yaml import DataStoreYAML
import ubench.utils as utils

class Publisher(object):
    ''' Publisher class

    The main goal for this class is to copy the benchmark or campaign
    results from the benchmark run directory to the local repository.
    This class also provides methods to (a) copy the repository from
    remote location and to (b) update the remote repository.

    This class has two other child classes, Campaign and Benchmark.
    The reason for this method lays on different initialization parameters
    but also on different ways to handle origin and destination directories
    for benchmarks and campaigns. Knowing that the main operation is the same,
    ie, to copy files from one place to another, it seems a good choice to
    have a single method to do this operation, but custom methods to handle
    the construction of origin and destination directories. This seems even
    a better idea since we are still in an early stage of development where
    future uses of this class are not yet envisioned.

    Methods:
        publish
        download
        update_remote
        get_files_from_ref
    '''
    results_fname = 'bench_results.yaml'
    regexp = re.compile(r'''
                         campaign-
                         (?P<campaign_name>.*)
                         - 
                         (?P<campaign_date>[0-9]{4}-[0-9]{2}-[0-9]{2})
                         _
                         (?P<campaign_time>[0-9]{2}-[0-9]{2})
                         ''', re.VERBOSE)

    def __init__(self, repo_str=None, local_dir=None, vcs=None):
        ''' Contructor '''
        self.repo_str = repo_str
        self.local_dir = local_dir
        self.vcs = vcs

    def update_remote(self):
        ''' Updates remote repository with local commits '''
        vcs = self._return_vcs()
        vcs.update_remote()

    def download(self):
        ''' Downloads remote repository to local machine '''
        vcs = self._return_vcs()
        vcs.copy_remote_to_local()

    def publish(self, commit_msg):
        ''' Copy, commit and push '''
        self._copy_files()
        self.vcs = self._return_vcs()
        self.vcs.add_contents_to_local_repo(self._files_to_commit(), commit_msg)

    def get_files_from_ref(self, ref):
        ''' Returns benchmark results

        Returns path to bench_results.yaml for every benchmark
        listed in given commit.

        Args:
            reference to commit
        Returns:
            { benchmark : 'path/to/bench_results.yaml' }
        '''
        vcs = Git(self.local_dir, self.repo_str)
        files = vcs.get_files_from_tag(ref)
        b_map = {}
        for f in files:
            data = DataStoreYAML()
            metadata, _ = data.load(f)
            b_map[metadata['Benchmark_name']] = f
        return b_map

    def _copy_files(self):
        ''' Copy files from execution directory to local repository '''
        for f, b in zip(self._files_to_publish(), self._benchs_to_publish()):
            dest = os.path.join(self.local_dir, 'results', self.publish_dir, b)
            utils.mkdir(dest, err_msg=utils.global_msg['err_dir_exists'])
            shutil.copy2(f, dest)
            print('{} [{}] ---> {}'.format(self.results_fname, b, utils.trim_head(dest, 4)))

    def _files_to_commit(self):
        ''' Returns absolute path of files to commit '''
        files = []
        for f, b in zip(self._files_to_publish(), self._benchs_to_publish()):
            dest = os.path.join(self.local_dir, 'results', self.publish_dir, b)
            files.append(os.path.join(dest, os.path.basename(f)))
        return files

    def _return_vcs(self):
        ''' Return VCS instance '''
        vcs = Git(self.local_dir, self.repo_str)
        return vcs

class Benchmark(Publisher):
    ''' Provides specific Benchmark customization '''

    # pylint: disable=too-many-arguments
    def __init__(self, local_dir, publish_dir, benchmark, platform, run_dir, run_id=None):
        ''' Constructor '''
        self.local_dir = local_dir
        self.publish_dir = publish_dir
        self.benchmark = benchmark
        self.platform = platform
        self.run_id = run_id
        self.run_dir = run_dir

    def _files_to_publish(self):
        ''' Returns absolute path of bench_results.yaml file in benchmark context

        If no run id is specified, it will return the last execution found,
        the execution with greatest run_id. '''
        if self.run_id is None:
            self.run_id = utils.get_bench_rundir(self.run_dir, self.platform, self.benchmark)
        path = os.path.join(self.run_dir, self.platform, self.benchmark, 'benchmark_runs',
                            self.run_id, self.results_fname)
        file_list = glob.glob(path)
        return file_list

    def _benchs_to_publish(self):
        ''' For compliance with publish method. This step not needed at the current
        development phase in the benchmark context. '''
        return [self.benchmark]

    def _return_vcs(self):
        ''' Return VCS instance '''
        vcs = Git(self.local_dir)
        return vcs

class Campaign(Publisher):
    ''' Provides specific Campaign customization '''

    def __init__(self, local_dir, publish_dir, campaign_dir, run_dir):
        ''' Constructor '''
        self.local_dir = local_dir
        self.publish_dir = publish_dir
        self.campaign_dir = campaign_dir
        self.run_dir = run_dir

    def _benchs_to_publish(self):
        ''' Creates list - each element its a benchmark execution '''
        return [os.path.basename(utils.trim_tail(bench, 3)) for bench in self._files_to_publish()]

    def _files_to_publish(self):
        ''' Returns absolute path of bench_results.yaml files in campaign context '''
        path = os.path.join(self.run_dir, self.campaign_dir, '*', 'benchmark_runs',
                            '000000', self.results_fname)
        file_list = glob.glob(path)
        return file_list

    def _campaign_name(self):
        ''' Returns campaign name (based on campaign directory) '''
        return re.search(self.regexp, self.campaign_dir).groupdict()['campaign_name']

    def _campaign_date(self):
        ''' Returns campaign date (based on campaign directory) '''
        return re.search(self.regexp, self.campaign_dir).groupdict()['campaign_date']

    def _campaign_time(self):
        ''' Returns campaign time (based on campaign directory) '''
        return re.search(self.regexp, self.campaign_dir).groupdict()['campaign_time']

    def _return_vcs(self):
        ''' Return VCS instance '''
        vcs = Git(self.local_dir)
        return vcs
