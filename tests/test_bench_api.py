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

# pylint: disable=import-error, unused-import, wrong-import-order, ungrouped-imports

import os
import lxml.etree as ET
from ubench.benchmarking_tools_interfaces.jube_benchmarking_api import JubeBenchmarkingAPI
import ubench.core.fetcher as fetcher
import ubench.core.ubench_commands as ubench_commands
import ubench.benchmark_managers.jube_benchmark_manager as jbm
import time
from subprocess import Popen


def test_init():
    """ docstring """
    benchmarking_api = JubeBenchmarkingAPI("", "")
    assert isinstance(benchmarking_api.benchmark_path, str)
    assert benchmarking_api.benchmark == ""


def test_bench_m():
    """ docstring """

    # pylint: disable=unused-variable
    bench = jbm.JubeBenchmarkManager("simple", "")


# def test_benchmark_no_exist(init_env):
#     """ docstring """

#     # pylint: disable=redefined-outer-name, unused-argument, unused-variable
#     uconf = uconfig.UbenchConfig()
#     with pytest.raises(OSError):
#         benchmarking_api = jba.JubeBenchmarkingAPI("bench_name", "", uconf)


# def test_benchmark_empty(init_env):
#     """ docstring """

#     # pylint: disable=unused-variable, redefined-outer-name, no-member

#     init_env.create_empty_bench()
#     with pytest.raises(ET.ParseError):
#         benchmarking_api = jba.JubeBenchmarkingAPI("test_bench", "")


def test_load_bench_file():
    """ docstring """

    # pylint: disable=unused-variable
    benchmarking_api = JubeBenchmarkingAPI("simple", "")


def test_out_xml_path(init_env):
    """ docstring """

    # pylint: disable=superfluous-parens, redefined-outer-name
    benchmarking_api = JubeBenchmarkingAPI("simple", "")
    assert benchmarking_api.jube_files.bench_xml_path_out == os.path.join(
        init_env.config['run_path'], "simple")


def test_xml_get_result_file(init_env):
    """ docstring """
    # pylint: disable=redefined-outer-name, unused-argument
    benchmarking_api = JubeBenchmarkingAPI("simple", "")
    assert benchmarking_api.jube_files.get_bench_resultfile(
    ) == "result.dat"


def test_write_bench_xml(init_env):
    """ docstring """

    # pylint: disable=redefined-outer-name, singleton-comparison
    benchmarking_api = JubeBenchmarkingAPI("simple", "")
    init_env.create_run_dir("simple", "")
    benchmarking_api.jube_files.write_bench_xml()
    assert os.path.exists(os.path.join(init_env.config['run_path'],
                                       "simple")) == True


def test_custom_nodes(init_env):
    """ docstring """

    # pylint: disable=redefined-outer-name, no-member,c-extension-no-member,protected-access
    benchmarking_api = JubeBenchmarkingAPI("simple", "")

    benchmarking_api._set_custom_nodes([(1, 'cn050'), (2, 'cn[103-107,145]')])
    benchmarking_api.jube_files.write_bench_xml()
    xml_file = ET.parse(
        os.path.join(init_env.config['run_path'], "simple/simple.xml"))
    benchmark = xml_file.find('benchmark')
    assert benchmark.findall("parameterset[@name='custom_parameter']")


def test_result_custom_nodes(init_env):
    """ docstring """

    # pylint: disable=redefined-outer-name, no-member,c-extension-no-member,protected-access
    benchmarking_api = JubeBenchmarkingAPI("simple", "")
    benchmarking_api._set_custom_nodes([(1, 'cn050'), (2, 'cn[103-107,145]')])
    benchmarking_api.jube_files.write_bench_xml()
    xml_file = ET.parse(
        os.path.join(init_env.config['run_path'], "simple/simple.xml"))
    benchmark = xml_file.find('benchmark')
    table = benchmark.find('result').find('table')
    result = [
        column for column in table.findall('column')
        if column.text == 'custom_nodes_id'
    ]
    assert result


