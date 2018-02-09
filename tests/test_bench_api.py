# import py
import pytest
import tempbench
import os
import xml.etree.ElementTree as ET
import ubench.benchmarking_tools_interfaces.jube_benchmarking_api as jba
import ubench.benchmarking_tools_interfaces.jube_xml_parser as j_xml
import ubench.core.fetcher as fetcher
import subprocess
import ubench.core.ubench_commands as ubench_commands
import ubench.benchmark_managers.benchmark_manager as bm
import ubench.core.ubench_config as uconfig
import time

@pytest.fixture(scope="module")
def init_env():
  config = {}
  config['main_path'] = "/tmp/ubench_pytest/"
  os.environ["UBENCH_BENCHMARK_DIR"] = os.path.join(config['main_path'],'benchmarks')
  test_env = tempbench.Tempbench(config);
  test_env.copy_files()
  os.environ["UBENCH_RUN_DIR_BENCH"] = test_env.config['run_path']
  yield test_env
  test_env.destroy_dir_structure()

def test_xml(init_env):
  benchs_files = [init_env.config['bench_path']+'/simple/simple.xml']
  uconf=uconfig.UbenchConfig()
  jube_xml_files = j_xml.JubeXMLParser(init_env.config['bench_path']+'/simple/',benchs_files,init_env.config['bench_path'],uconf.platform_dir)
  assert len(jube_xml_files.get_dirs(uconf.platform_dir)) < 2

def test_init():

  benchmarking_api=jba.JubeBenchmarkingAPI("","")
  assert isinstance(benchmarking_api.benchmark_path,str)
  assert benchmarking_api.benchmark_name == ""

def test_bench_m():
  bench = bm.BenchmarkManager("simple","")

def test_benchmark_no_exist(init_env):

  with pytest.raises(OSError):
    benchmarking_api=jba.JubeBenchmarkingAPI("bench_name","")

def test_benchmark_empty():
  with pytest.raises(ET.ParseError):
    benchmarking_api=jba.JubeBenchmarkingAPI("test_bench","")

def test_load_bench_file():
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")

def test_out_xml_path(init_env):
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  print init_env.config['run_path']
  assert benchmarking_api.jube_xml_files.bench_xml_path_out == os.path.join(init_env.config['run_path'],"simple")

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
  benchmarking_api.set_custom_nodes([1,2],[None,None])
  benchmarking_api.jube_xml_files.write_bench_xml()
  xml_file = ET.parse(os.path.join(init_env.config['run_path'],"simple/simple.xml"))
  benchmark = xml_file.find('benchmark')
  table = benchmark.find('result').find('table')
  for column in table.findall('column'):
    assert column.text != 'custom_nodes_id'

def test_get_bench_multisource():
  benchmarking_api=jba.JubeBenchmarkingAPI("simple","")
  multisource = benchmarking_api.jube_xml_files.get_bench_multisource()
  source_1 = multisource[0]
  assert len(multisource) > 0
  assert source_1['protocol'] == 'svn'

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
  assert len(bench_config.findall("parameter[@name='simple_code']")) > 0
  assert len(bench_config.findall("parameter[@name='simple_code_id']")) > 0
  assert len(bench_config.findall("parameter[@name='input']")) > 0
  assert len(bench_config.findall("parameter[@name='input_id']")) > 0
  simple_code_count = 0
  input_count = 0
  for param in bench_config.findall("parameter"):
    if "simple_code_revision" in param.text:
      simple_code_count +=1
    if "input_revision" in param.text:
      input_count +=1
  assert simple_code_count < max_files
  assert input_count < max_files

# def test_fetcher(monkeypatch,init_env):
#   def mocksvncmd(self):
#     svn_dir = os.path.join(init_env.config['resources_path'],'svn')
#     if not os.path.exists(svn_dir):
#       os.makedirs(svn_dir)
#     return True
#   def mockcredentials(self):
#     return True

#   monkeypatch.setattr("subprocess.Popen.communicate", mocksvncmd)
#   monkeypatch.setattr("ubench.core.fetcher.Fetcher.get_credentials",mockcredentials)
#   fetch_bench = fetcher.Fetcher(resource_dir='/tmp/test/resource',benchmark_name='simple')
#   fetch_bench.svn_checkout('https://blabla.fr',['/tmp/test1','/tmp/test2','/tmp/test3'],None)
#   assert os.path.exists(os.path.join(init_env.config['resources_path'],'svn'))


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

  def mock_bm_run_bench(self,platform,wklist):
    return True

  monkeypatch.setattr("ubench.core.auto_benchmarker.AutoBenchmarker.init_run_dir", mock_auto_bm_init)
  monkeypatch.setattr("ubench.core.auto_benchmarker.AutoBenchmarker.get_benchmark_manager", mock_auto_bm_bench)
  monkeypatch.setattr("ubench.benchmark_managers.benchmark_manager.BenchmarkManager.set_parameter",mock_bm_set_param)
  monkeypatch.setattr("ubench.benchmark_managers.benchmark_manager.BenchmarkManager.run_benchmark",mock_bm_run_bench)
  ubench_cmd = ubench_commands.Ubench_cmd("",["simple"])
  ubench_cmd.run(['host1'],["param:new_value","argexec:'PingPong -npmin 56 msglog 1:18'"])
