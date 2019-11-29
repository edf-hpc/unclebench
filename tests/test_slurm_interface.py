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
import pytest
import mock
import pytest_mock
import ubench.scheduler_interfaces.slurm_interface as slurm_i
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
    """ docstring """

    mock_popen = mocker.patch("ubench.scheduler_interfaces.slurm_interface.Popen",
                              side_effect=mockpopen)

    interface = slurm_i.SlurmInterface()
    jobs_info = interface.get_jobs_state(['222'])
    exp_cmd = 'sacct -n --jobs=111.0,222.0 --format=JobId,State'
    repository_root = os.path.join(pytestconfig.rootdir.dirname,
                                   pytestconfig.rootdir.basename)

    # we used cached values no commmand is called
    assert not mock_popen.called
    # we load cached results
    assert jobs_info == {'175757' : 'RUNNING', '26382': 'COMPLETED', '26938': 'COMPLETED'}
    # we assert if cache file has been created
    cache_file = '/tmp/ubench_cache-{}'.format(ubench.config.USER)
    assert os.path.isfile(cache_file)
    # # we invalidate cache
    cache = {'date': time.time()-1000}
    json.dump(cache, open(cache_file, 'w'))
    jobs_info = interface.get_jobs_state(['111', '222'])
    exp_cmd = 'sacct -n --jobs=111.0,222.0 --format=JobId,State'
    repository_root = os.path.join(pytestconfig.rootdir.dirname,
                                   pytestconfig.rootdir.basename)
    # we dont use cache
    mock_popen.assert_called_with(exp_cmd, cwd=repository_root,
                                  shell=True, stdout=-1, universal_newlines=True)

    assert interface.get_jobs_state(['111', '222']) == {'175757' : 'RUNNING', '26382': 'COMPLETED', '26938': 'COMPLETED'}
    delete_cache_file()