def test_custom_nodes_not_in_result(init_env):
    """ docstring """

    # pylint: disable=redefined-outer-name, no-member,c-extension-no-member
    benchmarking_api = JubeBenchmarkingAPI("simple", "")
    benchmarking_api.set_custom_nodes([1, 2], None)
    benchmarking_api.jube_files.write_bench_xml()
    xml_file = ET.parse(
        os.path.join(init_env.config['run_path'], "simple/simple.xml"))
    benchmark = xml_file.find('benchmark')
    table = benchmark.find('result').find('table')
    for column in table.findall('column'):
        assert column.text != 'custom_nodes_id'


def test_add_bench_input():
    """ docstring """

    # pylint: disable=unused-variable

    #check _revision prefix are coherent
    benchmarking_api = JubeBenchmarkingAPI("simple", "")
    bench_input = benchmarking_api.jube_files.add_bench_input()
    multisource = benchmarking_api.jube_files.get_bench_multisource()
    max_files = max([len(source['files']) for source in multisource])
    bench_xml = benchmarking_api.jube_files.bench_xml['simple.xml']
    benchmark = bench_xml.find('benchmark')
    assert benchmark.findall("parameterset[@name='ubench_config']")
    bench_config = benchmark.find("parameterset[@name='ubench_config']")
    assert bench_config.findall("parameter[@name='stretch']")
    assert bench_config.findall("parameter[@name='stretch_id']")
    # assert len(bench_config.findall("parameter[@name='input']")) > 0
    # assert len(bench_config.findall("parameter[@name='input_id']")) > 0
    simple_code_count = 0
    input_count = 0
    for param in bench_config.findall("parameter"):
        if "simple_code_revision" in param.text:
            simple_code_count += 1
        if "input_revision" in param.text:
            input_count += 1
    assert simple_code_count < max_files
    assert input_count < max_files


def test_fetcher_dir_rev(mocker, init_env):
    """ docstring """
    # pylint: disable=redefined-outer-name, unused-argument, unused-variable

    scms = [{
        'type': 'svn',
        'url': 'svn://toto.fr/trunk',
        'revisions': ['20'],
        'files': ['file1', 'file2']
    }, {
        'type': 'git',
        'url': 'https://toto.fr/git-repo',
        'revisions': ['e2be38ed38e4'],
        'files': ['git-repo']
    }]

    def mocksubpopen(args, shell, cwd, universal_newlines=False):
        """ docstring """

        # simulating directory creation by scms
        for scm in scms:
            for rev in scm['revisions']:
                for f in scm['files']:  # pylint: disable=invalid-name
                    path = os.path.join(cwd, f)
                    if not os.path.exists(path):
                        os.makedirs(path)
        return Popen("date")

    mock_popen = mocker.patch("ubench.core.fetcher.Popen",
                              side_effect=mocksubpopen)
    mock_credentials = mocker.patch(
        "ubench.core.fetcher.Fetcher.get_credentials")
    fetch_bench = fetcher.Fetcher(
        resource_dir=init_env.config['resources_path'],
        benchmark_name='simple')
    for scm in scms:
        fetch_bench.scm_fetch(scm['url'], scm['files'], scm['type'],
                              scm['revisions'])
        for rev in scm['revisions']:
            assert os.path.exists(
                os.path.join(init_env.config['resources_path'], 'simple',
                             scm['type'], rev))
            assert os.path.exists(
                os.path.join(init_env.config['resources_path'], 'simple',
                             scm['type'],
                             rev + "_" + os.path.basename(scm['files'][0])))

    assert mock_popen.call_count == 2
    # it creates directory


def test_fetcher_cmd(mocker, init_env):
    """ docstring """
    # pylint: disable=redefined-outer-name, unused-variable

    scm = {
        'type': 'svn',
        'url': 'svn://toto.fr/trunk',
        'revisions': ['20'],
        'files': ['file1']
    }
    mock_popen = mocker.patch("ubench.core.fetcher.Popen")
    mock_credentials = mocker.patch(
        "ubench.core.fetcher.Fetcher.get_credentials")
    fetch_bench = fetcher.Fetcher(
        resource_dir=init_env.config['resources_path'],
        benchmark_name='simple')
    fetch_bench.scm_fetch(scm['url'], scm['files'], scm['type'],
                          scm['revisions'])
    username = os.getlogin()
    fetch_command = "svn export -r {0} {1}/{2} {2} --username {3} --password '' ".format(
        scm['revisions'][0], scm['url'], scm['files'][0], username)
    fetch_command += "--trust-server-cert --non-interactive --no-auth-cache"
    mock_popen.assert_called_with(fetch_command,
                                  cwd=os.path.join(
                                      init_env.config['resources_path'],
                                      'simple', 'svn', scm['revisions'][0]),
                                  shell=True, universal_newlines=True)


