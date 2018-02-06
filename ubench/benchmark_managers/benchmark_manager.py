#!/usr/bin/env python
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

import os, re, sys
import ubench.benchmarking_tools_interfaces.jube_benchmarking_api as jba
import time
import ubench.core.ubench_config as uconfig

class BenchmarkManager:

    def __init__(self,benchmark_name,platform):
        """ Constructor
        :param benchmark_name: name of the benchmark
        :type benchmark_name: str
        :param benchmark_path: absolute path of the benchmark root directory.
        :type benchmark_path: str
        """
        self.result_array=[]
        self.transposed_result_array=[]
        self.benchmark_results_path=''
        self.benchmark_name=benchmark_name
        uconf = uconfig.UbenchConfig()
        self.benchmark_path= os.path.join(uconf.run_dir,platform,benchmark_name)
        self.benchmarking_api=jba.JubeBenchmarkingAPI(benchmark_name,platform)

        # Default report parameters
        self.title=benchmark_name
        self.description=''
        self.print_array=True
        self.print_transposed_array=False
        self.print_plot=False
        self.plot_list=[]


#===============  Benchmarking part  ===============#

    def run_benchmark(self,platform,w_list=[]):
        """ Run benchmark on a given platform and write a ubench.log file in
        the benchmark run directory.
        :param platform: name of the platform used to retrieve parameters needed to run the benchmark.
        :type platform: str
        :param w_list: nodes configurations used to run the benchmark.
        :type w_list: list of tuples [(number of nodes, nodes id list), ....]
        """
        if w_list:
            try:
                nnodes_list=[list(t) for t in zip(*w_list)][0]
                nodes_id_list=[list(t) for t in zip(*w_list)][1]
                # unique values in list
                if len(list(set(nodes_id_list))) == 1 and not nodes_id_list[0]:
                  nodes_id_list = None

                self.benchmarking_api.set_custom_nodes(nnodes_list,nodes_id_list)
            except ValueError:
                print 'Custom node configuration is not valid.'
                return
            except IndexError:
                print 'Custom node configuration is not valid.'
                return

        try:
            run_dir,ID =self.benchmarking_api.run_benchmark(platform)
        except RuntimeError as rerror:
            print '---- Error launching benchmark :'
            print str(rerror)
            return
        except OSError:
            print
            return

        print '---- benchmark run directory :',run_dir
        logfile_path=os.path.join(run_dir,'ubench.log')
        date=time.strftime("%c")
        flattened_w_list=''
        if w_list:
            for nnodes,nodes_id in w_list:
                if nodes_id:
                    flattened_w_list+=str(nodes_id)+' '
                else:
                    flattened_w_list+=str(nnodes)+' '
        else:
            flattened_w_list='default'

        with open(logfile_path, 'w') as logfile:
            logfile.write('Benchmark_name  : {0} \n'.format(self.benchmark_name))
            logfile.write('Platform        : {0} \n'.format(platform))
            logfile.write('ID              : {0} \n'.format(ID))
            logfile.write('Date            : {0} \n'.format(date))
            logfile.write('Run_directory   : {0} \n'.format(run_dir))
            logfile.write('Nodes           : {0} \n'.format(flattened_w_list))

        print '---- Use the following command to follow benchmark progress :'\
            +'    " ubench log -p {0} -b {1} -i {2}"'.format(platform,self.benchmark_name,ID)

    def list_parameters(self,config_dir_path=None):
      all_parameters = self.benchmarking_api.list_parameters(config_dir_path)
      for type_param in all_parameters:
        print "\n"
        print type_param + " parameters"
        print "-----------------------------------------------"
        for parameter,value in all_parameters[type_param]:
            print parameter.rjust(20)+' : '+value

    def set_parameter(self,dict_options):
        """
        Set custom parameter from its name and a new value.
        :param parameter_name: name of the parameter to customize
        :type parameter_name:
        :param value: value to substitute to old value
        :type value: str
        :returns: Return a list of tuples [(filename,param1,old_value,new_value),(filename,param2,old_value,new_value),....]
        :rtype: List of 3-tuples ex:[(parameter_name,old_value,value),....]
        """
        modified_params=self.benchmarking_api.set_parameter(dict_options)
        for elem in modified_params:
            print '---- {0} parameter was modified from {1} to {2} for this run'.format(*elem)

        return

