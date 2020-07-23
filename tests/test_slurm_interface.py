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
""" Provides test API """

# pylint: disable=unused-import,unused-variable,line-too-long,unused-argument,missing-docstring,superfluous-parens,too-many-arguments
from subprocess import Popen
import os
import time
import json
import hashlib
import ubench.scheduler_interfaces.slurm_interface as slurm_i
from ubench.scheduler_interfaces.slurm_interface import wlist_to_scheduler_wlist
import ubench.config
import fake_data

MOCK_UTILS = ["ubench",
              "utils"]

def delete_cache_file():
    cache_file = '/tmp/ubench_cache-{}'.format(ubench.config.USER)
    os.remove(cache_file)

def mockpopen(args, shell, cwd, env=None, stdout=None, stderr=None, universal_newlines=False):
    """Mock Popen"""
    if 'sinfo' in args:
        return fake_data.MockPopen("sinfo")
    elif 'squeue' in args:
        print('OK')
        return fake_data.MockPopen("squeue")

    return fake_data.MockPopen("sacct")

def test_wlist():
    """Test translation of list of nodes"""

    assert wlist_to_scheduler_wlist(['1', '2', '3']) == [(1, None), (2, None), (3, None)]
    assert wlist_to_scheduler_wlist(['6', 'cn184', 'cn[380,431-433]']) == [(6, None), (1, 'cn184'), (4, 'cn[380,431-433]')]
    assert wlist_to_scheduler_wlist(['6', 'cn184', 'host1']) == [(6, None), (1, 'cn184'), (1, 'host1')]

def test_emptylist():
    """ docstring """
    interface = slurm_i.SlurmInterface()
    assert not interface.get_available_nodes()

def test_available_nodes(mocker):
    """ docstring """

    mock_popen = mocker.patch(".".join(MOCK_UTILS+["Popen"]),
                              side_effect=mockpopen)

    interface = slurm_i.SlurmInterface()
    node_list = interface.get_available_nodes(5)
    assert interface.get_available_nodes()
    assert len(node_list) == 3
    assert node_list[0] == "node[0006-0008,0020-0021]"

def test_job_status(mocker):
    """ docstring """

    mock_popen = mocker.patch("ubench.scheduler_interfaces.slurm_interface.Popen",
                              side_effect=mockpopen)

    interface = slurm_i.SlurmInterface()
    assert interface.get_jobs_state(['111', '222']) == {'175757' : 'RUNNING', '26382': 'COMPLETED', '26938': 'COMPLETED'}
    # assert interface.get_jobs_state(['111', '222']) == {'175757' : 'RUNNING'}
    # time.sleep(10)

def test_job_status_cache(pytestconfig, mocker):
    """ we test memoize_disk decorator"""

    mock_popen = mocker.patch("ubench.scheduler_interfaces.slurm_interface.Popen",
                              side_effect=mockpopen)

    # cache files have a postfix based on the arguments used in the method's call
    md5_id = hashlib.md5(''.join(['222']).encode('utf-8')).hexdigest()
    cache_file = '/tmp/ubench_cache-{}-{}'.format(ubench.config.USER, md5_id)
    # the cache file exist if the test has failed before so we clean
    if os.path.isfile(cache_file):
        os.remove(cache_file)

    # we create a fake cache file:
    expected_results = {"175757": "RUNNING", "26382": "COMPLETED", "26938": "COMPLETED"}
    cache_contets = {'date': time.time(), 'data': expected_results}
    json.dump(cache_contets, open(cache_file, 'w'))

    interface = slurm_i.SlurmInterface()

    # we used cached values no slurm command is executed
    jobs_info = interface.get_jobs_state(['222'])

    assert not mock_popen.called
    assert jobs_info == expected_results

    # we invalidate cache
    cache = {'date': time.time()-1000}
    json.dump(cache, open(cache_file, 'w'))
    jobs_info = interface.get_jobs_state(['111', '222'])
    # slurm command has been executed
    assert mock_popen.called
    