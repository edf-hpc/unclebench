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
# pylint: disable=no-self-use,superfluous-parens
""" Provides SlurmInterface class"""


import os
import re
import json
import time
from subprocess import Popen, PIPE
from ClusterShell.NodeSet import NodeSet
import ubench.config
import ubench.utils as utils

def wlist_to_scheduler_wlist(w_list_arg):
    """ Translate ubench custom node list format to scheduler custome node list format

    Args:
        w_list_arg:
    """
    scheduler_interface = SlurmInterface()

    w_list = []
    for element in w_list_arg:
        if element.isdigit():
            elem_tuple = (int(element), None)
        else:
            elem_tuple = (scheduler_interface.get_nnodes_from_string(element), element)
        w_list.append(elem_tuple)

    return w_list

def memoize_disk(cache_file):
    """Memoize to disk with TTL value"""

    user_c_file = "{}-{}".format(cache_file, ubench.config.USER)

    def decorator(original_func):
        """Decorator"""
        # cache format:
        # date : timestamp
        # data : hash {}

        def new_func(cls, param):
            """ Wrapper function"""
            now = time.time()

            try:
                cache = json.load(open(user_c_file, 'r'))

            except (IOError, ValueError):
                cache = {}

            no_cache = True

            if 'date' in cache:
                if now-cache['date'] < ubench.config.MEM_DISK_TTL:
                    no_cache = False

            if no_cache:
                data = {}
                data['date'] = time.time()
                data['data'] = original_func(cls, param)
                json.dump(data, open(user_c_file, 'w'))
                return data['data']

            return cache['data']

        return new_func

    return decorator

class SlurmInterface(object):
    """ Provides methods to execute jobs with slurm scheduler """

    def __init__(self):
        """ Constructor """


    def get_available_nodes(self, slices_size=1):
        """ Returns a list of currently available nodes by slice of slices_size
        ex: for slices of size 4 ['cn[100-103]','cn[109,150-152]']

        Args:
            (int) slices_size: slices size

        Returns:
            (str) list of nodes_id
        """

        cmd_str = "sinfo -h -t IDLE"
        ret_code, stdout, _ = utils.run_cmd(cmd_str, os.getcwd())

        if ret_code:
            print("!!Warning: unclebech was not able to get avaiable nodes")
            return []

        nodeset = NodeSet()

        for line in stdout:
            nodeset_str = re.split(r'\s+', line.strip())[5]
            nodeset.update(nodeset_str)


        split_c = int(len(nodeset)/slices_size)
        nodes_list = [str(ns) for ns in nodeset.split(split_c)]

        return nodes_list


    def get_truncated_nodes_lists(self, nnodes_list, nodes_id):
        """ From a list of nodes number and a list of nodes id returns a list of nodes_id
        truncated according to nodes number

        Args:
            (list of int) nnodes_list: ex [2,4]
            (list of str) nodes_id: ex ['cn[100-104]','cn[50-84]']

        Returns:
            (list of str) truncated node list ex: ['cn[100-101]','cn[50-53]']
        """
        nodes_id_list = []
        for nnode in nnodes_list:
            nodeset = NodeSet()
            nodeset.update(nodes_id)
            if nnode > len(nodeset):
                raise Exception('Number of nodes is greater than the giver number of nodes id')
            nodes_id_list.append(str(nodeset[:nnode]))

        return nodes_id_list


    def get_nnodes_from_string(self, nodes_id):
        """ From a string reprenting a set of nodes returns the number of nodes
        the set contains.

        Args:
            (str) nodes_id: nodes id

        Returns:
            (int) number of nodes
        """

        nodeset = NodeSet(nodes_id)
        return len(nodeset)


    def get_job_info(self, job_id):
        """Return a hash with job information using an id

        Args:
            (int) job_id: job id

        Returns:
            (dictionary) Job information
        """

        job_cmd = ('sacct --jobs={0} -n -p --format=JobName,Elapsed,NodeList,Submit,Start'
                   .format(job_id))

        ret_code, stdout, stderr = utils.run_cmd(job_cmd, os.getcwd())

        if ret_code:
            print("!!Warning: unclebech was not able to get job information")
            print("!!Warning: {}".format(stderr))
            return []

        job_info = []
        for line in stdout:
            fields = line.split("|")

            if not fields or len(fields) < 5:
                continue

            job_name = fields[0]
            job_info_temp = {}
            if job_name != 'batch':
                job_info_temp['job_name'] = job_name
                job_info_temp['job_elasped'] = fields[1]
                job_info_temp['job_nodelist'] = [node for node in NodeSet(fields[2])]
                job_info_temp['job_submit_time'] = fields[3]
                job_info_temp['job_start_time'] = fields[4]
                job_info.append(job_info_temp)

        return job_info

    @memoize_disk('/tmp/ubench_cache')
    def get_jobs_state(self, job_ids=[]):#pylint: disable=dangerous-default-value
        """Return a hash with jobs status using a list of jobs ids"""

        # two commands

        # $ squeue -h -j -o "%.18i %.8T"
        #    175757  RUNNING

        # $ sacct -n --jobs=jobid1.0,jobid2.0 --format=JobId,State
        # 26938.0     COMPLETED
        # 26382.0     COMPLETED

        # Possible states: CANCELLED COMPLETED PENDING RUNNING TIMEOUT

        # { jobid : 'STATE' } => { 12441 : 'RUNNING', 12818 : 'COMPLETED' }

        if not job_ids:
            return {}

        squeue_rex = re.compile(r'^\s+(\d+)\s+(\w+)')
        sacct_rex = re.compile(r'^\s*(\d+)\.0\s+(\w+)')
        squeue_cmd = "squeue -h -j {} -o \"%.18i %.8T\"".format(",".join(job_ids))
        job_ids_0 = [job_id+'.0' for job_id in job_ids]
        sacct_cmd = "sacct -n --jobs={} --format=JobId,State".format(",".join(job_ids_0))
        try_count = 0
        while True:
            job_info = {}

            s_process = Popen(squeue_cmd, cwd=os.getcwd(), shell=True,
                              stdout=PIPE, universal_newlines=True)

            for line in s_process.stdout:
                match = squeue_rex.match(line)
                if match:
                    groups = match.groups()
                    job_info[groups[0]] = groups[1]

            s_process = Popen(sacct_cmd, cwd=os.getcwd(), shell=True,
                              stdout=PIPE, universal_newlines=True)
            for line in s_process.stdout:
                match = sacct_rex.match(line)
                if match:
                    groups = match.groups()
                    job_info[groups[0]] = groups[1]

            # we garantee information for every job
            if len(job_info) == len(job_ids) or try_count > 3:
                break
            else:
                # do not loop forever
                try_count += 1

        return job_info
