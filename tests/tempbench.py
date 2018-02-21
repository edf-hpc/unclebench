#This class creates a test env for unclebench


import os
import tempfile
import shutil

class Tempbench:

  def __init__(self,config):
    self.config = config
    self.config['bench_path']=config['main_path']+'/benchmarks'
    self.config['plugin_path']=config['main_path']+'/plugin'
    self.config['run_path']=config['main_path']+'/run'
    self.config['resources_path']=config['main_path']+'/resources'
    if config.has_key('bench_input'):
      self.config['bench_input']=config['bench_input']
    else:
      self.config['bench_input']=os.path.join(os.getcwd(),'tests/data/benchmarks/')

    self.create_dir_structure()


  def create_dir_structure(self):
    for name, path in self.config.iteritems():
      if not os.path.exists(path):
        os.makedirs(path)

  def copy_files(self):
    bench_input = self.config['bench_input']
    for d in os.listdir(bench_input):
      source_path = os.path.join(bench_input,d)
      target_path = os.path.join(self.config['bench_path'],d)
      if not os.path.exists(target_path):
        shutil.copytree(source_path,target_path)

  def create_run_dir(self,bench):
    path_bench = os.path.join(self.config['run_path'],bench)
    os.makedirs(path_bench)

  def destroy_dir_structure(self):
    self.config.pop('bench_input', None)
    for name, path in self.config.iteritems():
      if os.path.exists(path):
        shutil.rmtree(path)
