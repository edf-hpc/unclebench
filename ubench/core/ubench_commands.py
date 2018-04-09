# -*- coding: utf-8 -*-
##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2017  EDF SA                                          #
#                                                                            #
#  UncleBench is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by      #
#  the Free Software Foundation, either version 3 of the License, or         #
#  (at your option) any later version.                                       #
#                                                                            #
#  UncleBench is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#  GNU General Public License for more details.                              #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with UncleBench.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                            #
##############################################################################


import os, datetime, getpass
from subprocess import Popen
import ubench_config as uconfig
import auto_benchmarker as abench


import re
try :
  import ubench.scheduler_interfaces.slurm_interface as slurmi
except:
  pass

import ubench.benchmarking_tools_interfaces.jube_xml_parser as jube_xml_parser
import fetcher
import results_comparator as rc

class Ubench_cmd:

  def __init__(self,platform,benchmark_list = []):
    uconf = uconfig.UbenchConfig()
    self.run_dir = os.path.join(uconf.run_dir,platform)
    self.bench_dir = uconf.benchmark_dir
    self.platform = platform
    self.resource_dir = uconf.resource_dir
    self.report_dir = uconf.report_dir
    self.stylesheet_path = uconf.stylesheet_path
    self.conf_dir = uconf.conf_dir
    # Add benchmark managers for each benchmark in directory
    self.benchmark_list = benchmark_list
    self.auto_bm = abench.AutoBenchmarker('')
    self.auto_bm.add_benchmark_managers_from_path(uconf.plugin_dir,benchmark_list,platform)
    

  def log(self,id_list=[]):

    if not id_list:
      id_list=[-1]
    for bm_name in self.benchmark_list:
        bm=self.auto_bm.get_benchmark_manager(bm_name)
        for idb in id_list:
          try :
            bm.print_log(int(idb))
          except OSError as ose:
            print '    No run was found for {0} benchmark with id {1} : '.format(bm_name,str(idb))
            print '    '+str(ose)
    print ''


  def list_parameters(self):
    for benchmark_name in self.benchmark_list:
      bm=self.auto_bm.get_benchmark_manager(benchmark_name)
      print os.path.join(self.bench_dir,benchmark_name)
      bm.list_parameters(os.path.join(self.bench_dir,benchmark_name))

  def result(self,id_list):

    if not id_list:
      id_list=['last']

    for bm_name in self.benchmark_list:
      bm=self.auto_bm.get_benchmark_manager(bm_name)

      print 'Processing {0} benchmark :'.format(bm.benchmark_name)

      for idb in id_list:
        if idb=='-1':
          idb='last'

        # Analyse raw results from benchmark
        try:
          print '----analysing results'
          bm.analyse_benchmark(idb)
        except IOError:
          print '----no benchmark run found'
          return
        # Get formated results and build associated documentation
        try:
          print '----extracting analysis'
          print '----benchmark results path: {0}'.format(bm.benchmark_results_path)
          bm.extract_result_from_benchmark(idb)
        except IOError:
          print '----no result analyzer found, only raw results will be copied to the report directory'
        bm.print_result_array()

  # Lists runs information for a given benchmark
  def listb(self):

    for bm_name in self.benchmark_list:
      bm=self.auto_bm.get_benchmark_manager(bm_name)
      try :
        bm.list_benchmark_runs()
      except OSError as ose:
        print '    No run was found for {0} benchmark :'.format(bm_name)
        print '    '+str(ose)
      print ''


  def status(self,id_list=[]):
  # Set All default path.
    print "Status run dir: " + self.run_dir

    if not id_list:
      # JUBE command info and continue do not work with id: last
      id_list=['last']

    for bm_name in self.benchmark_list:
      bm=self.auto_bm.get_benchmark_manager(bm_name)
      print 'Processing {} benchmark :'.format(bm.benchmark_name)

      for idb in id_list:
        if idb=="-1":
          idb='last'
        bm.status(idb)

  def run(self,w_list=[],customp_list=[],raw_cli=[]):

    if w_list:
      try:
        w_list=self.translate_wlist_to_scheduler_wlist(w_list)
      except Exception as e:
        print '---- Custom node configuration is not valid : {0}'.format(str(e))
        return

    print ''
    print '-- Ubench platform name set to : {0}'.format(self.platform)

    try:
      self.auto_bm.init_run_dir(self.bench_dir,self.run_dir,self.benchmark_list)
    except Exception as e:
      print '---- Error while initializing run directory : {0} '.format(str(e))
      return

    if (not os.path.isdir(self.resource_dir)):
      print '---- The resource directory {0} does not exist. Please run ubench fetch to retrieve sources and test cases.'.format(self.resource_dir)
      return

    # Launch each benchmark if resources needed are found
    for benchmark_name in self.benchmark_list:
      if not (benchmark_name in os.listdir(self.resource_dir)):
        print '---- {0} will not be run as neither test case nor sources were found in {1}'.format(benchmark_name,self.resource_dir)
        continue
      bm=self.auto_bm.get_benchmark_manager(benchmark_name)
      # Set custom parameters

      dict_options = {}
      for elem in customp_list:
        try:
          splitted_param=re.split(':',elem,1)
          dict_options[splitted_param[0]]=splitted_param[1]
        except Exception as e:
          print '---- {0} is not formated correctly, please consider using : -c param:new_value'.format(elem)

      bm.set_parameter(dict_options)

      bm.run_benchmark(self.platform,w_list,raw_cli)

  def report(self):
    from jinja2 import Environment, PackageLoader
    # Get current time to name report directory
    now  = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M")
    # Set directory names and make report directory
    global_report_dirname  = 'Report_'+date+'-'+time
    global_report_dir_path = os.path.abspath(self.report_dir+'/Report_'+date+'-'+time)

    if not os.path.exists(global_report_dir_path):
      os.makedirs(global_report_dir_path)

    global_report_filename  = 'Benchmark_performances_report.txt'
    global_report_file_path = os.path.join(global_report_dir_path,global_report_filename)
    global_report_file      = open(global_report_file_path,'w')

    # Write report header
    template_env = Environment(loader=PackageLoader('ubench.core.ubench_commands','../../templates'))

    template = template_env.get_template('main.html')

    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    report_list=[]

    for benchmark_name in self.benchmark_list:
      print 'Do you want build a report section for '+benchmark_name+' benchmark(y/n)? ',
      choice = raw_input().lower()
      if choice in yes:
        bm=self.auto_bm.get_benchmark_manager(benchmark_name)
        print bm.benchmark_path
        if bm:
          try :
            report_file=self.auto_bm.write_report(global_report_dir_path,bm.benchmark_name,template_env)
          except OSError as ose:
            report_file=None
            print '----'+benchmark_name+' benchmark results cannot be found :'
            print '     '+str(ose)
          if report_file:
            report_list.append(report_file)
        else:
          print '----'+benchmark_name+' benchmark cannot be found'
      else:
        print '----'+benchmark_name+' benchmark section will not be written'
      print ''

    # Write report source file according using Jinja2 template file :
    global_report_file.write(template.render(report_file_list=report_list, date={'DMY':date,'hour':time}))
    # Compile global documentation file
    global_report_file.close()
    Popen('asciidoctor -a stylesheet='+self.stylesheet_path+' -n '+global_report_file_path,cwd=os.getcwd(),shell=True)

    print 'Report was built in '+global_report_dir_path

  def fetch(self,server=[]):

    for benchmark_name in self.benchmark_list:
      benchmark_dir = os.path.join(self.bench_dir,benchmark_name)
      benchmark_files = [file_b for  file_b in os.listdir(benchmark_dir) if file_b.endswith(".xml")]
      jube_xml_files = jube_xml_parser.JubeXMLParser(benchmark_dir,benchmark_files)
      multisource = jube_xml_files.get_bench_multisource()

      if multisource is None:
        print "ERROR !! : Multisource information for benchmark not found"
        return None

      fetch_bench = fetcher.Fetcher(resource_dir=self.resource_dir,benchmark_name=benchmark_name)
      for source in multisource:

        if not source.has_key('do_cmds'):
          source['do_cmds'] = None

        if source['protocol'] == 'https':
          fetch_bench.https(source['url'],source['files'])
        elif source['protocol'] == 'svn' or source['protocol'] == 'git':
          if not source.has_key('revision'):
            source['revision'] = None
          if not source.has_key('branch'):
            source['branch'] = None

          fetch_bench.scm_fetch(source['url'],source['files'],source['protocol'],source['revision'],source['branch'],source['do_cmds'])

        elif source['protocol'] == 'local':
          fetch_bench.local(source['files'])


  def compare(self,result_directories,context_list=None,threshold=None):
    """
    Compare bencharks results from different directories.
    """
    rcomparator=rc.ResultsComparator(context_list,threshold)
    print("    comparing :")
    for rdir in result_directories:
      print("    - "+rdir)
    print("")
    rcomparator.print_comparison(result_directories)
    

  def translate_wlist_to_scheduler_wlist(self,w_list_arg):
  # Translate ubench custom node list format to scheduler custome node list format
  # TODO determine scheduler_interface from platform data.

    try:
      scheduler_interface=slurmi.SlurmInterface()
    except:
      print "Warning!! Unable to load slurmi module"
      scheduler_interface=None
      return

    w_list=list(w_list_arg)
    for sub_wlist in w_list:
      sub_wlist_temp=list(sub_wlist)
      stride=0
      for idx, welem in enumerate(sub_wlist_temp):
      # Manage the all keyword that is meant to launch benchmarks on evry idle node
        catch=re.search(r'^all(\d+)$',str(welem))
        idxn=idx+stride
        if catch:
          slice_size=int(catch.group(1))
          available_nodes_list=scheduler_interface.get_available_nodes(slice_size)
          njobs=len(available_nodes_list)
          sub_wlist[idxn:idxn+1]=zip([slice_size]*njobs,available_nodes_list)
          stride+=njobs-1
        else:
          # Manage the cn[10,13-17] notation
          catch=re.search(r'^(\D+.*)$',str(welem))
          if catch:
            nnodes_list=[scheduler_interface.get_nnodes_from_string(catch.group(1))]
            nodes_list=[catch.group(1)]
            sub_wlist[idxn:idxn+1]=zip(nnodes_list,nodes_list)
          else:
            # Manage the 2,4 notation that is needed to launch jobs without defined node targets.
            catch=re.search(r'^([\d+,]*)([\d]+)$',str(welem))
            if catch:
              nnodes_list=[int(x) for x in (re.split(',',str(welem)))]
              sub_wlist[idxn:idxn+1]=zip(nnodes_list,[None]*len(nnodes_list))
              stride+=len(nnodes_list)-1
            else:
            # Manage the 2,4,cn[200-205] notation that is used to get cn[200-201] cn[200-203]
              catch=re.search(r'^([\d+,]*[\d+]),(.*)$',str(welem))
              if catch:
                nnodes_list=[int(x) for x in (re.split(',',catch.group(1)))]
                nodes_list=str(catch.group(2))
                sub_wlist[idxn:idxn+1]=zip(nnodes_list,\
                                         scheduler_interface.get_truncated_nodes_lists(nnodes_list,nodes_list))
                stride+=len(nnodes_list)-1
              else:
                raise Exception(str(welem)+'format is not correct')

    # Flatten the w_list
    w_list=[item for sublist in w_list for item in sublist]
    return w_list
