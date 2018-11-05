# import py
import pytest
import mock
import pytest_mock
import tempbench
import os
import xml.etree.ElementTree as ET
import ubench.benchmarking_tools_interfaces.jube_benchmarking_api as jba
import ubench.benchmarking_tools_interfaces.jube_xml_parser as j_xml
import ubench.core.fetcher as fetcher
import subprocess
import ubench.core.ubench_commands as ubench_commands
import ubench.benchmark_managers.jube_benchmark_manager as jbm
import ubench.core.ubench_config as uconfig
import time

from subprocess import Popen
@pytest.fixture(scope="module")
def init_env():
  config = {}
  config['main_path'] = "/tmp/ubench_pytest/"
  repository_root= os.path.join(pytest.config.rootdir.dirname,pytest.config.rootdir.basename)
  os.environ["UBENCH_BENCHMARK_DIR"] = os.path.join(config['main_path'],'benchmarks')
  os.environ["UBENCH_PLATFORM_DIR"] = os.path.join(repository_root,'platform')
  os.environ["UBENCH_PLUGIN_DIR"] = os.path.join(repository_root,'ubench/plugins')
  test_env = tempbench.Tempbench(config,repository_root)
  test_env.copy_files()
  os.environ["UBENCH_RUN_DIR_BENCH"] = test_env.config['run_path']
  os.environ["UBENCH_RESOURCE_DIR"] = test_env.config['resources_path']
  yield test_env
  test_env.destroy_dir_structure()

# def test_xml(init_env):
#   benchs_files = [init_env.config['bench_path']+'/simple/simple.xml']
#   uconf=uconfig.UbenchConfig()
#   jube_xml_files = j_xml.JubeXMLParser(init_env.config['bench_path']+'/simple/',benchs_files,init_env.config['bench_path'],uconf.platform_dir)
#   assert len(jube_xml_files.get_dirs(uconf.platform_dir)) == 2

def test_init():

  benchmarking_api=jba.JubeBenchmarkingAPI("","")
  assert isinstance(benchmarking_api.benchmark_path,str)
  assert benchmarking_api.benchmark_name == ""

def test_bench_m():
  uconf = uconfig.UbenchConfig()
  bench = jbm.JubeBenchmarkManager("simple","",uconf)

def test_benchmark_no_exist(init_env):
  with pytest.raises(OSError):
    benchmarking_api=jba.JubeBenchmarkingAPI("bench_name","")

def test_benchmark_empty(init_env):
  init_env.create_empty_bench()
  with pytest.raises(ET.ParseError):
    benchmarking_api=jba.JubeBenchmarkingAPI("test_bench","")

def test_load_bench_file():
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")

def test_out_xml_path(init_env):
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  print init_env.config['run_path']
  assert benchmarking_api.jube_xml_files.bench_xml_path_out == os.path.join(init_env.config['run_path'],"simple")

def test_xml_get_result_file(init_env):
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  assert benchmarking_api.jube_xml_files.get_bench_resultfile() == "result.dat"

def test_write_bench_xml(init_env):
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  init_env.create_run_dir("simple")
  benchmarking_api.jube_xml_files.write_bench_xml()
  assert os.path.exists(os.path.join(init_env.config['run_path'],"simple")) == True

def test_custom_nodes(init_env):
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  benchmarking_api.set_custom_nodes([1,2],['cn050','cn[103-107,145]'])
  benchmarking_api.jube_xml_files.write_bench_xml()
  xml_file = ET.parse(os.path.join(init_env.config['run_path'],"simple/simple.xml"))
  benchmark = xml_file.find('benchmark')
  assert len(benchmark.findall("parameterset[@name='custom_parameter']")) > 0

def test_result_custom_nodes(init_env):
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  benchmarking_api.set_custom_nodes([1,2],['cn050','cn[103-107,145]'])
  benchmarking_api.jube_xml_files.write_bench_xml()
  xml_file = ET.parse(os.path.join(init_env.config['run_path'],"simple/simple.xml"))
  benchmark = xml_file.find('benchmark')
  table = benchmark.find('result').find('table')
  result  = [column for column in table.findall('column')  if column.text == 'custom_nodes_id']
  assert len(result) > 0

def test_custom_nodes_not_in_result(init_env):
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  benchmarking_api.set_custom_nodes([1,2],None)
  benchmarking_api.jube_xml_files.write_bench_xml()
  xml_file = ET.parse(os.path.join(init_env.config['run_path'],"simple/simple.xml"))
  benchmark = xml_file.find('benchmark')
  table = benchmark.find('result').find('table')
  for column in table.findall('column'):
    assert column.text != 'custom_nodes_id'

# def test_get_bench_multisource_svn():
#   benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
#   multisource = benchmarking_api.jube_xml_files.get_bench_multisource()
#   gen_config = benchmarking_api.jube_xml_files.gen_bench_config()
#   assert len(multisource) > 0
#   for source in multisource:
#     assert source['protocol'] == 'svn'
#   for source in multisource:
#     assert gen_config['svn'].has_key(source['name'])

# def test_get_bench_multisource_git():
#   benchmarking_api=jba.JubeBenchmarkingAPI("simple_git","")
#   multisource = benchmarking_api.jube_xml_files.get_bench_multisource()
#   gen_config = benchmarking_api.jube_xml_files.gen_bench_config()
#   assert len(multisource) > 0
#   for source in multisource:
#     assert source['protocol'] == 'git'
#   for source in multisource:
#     assert gen_config['git'].has_key(source['name'])



