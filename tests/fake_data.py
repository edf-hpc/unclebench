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

UConf = collections.namedtuple('Uconf', 'resource_dir run_dir benchmark_dir platform_dir')
JubeRun = collections.namedtuple('JubeRun', 'result_path jubeid')

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