#===============      Analyze part   ===============#
    def print_log(self,idb=-1):
        """ Print log from a benchmark run
        :param idb: id of the benchmark
        :type idb:int
        """
        try :
            print self.benchmarking_api.get_log(idb)
        except IOError as io_error:
            print '---- Error: cannot find benchmark logs :'
            print str(io_error)
            return

    def list_benchmark_runs(self):
        """ List benchmark runs with their IDs and status """
        field_pattern = re.compile('(.*) : (.*)')
        field_dict={}
        max_len_key={}
        sorted_key_list=[]
        nbenchs=0
        # Retrieve informations from ubench.log files found in the benchmark directory.
        # Informations are organized in a dictionnary.
        logfile_paths=[]
        result_root_dir=self.benchmarking_api.get_results_root_directory()
        for fd in os.listdir(result_root_dir):
            for filename in os.listdir(os.path.join(result_root_dir,fd)):
                if (filename=='ubench.log'):
                    logfile_paths.append(os.path.join(result_root_dir,fd,'ubench.log'))

        # The second loop is need to parse files in a sorted order.
        for filepath in sorted(logfile_paths):
            with open(filepath, 'r') as logfile:
                nbenchs+=1
                fields = field_pattern.findall(logfile.read())
                for field in fields :
                    if field[0] in field_dict:
                        field_dict[field[0]].append(field[1])
                        max_len_key[field[0]]=max(len(field[1]),max_len_key[field[0]])
                    else:
                        sorted_key_list.append(field[0]) # List to keep keys sorted in order of appearrance
                        field_dict[field[0]]=[field[1]]
                        max_len_key[field[0]]=max(len(field[1]),len(field[0]))

        if not field_dict:
            print '----no benchmark run found for : {0}'.format(self.benchmark_name)

        # Print dictionnary with a table layout.
        separating_line=''
        for key in sorted_key_list:
            sys.stdout.write(key.ljust(max_len_key[key])+' | ')
            separating_line+='-'*max_len_key[key]
        print ''
        print separating_line

        for i in range(nbenchs):
            for key in sorted_key_list:
                sys.stdout.write(field_dict[key][i].ljust(max_len_key[key])+' | ')
            print ''


    def analyse_benchmark(self,benchmark_id):
        """ Analyse benchmark results
        :param benchmark_id: id of the benchmark to analyze
        :type benchmark_id: int"""
        self.benchmark_results_path=self.benchmarking_api.analyse_benchmark(benchmark_id)

    def extract_result_from_benchmark(self,benchmark_id):
        """ Get result from a jube benchmark with its id and build a python result array
        :param benchmark_id: id of the benchmark to analyze
        :type benchmark_id: int"""
        self.result_array=self.benchmarking_api.extract_result_from_benchmark(benchmark_id)
        self.transposed_result_array=[list(x) for x in zip(*self.result_array)]

    def analyse_last_benchmark(self):
        """ Get last result from a jube benchmark """
        self.benchmark_results_path=self.benchmarking_api.analyse_last_benchmark()

    def extract_result_from_last_benchmark(self):
        """ Get last result from a jube benchmark """
        self.result_array=self.benchmarking_api.extract_result_from_last_benchmark()
        self.transposed_result_array=[list(x) for x in zip(*self.result_array)]

    def status(self,benchmark_id):
        self.benchmarking_api.status(benchmark_id)

#===============    Reporting part   ===============#

    def print_result_array(self,output_file=None):
        """ Asciidoc printing of Jube result array
        :param output_file:  path of a file where to write the array,
        if not set the array is printed on stdout.
        :type output_file: string"""
        if output_file:
            output_file.write('[options="header"]\n')
            output_file.write('|=== \n')
            for row in self.result_array:
                output_file.write('|')
                output_file.write('|'.join(row).replace("\n", ""))
                output_file.write('\n')
            output_file.write('|=== \n')
        else:
            # print formatted array on stdout
            max_width=[]
            for row in self.result_array:
                col=0
                for el in row:
                    if (len(max_width)-1)<col:
                        max_width.append(len(el))
                    else:
                        max_width[col]=max(max_width[col],len(el))
                    col+=1

            print ''
            for row in self.result_array:
                col=0
                for el in row[:-1]:
                    print str(el).ljust(max_width[col]+1),
                    col+=1
                if row[-1]:
                    print str(row[-1]).strip()
                else:
                    print ''
            print ''


    def print_transposed_result_array(self,output_file=None):
        """ Asciidoc printing of transposed Jube result array
        :param output_file:  path of a file where to write the array,
        if not set the array is printed on stdout.
        :type output_file: string"""
        if output_file:
            output_file.write('[options="header"]\n')
            output_file.write('|=== \n')

            for row in self.transposed_result_array:
                output_file.write('|')
                output_file.write('|'.join(row).replace("\n", ""))
                output_file.write('\n')
            output_file.write('|=== \n')


    def print_image(self,output_file,image_filename,image_id,title):
        """ Asciidoc printing of an image """
        output_file.write('[[{0}]]\n.{1}\n'.format(image_id,title))
        output_file.write('image::{0}[]\n'.format(image_filename))


    def plot(self,output_file,benchmark_idx=0):
        """ Default plot. Returns a tuple containing image title, legend and image filename  """
        return ("","","")

    def build_doc(self,docfile_path,template_env):
        """ Build a report file from a template using [transposed]_result_array attribute that is set by
        the analyse_benchmark method.
        :param docfile_path: path of file where to save the report
        :type docfile_path: str
        :param template_env: template environment
        :type template_env: Environment (jinja2)"""
        doc_dir=os.path.dirname(docfile_path)
        template_dic={}
        # Print benchmark title + description
        template_dic['title']=self.title
        template_dic['description']=self.description

        # Print transposed result_array
        if self.print_array:
            template_dic['result_array']=self.result_array

        if self.print_transposed_array:
            template_dic['result_array']=self.transposed_result_array

        if self.print_plot:
            template_dic['plot_list']=[]
            for iplot in self.plot_list :
                image_filename=self.benchmark_name+'_'+str(iplot)+'.png'
                image_title,legend=self.plot(os.path.join(doc_dir,image_filename),iplot)
                template_dic['plot_list'].append((image_title,legend,image_filename))

        template = template_env.get_template('bench.html')
        with open(docfile_path, 'w') as doc_file :
            doc_file.write(template.render(template_dic))
