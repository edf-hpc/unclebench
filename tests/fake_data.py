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
# pylint: disable=no-self-use,unused-argument,no-init,old-style-class,missing-docstring,too-few-public-methods
""" Provides fake data and clases for test purposes """

import collections
import random

UConf = collections.namedtuple('Uconf', 'resource_dir run_dir benchmark_dir platform_dir')
JubeRun = collections.namedtuple('JubeRun', 'result_path jubeid')

def gen_jubeinfo_output():
    # generate jube info output
    head, param, field_names, line = "", "", "", ""
    mock_vars = []
    for i in range(0, 10):
        mock_v = {'id' : i,
                  'host' : "host{}".format(i),
                  'mpi_version': "OpenMPI-{}".format(i),
                  'nodes': i % 5 + 1,
                  'modules': "openmpi/{}".format(i),
                  'p_pat_min': 10*i-i,
                  'p_pat_avg': 10*i,
                  'p_pat_max': 10*i+1}

        mock_vars.append(mock_v)

    order_ids = [4, 1, 3, 6, 5, 3, 2, 7, 0, 8, 9]

    # generates old version
    with open("data/jube_info_head.txt", 'r') as f:
        head = f.read()

    with open("data/jube_info_template.txt", 'r') as f:
        param = f.read()

    with open("data/mock_jube_info.txt", 'w') as f:
        f.write(head)
        for i in order_ids:
            val = param.format(mock_vars[i]['id'],
                               str(mock_vars[i]['id']).zfill(6),
                               mock_vars[i]['host'],
                               mock_vars[i]['mpi_version'],
                               mock_vars[i]['nodes'],
                               mock_vars[i]['modules'])
            f.write(val)
            f.write('\n')

    # generates new version
    with open("data/jube_info_csv_fieldnames.csv", 'r') as f:
        field_names = f.read()

    with open("data/jube_info_csv_template.csv", 'r') as f:
        line = f.read()

    with open("data/mock_jube_info.cvs", 'w') as f:
        f.write(field_names)
        for i in order_ids:
            val = line.format(mock_vars[i]['id'],
                              str(mock_vars[i]['id']).zfill(6),
                              mock_vars[i]['host'],
                              mock_vars[i]['mpi_version'],
                              mock_vars[i]['nodes'],
                              mock_vars[i]['modules'])
            f.write(val)

    # generate_results_data
    with open("data/mock_data_results.dat", 'w') as f:
        f.write("nodes,host_p,comp_version,mpi_version,p_pat_min,p_pat_avg,p_pat_max\n")
        for i in sorted(order_ids):
            f.write("{},{},{},{},{},{},{}\n".format(mock_vars[i]['nodes'],
                                                    mock_vars[i]['host'],
                                                    "gnu",
                                                    mock_vars[i]['mpi_version'],
                                                    mock_vars[i]['p_pat_min'],
                                                    mock_vars[i]['p_pat_avg'],
                                                    mock_vars[i]['p_pat_max']))





def get_mock_jube_file():
    # return open("tests/data/mock_jube_info.txt", 'r')
    return open("tests/data/mock_jube_info.cvs", 'r')

def get_results_file(f_name, mode=None):
    if 'dat' in f_name:
        return open("tests/data/mock_data_results.dat", 'r')
    if 'stdout' in f_name:
        #return empty file
        open('/tmp/job_info', 'a').close()
        return open("/tmp/job_info", 'r')
    if 'ubench.log' in f_name:
        return open("tests/data/ubench.log", 'r')

    return open("/tmp/bench_results.yaml", mode)