def test_fetcher_cmd_no_revision(mocker, init_env):
    """ docstring """

    # pylint: disable=redefined-outer-name, unused-variable

    scm = {
        'type': 'svn',
        'url': 'svn://toto.fr/trunk',
        'revisions': ['20'],
        'files': ['file1']
    }
    mock_popen = mocker.patch("ubench.core.fetcher.Popen")
    mock_credentials = mocker.patch(
        "ubench.core.fetcher.Fetcher.get_credentials")
    fetch_bench = fetcher.Fetcher(
        resource_dir=init_env.config['resources_path'],
        benchmark_name='simple')
    fetch_bench.scm_fetch(scm['url'], scm['files'], scm['type'], [''], None,
                          None)
    username = os.getlogin()
    fetch_command = "svn export {0}/{1} {1} --username {2} --password '' ".format(
        scm['url'], scm['files'][0], username)
    fetch_command += "--trust-server-cert --non-interactive --no-auth-cache"
    mock_popen.assert_called_with(fetch_command,
                                  cwd=os.path.join(
                                      init_env.config['resources_path'],
                                      'simple', 'svn'),
                                  shell=True, universal_newlines=True)


def test_run_customp(monkeypatch, init_env):
    """ docstring """
    # pylint: disable=missing-docstring, unused-argument, unused-variable, redefined-outer-name, undefined-variable

    def mock_auto_bm_init(self, bench_dir, run_dir, benchmark_list):
        return True

    def mock_auto_bm_bench(self, name):
        return bm.BenchmarkManager("simple", "")

    def mock_bm_run_bench(self, opt_dict):
        return True

    monkeypatch.setattr(
        "ubench.benchmark_managers.standard_benchmark_manager.StandardBenchmarkManager.run",
        mock_bm_run_bench)
    ubench_cmd = ubench_commands.UbenchCmd("", ["simple"])
    ubench_cmd.run(
        {'customp_list':
         ["param:new_value", "argexec:'PingPong -npmin 56 msglog 1:18'"],
         'w':
         "host1",
         'file_params' : None,
         'custom_params': None}
    )

# def test_extract_job_id(init_env):
#     """ docstring """
#     # init_env.create_run_dir("simple")
#     benchmarking_api = JubeBenchmarkingAPI("simple", "")
#     id_dir = os.path.join(init_env.config['run_path'],
#                           'simple',
#                           'benchmark_runs',
#                           '0000000')

#     assert benchmarking_api.extract_job_ids(id_dir) == ['617222', '617221']

def tests_run_parallel(init_env):
    init_env.create_run_dir("simple", "l470")
    init_env.create_resource_bench("simple")
    bench_api = JubeBenchmarkingAPI("simple", "l470")

    bench_api.run({'custom_params' : None,
                   'execute' : False,
                   'w' : [],
                   'test' : True})

    bench_api.run({'custom_params' : None,
                   'execute' : False,
                   'w' : [],
                   'test' : True})

def tests_run_wait(init_env):
    init_env.create_run_dir("simple", "l470")
    init_env.create_resource_bench("simple")
    bench_api = JubeBenchmarkingAPI("simple", "l470")
    jube_job, _ = bench_api.run({'custom_params' : None,
                                 'execute' : False,
                                 'w' : [],
                                 'test' : True})

    while jube_job.jube_returncode is None:
        time.sleep(1)

    assert jube_job.jube_returncode == 0

# def tests_run_kill(init_env):
#     init_env.create_run_dir("simple", "l470")
#     init_env.create_resource_bench("simple")
#     bench_api = JubeBenchmarkingAPI("simple", "l470")

#     jube_job, _ = bench_api.run({'custom_params' : None,
#                                  'execute' : False,
#                                  'w' : [],
#                                  'test' : True})
#     # import pdb;pdb.set_trace()


#     time.sleep(1)
#     jube_job.kill()

#     assert jube_job.jube_returncode == None
