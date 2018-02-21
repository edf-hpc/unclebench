import os
import tempbench
import xml.etree.ElementTree as ET
import ubench.benchmarking_tools_interfaces.jube_benchmarking_api as jba
import ubench.benchmarking_tools_interfaces.jube_xml_parser as j_xml


test_env = None


"you have to export UBENCH_BENCHMARK_DIR= path of bench you want to test"
def init_env():
  config = {}
  config['main_path'] = "/tmp/ubench_multisource_test/"
  global test_env
  test_env = tempbench.Tempbench(config);
  test_env.copy_files()
  os.environ["UBENCH_RUN_DIR_BENCH"] = test_env.config['run_path']
  os.environ["UBENCH_RESOURCE_DIR"] = test_env.config['resources_path']


def get_bench_multisource_git(bench):
  benchmarking_api=jba.JubeBenchmarkingAPI(bench,"")
  path = os.path.join(test_env.config['run_path'],bench)
  if not os.path.exists(path):
    os.makedirs(path)
  benchmarking_api.jube_xml_files.add_bench_input()
  benchmarking_api.jube_xml_files.write_bench_xml()


init_env()
get_bench_multisource_git("aster")
print "Files were generated in {0}".format(test_env.config['run_path'])
