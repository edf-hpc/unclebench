#This class creates a test env for unclebench


import os
import tempfile
import shutil

class Tempbench:

  def __init__(self,config,repository_root):
    self.config = config
    self.config['bench_path']=config['main_path']+'/benchmarks'
    self.config['plugin_path']=config['main_path']+'/plugin'
    self.config['run_path']=config['main_path']+'/run'
    self.config['resources_path']=config['main_path']+'/resources'
    self.config['bench_input'] = os.path.join(repository_root,'benchmarks/simple')

    self.create_dir_structure()


  def create_dir_structure(self):
    for name, path in self.config.items():
      if not os.path.exists(path):
        os.makedirs(path)

  def copy_files(self):
    bench_input = self.config['bench_input']
    bench_path =os.path.join(self.config['bench_path'],'simple')
    shutil.copytree(bench_input,bench_path)

  def create_empty_bench(self):
    bench_path =os.path.join(self.config['bench_path'],'test_bench')
    os.makedirs(bench_path)
    open(os.path.join(bench_path,'test_bench.xml'),'a').close()

  def create_run_dir(self,bench):
    path_bench = os.path.join(self.config['run_path'],bench)
    os.makedirs(path_bench)

  def destroy_dir_structure(self):
    self.config.pop('bench_input', None)
    for name, path in self.config.items():
      if os.path.exists(path):
        shutil.rmtree(path)
