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
# pylint: disable=no-self-use
""" Provides SlurmInterface class"""


import os
from subprocess import Popen, PIPE
from ClusterShell.NodeSet import NodeSet
import pyslurm  # pylint: disable=import-error


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

        node_list = []
        a = pyslurm.node()  # pylint: disable=invalid-name
        node_dict = a.get()
        node_count = 0
        nodeset = NodeSet()

        if len(node_dict) > 0:
            for key, value in sorted(node_dict.items()):

                if value['state'] == 'IDLE':
                    nodetype = value  # pylint: disable=unused-variable
                    nodeset.update(key)
                    node_count += 1

                if node_count == slices_size:
                    node_list.append(str(nodeset))
                    nodeset = NodeSet()
                    slice_str = None  # pylint: disable=unused-variable
                    node_count = 0

        return node_list


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

        job_process = Popen(job_cmd, cwd=os.getcwd(), shell=True,
                            stdout=PIPE, universal_newlines=True)
        job_info = []
        for line in job_process.stdout:
            fields = line.split("|")
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