def test_add_bench_input():
  #check _revision prefix are coherent
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  bench_input = benchmarking_api.jube_xml_files.add_bench_input()
  multisource = benchmarking_api.jube_xml_files.get_bench_multisource()
  max_files = max([len(source['files']) for source in multisource])
  bench_xml = benchmarking_api.jube_xml_files.bench_xml['simple.xml']
  benchmark = bench_xml.find('benchmark')
  assert len(benchmark.findall("parameterset[@name='ubench_config']")) > 0
  bench_config = benchmark.find("parameterset[@name='ubench_config']")
  assert len(bench_config.findall("parameter[@name='stretch']")) > 0
  assert len(bench_config.findall("parameter[@name='stretch_id']")) > 0
  # assert len(bench_config.findall("parameter[@name='input']")) > 0
  # assert len(bench_config.findall("parameter[@name='input_id']")) > 0
  simple_code_count = 0
  input_count = 0
  for param in bench_config.findall("parameter"):
    if "simple_code_revision" in param.text:
      simple_code_count +=1
    if "input_revision" in param.text:
      input_count +=1
  assert simple_code_count < max_files
  assert input_count < max_files



def test_fetcher_dir_rev(mocker,init_env):
  # Test directory creation for each revision
  # if you want to test real repo: svn://scm.gforge.inria.fr/svnroot/darshan-ruby/trunk,  https://github.com/poelzi/git-clone-test
  scms = [
    {'type': 'svn','url' : 'svn://toto.fr/trunk','revisions': ['20'],'files': ['file1','file2']},
          {'type': 'git','url' : 'https://toto.fr/git-repo','revisions': ['e2be38ed38e4'],'files': ['git-repo']}]

  def mocksubpopen(args,shell,cwd):
    # simulating directory creation by scms
    for scm in scms:
      for rev in scm['revisions']:
        for f in scm['files']:
          path = os.path.join(cwd,f)
          if not os.path.exists(path):
            os.makedirs(path)
    return Popen("date")

  mock_popen = mocker.patch("ubench.core.fetcher.Popen",side_effect=mocksubpopen)
  mock_credentials = mocker.patch("ubench.core.fetcher.Fetcher.get_credentials")
  fetch_bench = fetcher.Fetcher(resource_dir=init_env.config['resources_path'],benchmark_name='simple')
  for scm in scms:
    fetch_bench.scm_fetch(scm['url'],scm['files'],scm['type'],scm['revisions'])
    for rev in scm['revisions']:
      assert os.path.exists(os.path.join(init_env.config['resources_path'],'simple',scm['type'],rev))
      assert os.path.exists(os.path.join(init_env.config['resources_path'],'simple',scm['type'],rev + "_"+os.path.basename(scm['files'][0])))

  # assert mock_popen.call_count > 2
  # it creates directory

def test_fetcher_cmd(mocker,init_env):
  scm = {'type': 'svn','url' : 'svn://toto.fr/trunk','revisions': ['20'],'files': ['file1']}
  mock_popen = mocker.patch("ubench.core.fetcher.Popen")
  mock_credentials = mocker.patch("ubench.core.fetcher.Fetcher.get_credentials")
  fetch_bench = fetcher.Fetcher(resource_dir=init_env.config['resources_path'],benchmark_name='simple')
  fetch_bench.scm_fetch(scm['url'],scm['files'],scm['type'],scm['revisions'])
  username = os.getlogin()
  fetch_command = "svn export -r {0} {1}/{2} {2} --username {3} --password '' ".format(scm['revisions'][0],scm['url'],scm['files'][0],username)
  fetch_command += "--trust-server-cert --non-interactive --no-auth-cache"
  mock_popen.assert_called_with(fetch_command,cwd=os.path.join(init_env.config['resources_path'],'simple','svn',scm['revisions'][0]) , shell=True)

def test_fetcher_cmd_no_revision(mocker,init_env):
  scm = {'type': 'svn','url' : 'svn://toto.fr/trunk','revisions': ['20'],'files': ['file1']}
  mock_popen = mocker.patch("ubench.core.fetcher.Popen")
  mock_credentials = mocker.patch("ubench.core.fetcher.Fetcher.get_credentials")
  fetch_bench = fetcher.Fetcher(resource_dir=init_env.config['resources_path'],benchmark_name='simple')
  fetch_bench.scm_fetch(scm['url'],scm['files'],scm['type'],None,None,None)
  username = os.getlogin()
  fetch_command = "svn export {0}/{1} {1} --username {2} --password '' ".format(scm['url'],scm['files'][0],username)
  fetch_command += "--trust-server-cert --non-interactive --no-auth-cache"
  mock_popen.assert_called_with(fetch_command,cwd=os.path.join(init_env.config['resources_path'],'simple','svn') , shell=True)


def test_run_customp(monkeypatch,init_env):

  # Test complex paramaters with customp
  def mock_auto_bm_init(self,bench_dir,run_dir,benchmark_list):
    return True

  def mock_auto_bm_bench(self,name):
    return bm.BenchmarkManager("simple","")

  def mock_bm_set_param(self,params):
    # if params['param'] != 'new_value':
    if params['argexec'] != "'PingPong -npmin 56 msglog 1:18'":
      raise NameError('param error')
    return True

  def mock_bm_run_bench(self,platform,opt_dict):
    return True

  monkeypatch.setattr("ubench.benchmark_managers.standard_benchmark_manager.StandardBenchmarkManager.set_parameter",mock_bm_set_param)
  monkeypatch.setattr("ubench.benchmark_managers.standard_benchmark_manager.StandardBenchmarkManager.run",mock_bm_run_bench)
  ubench_cmd = ubench_commands.UbenchCmd("",["simple"])
  ubench_cmd.run({'customp_list': ["param:new_value","argexec:'PingPong -npmin 56 msglog 1:18'"],'w_list' : "host1"})
