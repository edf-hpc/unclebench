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
    self.create_dir_structure()


  def create_dir_structure(self):
    for name, path in self.config.iteritems():
      if not os.path.exists(path):
        os.makedirs(path)

  def copy_files(self):
    dir_path = os.path.join(os.getcwd(),'tests/data/benchmarks/simple')
    shutil.copytree(dir_path,self.config['bench_path']+'/simple')
    dir_path = os.path.join(os.getcwd(),'tests/data/benchmarks/simple_git')
    shutil.copytree(dir_path,self.config['bench_path']+'/simple_git')
    dir_path = os.path.join(os.getcwd(),'tests/data/benchmarks/test_bench')
    shutil.copytree(dir_path,self.config['bench_path']+'/test_bench')

  def create_run_dir(self,bench):
    path_bench = os.path.join(self.config['run_path'],bench)
    os.makedirs(path_bench)

  def destroy_dir_structure(self):
    for name, path in self.config.iteritems():
      if os.path.exists(path):
        shutil.rmtree(path)