class MockPopen(object):
    """Fakes slurm commands """

    def __init__(self, cmd):
        self.cmd = cmd
        self.returncode = None

    # pylint: disable=R0201
    def wait(self):
        """ docstring """
        return 0

    def poll(self):
        """ docstring """
        return None

    # pylint: disable=R0201
    def communicate(self):
        """fake communicate Popen method
        We return a string as stdout"""
        return "\n".join(self.stdout), ""

    @property
    def stdout(self):
        """ docstring """
        if self.cmd == "sinfo":
            return ["node\tup\tinfinite\t16\tidle node[0006-0008,0020-0031]"]
        elif self.cmd == "squeue":
            return ["   175757  RUNNING"]
        elif self.cmd == "sacct":
            return [" 26938.0     COMPLETED", " 26382.0     COMPLETED"]

        elif self.cmd == "juberun":
            return ["######################################################################  ",
                    "# benchmark: simple",
                    "#                  ",
                    "#                  ",
                    "######################################################################  ",
                    "",
                    "stepname | all | open | wait | error | done",
                    "---------+-----+------+------+-------+-----",
                    "execute |   1 |    0 |    0 |     0 |    1",
                    " ",
                    ">>>> Benchmark information and further useful commands:",
                    ">>>>       id: 2",
                    ">>>>   handle: benchmark_runs",
                    ">>>>      dir: benchmark_runs/000002",
                    ">>>>  analyse: jube analyse benchmark_runs --id 2",
                    ">>>>   result: jube result benchmark_runs --id 2",
                    ">>>>     info: jube info benchmark_runs --id 2",
                    ">>>>      log: jube log benchmark_runs --id 2",
                    "#####################################################################"]

        elif self.cmd == "jubeanalyse":
            return ["######################################################################",
                    "# Analyse benchmark simple id: 1",
                    "######################################################################",
                    ">>> Start analyse",
                    ">>> Analyse finished",
                    ">>> Analyse data storage: benchmark_runs/000001/analyse.xml",
                    "######################################################################"]

        return [""]



class FakeAPI:
    """Fakes benchmark API"""

    def run(self, opts):
        return JubeRun('/tmp', 0), {}

    def _set_custom_nodes(self, nnodes, nodes):
        return True

class FakeAPI2:

    def __init__(self, benchmark, platform):
        self.benchmark = benchmark
    def run(self, opts):
        return FakeJubeRun(self.benchmark), {}

    def result(self):
        return True

class FakeJubeRun:
    """Fakes JubeRun Class"""
    def __init__(self, benchmark):
        self.benchmark = benchmark
        self._returncode = None
        self._job_prefix = str(sum(ord(c) for c in benchmark))
        self._job_ids = []
        self._exec_dir = {}

    @property
    def jube_returncode(self):

        if self._returncode is None:
            self._returncode = [None, None, None, 0][random.randint(0, 100) % 4]
        return self._returncode

    @property
    def job_ids(self):
        """ Returns the jobs id associated to a JubeRun"""
        if not self._job_ids:
            if self._returncode == 0:
                num = random.randint(1, 4)
                for _ in range(0, num):
                    fake_job_id = self._job_prefix + str(random.randint(0, 100))
                    self._job_ids.append(fake_job_id)

        return self._job_ids

    @property
    def exec_dir(self):
        if not self._exec_dir:
            for index, value in enumerate(self.job_ids):
                jube_exec_dir = "exec_{}".format(str(index).zfill(6))
                self._exec_dir[jube_exec_dir] = value
        return self._exec_dir


class FakeSlurm:

    def __init__(self):
        self.jobs = {}

    def get_jobs_state(self, job_ids):
        for job in job_ids:
            if job in job_ids:
                state = self.jobs.get(job, "RUNNING")
                if state != "COMPLETED":
                    self.jobs[job] = ["COMPLETED", "RUNNING", "RUNNING", "RUNNING"][random.randint(0, 100) % 4]

        return {job_n: job_s for job_n, job_s in self.jobs.items() if job_n in job_ids}

class FakeXML:

    def load_platform_xml(self, platform):
        return True

    def get_bench_outputdir(self):
        return "benchmark_runs"

    def add_bench_input(self):
        return True

    def remove_multisource(self):
        return True

    def write_bench_xml(self):
        return True

    def write_platform_xml(self):
        return True

    def get_platform_dir(self):
        return ""

    def delete_platform_dir(self):
        return True

    def set_platform_path(self, platform_path):
        return True
