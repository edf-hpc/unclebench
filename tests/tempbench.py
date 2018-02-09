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
    # self.config['resources_path']=config['main_path']+'/resources'
    self.create_dir_structure()


  def create_dir_structure(self):
    if not os.path.exists(self.config['main_path']):
      os.makedirs(self.config['main_path'])
    # for key,value in self.config.iteritems():
    #   if not os.path.exists(value):
    #     os.makedirs(value)

  def copy_files(self):
    dir_path = os.path.join(os.getcwd(),'tests/data/benchmarks/')
    shutil.copytree(dir_path,self.config['bench_path'])

  def create_run_dir(self,bench):
    path_bench = os.path.join(self.config['run_path'],bench)
    os.makedirs(path_bench)

  def destroy_dir_structure(self):
    shutil.rmtree(self.config['bench_path'])
    shutil.rmtree(self.config['run_path'])
    # shutil.rmtree(self.config['resources_path'])
