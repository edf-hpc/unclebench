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
"""
Jube benchmarking API module
"""
import os
import re
import time
import csv
import tempfile
from subprocess import Popen, PIPE


import ubench.core.ubench_config as uconfig
import ubench.data_management.data_store_yaml as data_store_yaml
from . import benchmarking_api as bapi
from . import jube_xml_parser

try:
    import ubench.scheduler_interfaces.slurm_interface as slurmi
except:
    pass

class JubeBenchmarkingAPI(bapi.BenchmarkingAPI):
    """
    Jube benchmarking API class implements abstract class benchmarkingAPI
    to use Jube backend.
    """

    def __init__(self, benchmark_name, platform_name):
        """ Constructor
        :param benchmark_name: name of the benchmark
        :type benchmark_name: str
        :param platform_name: name of the platform
        :type platform_name: str
        """
        bapi.BenchmarkingAPI.__init__(self, benchmark_name, platform_name)
        self.uconf = uconfig.UbenchConfig()
        self.benchmark_path_in \
          = os.path.join(self.uconf.benchmark_dir,\
                         benchmark_name,\
                         benchmark_name+".xml")

        self.benchmark_name = benchmark_name
        self.platform_name = platform_name
        benchmark_dir = os.path.join(self.uconf.benchmark_dir,\
                                     benchmark_name)

        benchmark_files = [file_b for  file_b in \
                           os.listdir(benchmark_dir) \
                           if file_b.endswith(".xml")]
        self.benchmark_path \
          = os.path.join(self.uconf.run_dir,\
                         platform_name,\
                         benchmark_name)

        self.jube_xml_files \
          = jube_xml_parser.JubeXMLParser(benchmark_dir,\
                                          benchmark_files,\
                                          self.benchmark_path,\
                                          self.uconf.platform_dir)
        self.jube_xml_files.load_platform_xml(platform_name)
        self.jube_const_params = {}

    def analyse(self, benchmark_id):
        """ Analyze benchmark results
        :param benchmark_id: id of the benchmark to be analyzed
        :type benchmark_id: int
        :returns: result directory absolute path
        :rtype: str
        :raises: IOError
        """
        old_path = os.getcwd()
        if not os.path.isdir(self.benchmark_path):
            raise IOError

        os.chdir(self.benchmark_path)
        output_dir = self.jube_xml_files.get_bench_outputdir()

        # Continue benchmark steps that were not already executed.
        # This is often mandatory to execute postprocessing steps.
        cmd_str = 'jube continue --hide-animation {} --id {}'.format(output_dir,benchmark_id)
        continue_cmd = Popen(cmd_str, cwd=os.getcwd(),
                             stdout=open(os.devnull, "w"), shell=True,
                             universal_newlines=True)
        continue_cmd.wait()

        input_str = 'jube analyse ./'+output_dir+' --id '+benchmark_id
        analyse_from_jube = Popen(input_str, cwd=os.getcwd(), shell=True, stdout=PIPE, universal_newlines=True)
        benchmark_results_path = ''


        for line in analyse_from_jube.stdout:
            if 'Analyse data storage: ' in line:
                benchmark_results_path \
                  = os.path.join(self.benchmark_path,
                                 line[(line.find(':')+2):(line.find('analyse.xml'))])
                if benchmark_results_path == '':
                    raise IOError

        # Restore working directory
        os.chdir(old_path)

        return benchmark_results_path


    def analyse_last(self):
        """ Get last result from a jube benchmark.
        :returns: result directory absolute path, None if analysis failed.
        :rtype: str
        """
        try:
            return self.analyse('last')
        except Exception:
            raise

    def get_results_root_directory(self):
        """ Returns benchmark results root directory
        :returns: result directory asbolut path
        :rtype: str
        """
        return os.path.join(self.benchmark_path, self.jube_xml_files.get_bench_outputdir())

    def get_log(self, idb=-1):
        """ Get a log from a benchmark run
        :param idb: id of the benchmark
        :type idb:int
        :returns: log
        :rtype:str
        """
        out_path = self.get_results_root_directory()
        # If idb equals -1 get highest id directory found in out_dir
        if idb == -1:
            dir_list = []
            newest_result_dir = None

            for fd in os.listdir(out_path):
                result_dir = os.path.join(out_path, fd)
                if os.path.isdir(result_dir):
                    dir_list.append(result_dir)

            newest_result_dir \
              = max(dir_list, key=os.path.getmtime)
            idb_s = newest_result_dir
        else:
            idb_s = str(idb).zfill(6)

        # Padding ID with zeros to reach a 6 length id to get Jube run directory path.
        run_path = os.path.join(out_path, idb_s)
        configuration_file_path = os.path.join(run_path, 'configuration.xml')

        # Standard log files to look for
        log_files = ['stdout', 'stderr', 'run.log']

        try:
            self.jube_xml_files.load_config_xml(configuration_file_path)
        except:
            raise IOError('Cannot find: '+configuration_file_path+' file.')

        # Get job errlog and outlog filenames from configuration.xml file
        log_files += self.jube_xml_files.get_job_logfiles()

        # Get filenames that are used for analyse from configuration.xml file
        log_files += self.jube_xml_files.get_analyse_files()

        # Concatenante evry files that are considered as log file and order them
        # with the last modified file at the last position.
        result = ''
        log_files_found = []
        for root, dirs, files in os.walk(run_path):
            for f in files:
                if f in log_files:
                    log_files_found.append(os.path.join(root, f))


        for fpath in sorted(log_files_found, key=os.path.getmtime):
            result += '========= '+fpath+' =========\n'
            with open(fpath, 'r') as log_file:
                result += log_file.read()+'\n'

        return '\n-------------------------------------------------------\n'\
            +'==== Log for {0} benchmark. (run ID = {1})  ==== \n'\
            .format(self.benchmark_name, os.path.basename(idb_s))\
            +'-------------------------------------------------------\n\n'\
            +result

    def get_status_info(self, benchmark_id):
        """ Get the status for a benchmark run
        :param benchmark_id: id of the benchmark
        :returns: global_status
        :rtype:dict
        """
        if not os.path.isdir(self.benchmark_path):
            raise IOError

        os.chdir(self.benchmark_path)
        output_dir = self.jube_xml_files.get_bench_outputdir()

        bench_steps = self.jube_xml_files.get_bench_steps()

        global_status = {}
        for step in bench_steps:
            # Updating state with continue command
            continue_cmd = Popen('jube continue --hide-animation ./'+\
                                 output_dir+' --id '+benchmark_id, cwd=os.getcwd(),\
                                 stdout=open(os.devnull, "w"), shell=True, universal_newlines=True)
            continue_cmd.wait()
            input_str = 'jube info ./'+output_dir+' --id '+benchmark_id+' --step '+step
            status_from_jube = Popen(input_str, cwd=os.getcwd(), shell=True, stdout=PIPE,
                                     universal_newlines=True)
            global_status[step] = []
            for line in status_from_jube.stdout:
                if re.search(r"^\s+\d+\s+\|\s+\w+\s+\|.*", line):
                    raw_values = [c.strip() for c in line.split("|")]
                    task = {}
                    task['id'] = raw_values[0]
                    task['started'] = raw_values[1]
                    task['done'] = raw_values[2]
                    task['workdir'] = raw_values[3]
                    global_status[step].append(task)

        return global_status

    def write_bench_data(self, benchmark_id):
        """
        TODO
        """
        try:
            scheduler_interface = slurmi.SlurmInterface()
        except:
            print("Warning!! Unable to load Slurm module")
            scheduler_interface = None

        os.chdir(self.benchmark_path)
        output_dir = self.jube_xml_files.get_bench_outputdir()
        benchmark_rundir = self.get_bench_rundir(benchmark_id)
        jube_cmd = "jube info ./{0} --id {1} --step execute".format(output_dir, benchmark_id)

        cmd_output = tempfile.TemporaryFile()
        result_from_jube = Popen(jube_cmd, cwd=os.getcwd(), shell=True, stdout=cmd_output,
                                 universal_newlines=True)
        ret_code = result_from_jube.wait()

        cmd_output.flush()
        cmd_output.seek(0)
        results = {}
        workpackages = re.findall(r"Workpackages(.*?)\n{2,}",
                                  cmd_output.read().decode('utf-8'), re.DOTALL)[0]
        workdirs = {}
        regex_workdir = r"^\s+(\d+).*("+re.escape(output_dir)+r".*work).*"

        for package in workpackages.split('\n'):
            temp_match = re.match(regex_workdir, package)
            if temp_match:
                id_workpackage = temp_match.group(1)
                path_workpackage = temp_match.group(2)
                workdirs[id_workpackage] = path_workpackage

        cmd_output.seek(0)
        parameterization = re.findall(r"ID:(.*?)(?=\n{3,}|\sID)",
                                      cmd_output.read().decode('utf-8')+'\n', re.DOTALL)
        for execution_step in parameterization:
            id_step = [x.strip() for x in execution_step.split("\n")][0]
            param_step = [x.strip() for x in execution_step.split("\n")][1:]
            results[id_step] = {}

            for parameter in param_step:
                temp_match = re.match(r'^\S+:', parameter)
                if temp_match:
                    value = parameter.replace(temp_match.group(0), '')
                    param = temp_match.group(0).replace(':', '')
                    results[id_step][param] = value.strip()


        cmd_output.close()

        for key, value in list(results.items()):
            result_file_path = os.path.join(benchmark_rundir, "result/ubench_results.dat")

            # we add the part of results which corresponds to a given execute
            with open(result_file_path) as csvfile:
                reader = csv.DictReader(csvfile)

                field_names = reader.fieldnames
                common_fields = list(set(value.keys()) & set(field_names))
                result_fields = list(set(field_names) - set(common_fields))
                temp_hash = {}

                for field in result_fields:
                    temp_hash[field] = []

                for row in reader:
                    add_to_results = True
                    for field in common_fields:
                        if value[field] != row[field]:
                            add_to_results = False
                            break
                    if add_to_results:
                        for field in result_fields:
                            temp_hash[field].append(row[field])

                # when there is just value we transform the array in one value
                for field in result_fields:

                    if len(temp_hash[field]) == 1:
                        temp_hash[field] = temp_hash[field][0]


                results[key]['results_bench'] = temp_hash
                results[key]['context_fields'] = common_fields

            #Add job information to step execute
            job_file_path = os.path.join(workdirs[key], "stdout")
            job_id = 0

            with  open(job_file_path, 'r') as job_file:
                for line in job_file:
                    re_result = re.findall(r'\d+', line)
                    if re_result:
                        job_id = re_result[0]
                        value['job_id_ubench'] = job_id
                        if scheduler_interface:
                            job_info = scheduler_interface.get_job_info(job_id)
                            if job_info:
                                value.update(job_info[-1])
                                results[key].update(value)
                        break

        # Add metadata present on ubench.log
        field_pattern = re.compile('(.*) : (.*)')

        try:
            log_file = open(os.path.join(benchmark_rundir, "ubench.log"), 'r')
        except IOError:
            print('Warning!! file ubench log was not found.'+\
                  'Benchmark data result could not be created')
            return

        metadata = {}
        fields = field_pattern.findall(log_file.read())

        for field in fields:
            metadata[field[0].strip()] = field[1].strip()


        bench_data = data_store_yaml.DataStoreYAML()
        bench_data.write(metadata, results, os.path.join(benchmark_rundir, 'bench_results.yaml'))



    def extract_results(self, benchmark_id):
        """ Get result from a jube benchmark with its id and build a python result array
        :param benchmark_id: id of the benchmark
        :type benchmark_id:int
        :returns: a result array
        :rtype:str
        """
        old_path = os.getcwd()
        os.chdir(self.benchmark_path)
        output_dir = self.jube_xml_files.get_bench_outputdir()
        benchmark_rundir = self.get_bench_rundir(benchmark_id)

        benchmark_runpath = os.path.join(old_path, output_dir, benchmark_rundir)

        configuration_file_path = os.path.join(benchmark_runpath, 'configuration.xml')

        try:
            self.jube_xml_files.load_config_xml(configuration_file_path)
        except:
            raise IOError('Cannot find: '+configuration_file_path+' file.')

        # Get job errlog and outlog filenames from configuration.xml file
        cvsfile = self.jube_xml_files.get_result_cvsfile()
        debugfile = "paths"

        input_str = 'jube result {} --id {} -o {} {}'.format(output_dir,
                                                             benchmark_id,
                                                             cvsfile,
                                                             debugfile)
        jube_command = Popen(input_str, cwd=os.getcwd(), shell=True, stdout=PIPE,
                                 universal_newlines=True)

        jube_stdout, _ = jube_command.communicate()
        result_array = []

        with open(os.path.join(benchmark_rundir, 'result/ubench_results.dat'), 'w') as result_file:

            for line in jube_stdout.split('\\n'):
                result_file.write(line)

        jubecvsfile_path = os.path.join(benchmark_runpath,'result','{}.dat'.format(cvsfile))

        try:
            with open(jubecvsfile_path,'r') as jubecsvfile:
                jubereader = csv.reader(jubecsvfile)
                for row in jubereader:

                    if isinstance(row,list):
                        result_array.append(row)
        except IOError:
            print("JUBE cvs file not found")
            return []

        return result_array


    def extract_results_last(self):
        """ Get result from the last execution of a benchmark
        :param benchmark_id: id of the benchmark
        :type benchmark_id:int
        :returns: result array
        :rtype:str
        """
        try:
            return self.extract_result('last')
        except IOError:
            raise


    def run(self, platform):
        """ Run benchmark on a given platform and return the benchmark run directory path
        and a benchmark ID.
        :param platform: name of the platform used to configure the benchmark options relative
        to the platform architecture and software.
        :type platform: str
        :returns: return absolute path of the benchmark result directory
        :rtype: str
        """
        old_path = os.getcwd()
        os.chdir(self.benchmark_path)

        # modify bench xml
        self.jube_xml_files.add_bench_input()
        self.jube_xml_files.remove_multisource()
        self.jube_xml_files.write_bench_xml()
        self.jube_xml_files.write_platform_xml()
        platform_dir = self.jube_xml_files.get_platform_dir()

        old_run_dir = self.analyse_last()

        input_str = 'jube run --hide-animation '+\
                    self.benchmark_name+'.xml --tag '+platform+' > /dev/null &'
        my_env = os.environ
        my_env['UBENCH_PLATFORM_DIR'] = platform_dir
        Popen(input_str, cwd=os.getcwd(), shell=True, env=my_env, universal_newlines=True)

        # Get the run directory without waiting for jube run command to finish
        run_dir = self.analyse_last()
        timeout_counter = 0
        time.sleep(2) # waiting for the directory to be created
        while run_dir == old_run_dir:
            time.sleep(1) # wait to avoid spamming
            timeout_counter += 1
            run_dir = self.analyse_last()
            if timeout_counter > 10:
                raise RuntimeError('Jube parsing might have gone wrong, please check '+
                                   self.benchmark_path+'/jube-parse.log file')

        # Get benchmark run directory
        bench_id = run_dir[-7:-1]

        absolute_run_dir = os.path.abspath(run_dir)
        # Restore working directory
        os.chdir(old_path)
        self.jube_xml_files.delete_platform_dir()
        return (absolute_run_dir, bench_id)


  # def status(self,benchmark_id):

  #       status = self.get_status_info(benchmark_id)
  #       for step in status:
  #           print "\nStatus for step: "+step
  #           print "--------------------------------"
  #           print "id\tstarted\tdone\tworkdir"
  #           print "--------------------------------"
  #           for task in status[step]:
  #               print task['id'] + "\t"+ task['started']+"\t"+task['done']+"\t"+task['workdir']


    def set_execution_only_mode(self):
        # Transform the benchmark file to utilise only the execution part of the benchmark
        self.jube_xml_files.set_bench_execution()

    def set_custom_nodes(self, nnodes_list, nodes_id_list):
        """
        Modify benchmark xml file to set custom nodes configurations.
        :param nnodes_list: list of number of nodes ex: [1,6]
        :type nnodes_list: list of int
        :param nodes_id_list: list of corresonding nodes ids  ex: ['cn050','cn[103-107,145]']
        :type nodes_id_list:  list of strings
        """
        self.jube_xml_files.substitute_element_text('parameter', 'nodes', '.*', '$custom_nodes')
        if nodes_id_list:
            for subcmd in ["submit", "{submit}", "submit_singleton", "{submit_singleton}"]:
                self.jube_xml_files.substitute_element_text('do', None, re.escape('$'+subcmd+' '),
                                                            '$custom_'+subcmd+' ')

        # Add an xml section describing custom nodes configurations
        self.jube_xml_files.add_custom_nodes_stub(nnodes_list, nodes_id_list)

    def list_parameters(self, default_values):
        """
        List benchmark customisable parameters
        :param default_values: TODO
        :type default_values: TODO
        :returns: Return a list of tuples [(param1,value),(param2,value),....]
        :rtype: list of tuples
        """
        platform_params = self.jube_xml_files.get_params_platform(self.platform_name)
        benchmark_params = self.jube_xml_files.get_params_bench()
        if default_values:
            eval_platform_params = self.parse_jube_parameter(platform_params)
            eval_benchmark_params = self.parse_jube_parameter(benchmark_params)
            parameters_list = {'platform' : eval_platform_params,
                               'benchmark' : eval_benchmark_params}
        else:
            parameters_list = {'platform' : platform_params,
                               'benchmark' : benchmark_params}

        return  parameters_list

    def set_parameter(self, dict_options):
        """
        Set custom parameter from its name and a new value.
        :param dic_options: TODO
        :type dict_options: TODO
        :returns: Return a list of tuples
        [(filename,param1,old_value,new_value),(filename,param2,old_value,new_value),....]
        :rtype: List of 3-tuples ex:[(parameter_name,old_value,value),....]
            """
        return self.jube_xml_files.set_params_bench(dict_options) \
            + self.jube_xml_files.set_params_platform(dict_options)

    def get_bench_rundir(self, benchmark_id):
        """
        Get bechmark rundir based on benchmark id
        """
        output_dir = self.jube_xml_files.get_bench_outputdir()

        if benchmark_id == 'last':
            jube_last_cmd = Popen('jube info ./'+output_dir+' -i last', cwd=os.getcwd(),
                                  shell=True, stdout=PIPE, universal_newlines=True)
            dir_pattern = re.compile(r'\S+: (\/.*)')
            return dir_pattern.findall(jube_last_cmd.stdout.read())[0]
        else:
            return os.path.join(self.benchmark_path, output_dir, str(benchmark_id).zfill(6))

    def parse_jube_parameter(self, list_jube_parameters):
        """
        TODO
        """
        # get constants
        const_hash = {}
        variable_hash = {}
        parameter_regex_sub = '(?<!\\$)(?:\\$\\$)*\\$(?!\\$)(\\{)?(.+?)(?(1)\\}|(?:\\w+|$))'
        parameter_regex_find = '(?<!\\$)(?:\\$\\$)*\\$(?!\\$)(\\{)?(.+?)(?(1)\\}|(?:\\W|$))'
        external_variables = []
        for k, v in list_jube_parameters:
            variables = [m2 for m1, m2 in re.findall(parameter_regex_find, v)]
            #import pdb;pdb.set_trace()
            if variables:
                # import pdb;pdb.set_trace()
                if len(set(variables) & set([var for var, value in list_jube_parameters]))\
                   != len(set(variables)):
                    external_variables.append(k)
                elif set(variables) & set(external_variables):
                    external_variables.append(k)

        [const_hash.update({k:v}) for k, v in list_jube_parameters\
         if not re.findall(parameter_regex_find, v)]
        [variable_hash.update({k:v}) for k, v in list_jube_parameters\
         if re.findall(parameter_regex_find, v)]

        # we get rid of variables that cannot not be resolved, mostly Jube
        for var in external_variables:
            variable_hash.pop(var)

        self.jube_const_params.update(const_hash)
        parsed_data = []
        while variable_hash:
            temp_hash = {}
            for k, v in variable_hash.items():
                python_exp = re.sub(parameter_regex_sub, self.val_repl, v)
                if not re.findall(parameter_regex_find, python_exp):
                    try:
                        python_eval = eval(python_exp)
                        self.jube_const_params[k] = python_eval
                        parsed_data.append((k, str(python_eval)))
                    except (NameError, SyntaxError, TypeError, KeyError):
                        self.jube_const_params[k] = python_exp
                        parsed_data.append((k, str(python_exp)))
                else:
                    temp_hash.update({k:python_exp})
            variable_hash = temp_hash
        return parsed_data

    def val_repl(self, matchobj):
        """
        TODO
        """
        match_variable_name = re.match(r'^\.*\$(\w+)\.*|^\.*\$\{(\w+)\\}\.*',\
                                       matchobj.group(0)).group(1, 2)
        name = [x for x in match_variable_name if x is not None][0]
        if name in self.jube_const_params:
            return str(self.jube_const_params[name])
        else:
            return matchobj.group(0)
