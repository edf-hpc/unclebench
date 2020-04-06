# -*- coding: utf-8 -*-
##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2019 EDF SA                                           #
#                                                                            #
#  UncleBench is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by      #
#  the Free Software Foundation, either version 3 of the License, or         #
#  (at your option) any later version.                                       #
#                                                                            #
#  UncleBench is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU General Public License for more details.                              #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with UncleBench. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                            #
##############################################################################
""" Jube benchmarking API module """

import os
import re
import csv
import tempfile
import time
import hashlib
from subprocess import Popen, PIPE
from collections import defaultdict
import ubench.utils as utils
import ubench.data_management.data_store_yaml as data_store_yaml
from ubench.core.ubench_config import UbenchConfig
from ubench.benchmarking_tools_interfaces.benchmarking_api import BenchmarkingAPI

# from ubench.benchmark_interface.benchmark_api import BenchmarkAPI
from . import jube_xml_parser

import ubench.scheduler_interfaces.slurm_interface as slurmi

#pylint: disable=superfluous-parens
class JubeBenchmarkingAPI(BenchmarkingAPI):
    """ Jube benchmarking API class implements abstract class benchmarkingAPI
    to use Jube backend.

    Methods:
        analyse
        analyse_last
        get_results_root_directory
        get_log
        get_status_info
        write_bench_data
        extract_results
        extract_results_last
        run
        set_custom_nodes
        list_parameters
        set_parameter
        get_bench_rundir
        parse_jube_parameter
        val_repl
    """


    def __init__(self, benchmark, platform):
        """ Class constructor

        Args:
            benchmark (str): name of the benchmark
            platform (str): name of the platform
        """
        self.benchmark = benchmark
        self.platform = platform
        self.benchmark_dir = os.path.join(UbenchConfig().benchmark_dir,
                                          benchmark)

        self.benchmark_path = os.path.join(UbenchConfig().run_dir,
                                           platform,
                                           benchmark)

        self.jube_const_params = {}
        self._jube_files = None
        self.results = {}
        self.results_file = None

    @property
    def jube_files(self):
        """ Jube files getter"""
        if not self._jube_files:
            benchmark_files = [file_b for file_b in os.listdir(self.benchmark_dir)
                               if file_b.endswith('.xml')]
            self._jube_files = jube_xml_parser.JubeXMLParser(self.benchmark_dir,
                                                             benchmark_files,
                                                             self.benchmark_path,
                                                             UbenchConfig().platform_dir)

        return self._jube_files


    def result(self, benchmark_id):
        """ Generate and print results
        Args:
             (int) benchmark_id: id of the benchmark

        Returns:
            (list) numeric results

        Raises:
            IOError
        """

        outpath = self.jube_files.get_bench_outputdir()
        benchmark_results_path = os.path.join(self.benchmark_path, outpath,
                                              self.get_bench_rundir(benchmark_id,
                                                                    outpath))

        if not os.path.isdir(benchmark_results_path):
            print("""----!Error: benchmark run directory {}
            does not exist""".format(benchmark_results_path))
            raise IOError

        print('----analysing {0} results'.format(self.benchmark))
        self._analyse(benchmark_id)
        print('----extracting results')
        print('----benchmark results path: {0}'.format(benchmark_results_path))
        results_array = self._extract_results(benchmark_id)
        print("""---- writing benchmark data in:
         {0}/bench_results.yaml""".format(benchmark_results_path))
        self.results = self._write_bench_data(benchmark_id)

        return results_array


    def _analyse(self, benchmark_id):
        """ Analyze benchmark results

        Args:
            benchmark_id (int): id of the benchmark to be analyzed

        Returns:
            (str) Result directory absolute path
        Raises:
            RuntimeError
        """

        outpath = self.jube_files.get_bench_outputdir()

        # Continue benchmark steps that were not already executed.
        # This is often mandatory to execute postprocessing steps.
        cmd_str = 'jube continue --hide-animation {} --id {}'.format(outpath,
                                                                     benchmark_id)
        ret_code, _, stderr = utils.run_cmd(cmd_str, self.benchmark_path)

        if ret_code:
            print(stderr)
            msg = "Error when executing command: {}".format(cmd_str)
            raise RuntimeError(msg)

        cmd_str = 'jube analyse {} --id {}'.format(outpath, benchmark_id)
        ret_code, _, stderr = utils.run_cmd(cmd_str, self.benchmark_path)

        if ret_code:
            print(stderr)
            msg = "Error when executing command: {}".format(cmd_str)
            raise RuntimeError(msg)


    def get_log(self, idb=-1):  # pylint: disable=too-many-locals
        """ Get a log from a benchmark run

        Args:
            idb (int): id of the benchmark

        Returns:
            (str) log
        """
        out_path = os.path.join(self.benchmark_path,
                                self.jube_files.get_bench_outputdir())
        # If idb equals -1 get highest id directory found in out_dir
        if idb == -1:
            dir_list = []
            newest_result_dir = None

            for fd in os.listdir(out_path):  # pylint: disable=invalid-name
                result_dir = os.path.join(out_path, fd)
                if os.path.isdir(result_dir):
                    dir_list.append(result_dir)

            newest_result_dir = max(dir_list, key=os.path.getmtime)
            idb_s = newest_result_dir
        else:
            idb_s = str(idb).zfill(6)

        # Padding ID with zeros to reach a 6 length id to get Jube run directory path.
        run_path = os.path.join(out_path, idb_s)

        # Standard log files to look for
        log_files = ['stdout', 'stderr', 'run.log']
        jube_xml_config = self._get_jubexmlconfig(idb_s)
        # Get job errlog and outlog filenames from configuration.xml file
        log_files += jube_xml_config.get_job_logfiles()

        # Get filenames that are used for analyse from configuration.xml file
        log_files += jube_xml_config.get_analyse_files()

        # Concatenante evry files that are considered as log file and order them
        # with the last modified file at the last position.
        result = ''
        log_files_found = []
        for root, dirs, files in os.walk(run_path):  # pylint: disable=unused-variable
            for f in files:  # pylint: disable=invalid-name
                if f in log_files:
                    log_files_found.append(os.path.join(root, f))

        for fpath in sorted(log_files_found, key=os.path.getmtime):
            result += '========= '+fpath+' =========\n'
            with open(fpath, 'r') as log_file:
                result += log_file.read()+'\n'

        return '\n-------------------------------------------------------\n'\
            +'==== Log for {0} benchmark. (run ID = {1})  ==== \n'\
            .format(self.benchmark, os.path.basename(idb_s))\
            +'-------------------------------------------------------\n\n'\
            +result


    def get_status_info(self, benchmark_id):
        """ Get the status for a benchmark run

        Args:
            benchmark_id (int): id of the benchmark

        Returns:
            (dict) global_status
        """

        outpath = self.jube_files.get_bench_outputdir()

        if not os.path.isdir(self.benchmark_path):
            raise IOError

        os.chdir(self.benchmark_path)

        bench_steps = self.jube_files.get_bench_steps()

        global_status = {}
        for step in bench_steps:
            # Updating state with continue command
            # countinue_str = 'jube continue --hide-animation
            cmd_str = 'jube continue --hide-animation {} --id {}'.format(outpath, benchmark_id)
            continue_cmd = Popen(cmd_str, cwd=os.getcwd(),
                                 stdout=open(os.devnull, 'w'), shell=True,
                                 universal_newlines=True)
            continue_cmd.wait()
            input_str = 'jube info {} --id {} --step {}'.format(outpath, benchmark_id, step)
            status_from_jube = Popen(input_str, cwd=os.getcwd(), shell=True, stdout=PIPE,
                                     universal_newlines=True)
            global_status[step] = []
            for line in status_from_jube.stdout:
                if re.search(r'^\s+\d+\s+\|\s+\w+\s+\|.*', line):
                    raw_values = [c.strip() for c in line.split('|')]
                    task = {}
                    task['id'] = raw_values[0]
                    task['started'] = raw_values[1]
                    task['done'] = raw_values[2]
                    task['workdir'] = raw_values[3]
                    global_status[step].append(task)

        return global_status

    def _write_bench_data(self, benchmark_id): # pylint: disable=too-many-locals
        """ Generates benchmarks results data

        Args:
            benchmark_id (int): id of the benchmark

        Returns:
            (dict) mapping between Jube execution directories and result values
        """

        outpath = self.jube_files.get_bench_outputdir()
        benchmark_rundir = self.get_bench_rundir(benchmark_id, outpath)
        context_names, context = self._get_execution_context(benchmark_id)
        results, field_names = self._get_results(benchmark_rundir, context_names)
        scheduler_interface = slurmi.SlurmInterface()
        common_fields = [n for n in context_names if n in field_names]
        map_dir = {}
        for exec_id, values in context.items():
            key_results = hashlib.md5("".join([values[n] for n in common_fields]))
            context[exec_id]['results_bench'] = results[key_results.hexdigest()]
            context[exec_id]['context_fields'] = common_fields
            exec_dir = "{}_execute".format(values['jube_wp_id'].zfill(6))
            map_dir[exec_dir] = results[key_results.hexdigest()]
            job_file_path = os.path.join(values['jube_wp_abspath'], 'stdout')

            with  open(job_file_path, 'r') as job_file:
                for line in job_file:
                    re_result = re.findall(r'\d+', line)
                    if re_result:
                        job_id = re_result[0]
                        values['job_id_ubench'] = job_id
                        if scheduler_interface:
                            job_info = scheduler_interface.get_job_info(job_id)
                            if job_info:
                                values.update(job_info[-1])
                                context[exec_id].update(values)
                        break


        try:

            with open(os.path.join(benchmark_rundir, 'ubench.log'), 'r') as logf:
                field_pattern = re.compile('(.*) : (.*)')
                fields = field_pattern.findall(logf.read())
                metadata = {name.strip():val.strip() for name, val in fields}

        except IOError:
            metadata = {'Benchmark_name': self.benchmark,
                        'Date' : time.strftime("%c"),
                        'Platform' : self.platform,
                        'Run_directory' : benchmark_rundir,
                        'cmdline' : 'Campaign'}


        bench_data = data_store_yaml.DataStoreYAML()
        self.results_file = os.path.join(benchmark_rundir, 'bench_results.yaml')
        bench_data.write(metadata, context, self.results_file)

        return map_dir


    def _extract_results(self, benchmark_id):  # pylint: disable=too-many-locals
        """ Get result from a jube benchmark with its id and build a python result array

        Args:
            benchmark_id (int): id of the benchmark

        Returns:
            (str) result array
        """
        outpath = self.jube_files.get_bench_outputdir()
        benchmark_runpath = os.path.join(self.benchmark_path, outpath,
                                         self.get_bench_rundir(benchmark_id, outpath))

        jube_xml_config = self._get_jubexmlconfig(benchmark_id)

        cvsfile = jube_xml_config.get_result_cvsfile()

        cmd_str = 'jube result {} --id {} -o {}'.format(outpath,
                                                        benchmark_id,
                                                        cvsfile)

        _, stdout, _ = utils.run_cmd(cmd_str, self.benchmark_path)
        result_array = []
        cvs_data = csv.reader(stdout)

        with open(os.path.join(benchmark_runpath, 'result/ubench_results.dat'), 'w') as result_file:
            cvs_writer = csv.writer(result_file)
            for row in cvs_data:
                cvs_writer.writerow(row)

        jubecvsfile_path = os.path.join(benchmark_runpath, 'result', '{}.dat'.format(cvsfile))

        try:
            with open(jubecvsfile_path, 'r') as jubecsvfile:
                jubereader = csv.reader(jubecsvfile)
                for row in jubereader:
                    if isinstance(row, list):
                        result_array.append(row)
        except IOError:
            print('JUBE cvs file not found')  # pylint: disable=superfluous-parens

        return result_array


    def _get_execution_context(self, benchmark_id): # pylint: disable=no-self-use

        separator = "~"
        context = {}
        outpath = self.jube_files.get_bench_outputdir()
        jube_cmd = 'jube info ./{0} --id {1} --step execute -p -c \"{2}\"'.format(outpath,
                                                                                  benchmark_id,
                                                                                  separator)
        cmd_output = tempfile.TemporaryFile()
        result_from_jube = Popen(jube_cmd, cwd=self.benchmark_path,
                                 shell=True, stdout=cmd_output,
                                 universal_newlines=True)
        ret_code = result_from_jube.wait()  # pylint: disable=unused-variable

        # with cmd_output as out:
        cmd_output.flush()
        cmd_output.seek(0)
        jubereader = csv.DictReader(cmd_output, delimiter='~')
        context_names = jubereader.fieldnames
        for row in jubereader:
            if len(context_names) == len(row):
                context[row['id']] = row
            else:
                msg = """Error when reading jube info output
                This error is probably due to the chosen separator"""
                raise msg

        cmd_output.close()

        return (context_names, context)


    def _get_results(self, benchmark_rundir, context_names): # pylint: disable=too-many-locals

        result_file_path = os.path.join(benchmark_rundir, 'result/ubench_results.dat')
        results = {}
        field_names = []
        temp_list = {}
        with open(result_file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            field_names = reader.fieldnames
            # changing parameters for execution
            result_fields = [k for k in field_names if k not in context_names]

            for row in reader:

                md5 = hashlib.md5("".join([row[n] for n in context_names if n in field_names]))
                key = md5.hexdigest()
                values = {k:v for k, v in row.items() if k in result_fields}
                results[key] = values

                if key not in temp_list:
                    temp_list[key] = defaultdict(list)

                for k, v in values.items():
                    temp_list[key][k].append(v)

            for key in results:
                if len(temp_list[key][result_fields[0]]) > 1:
                    results[key] = temp_list[key]

        return (results, field_names)


    def run(self, opts):
        """ Run benchmark on a given platform and return the benchmark run directory path
        and a benchmark ID.

        Args:
            opts (int): options for run the benchmark

        Returns:
            (str) return absolute path of the benchmark result directory
        """

        # Modify bench xml
        self.jube_files.load_platform_xml(self.platform)
        updated_params = []
        if 'custom_params' in opts:
            if opts['custom_params']:
                updated_params = self.jube_files.set_params_bench(opts['custom_params'])
                updated_params += self.jube_files.set_params_platform(opts['custom_params'])


        if 'execute' in opts:
            if opts['execute']:
                self.jube_files.set_bench_execution()

        if 'w' in opts:
            if opts['w']:
                self._set_custom_nodes(opts['w'])


        platform_dir = self.jube_files.get_platform_dir()
        self.jube_files.add_bench_input()
        self.jube_files.remove_multisource()
        self.jube_files.set_platform_path(platform_dir)
        self.jube_files.write_bench_xml()
        self.jube_files.write_platform_xml()

        outpath = self.jube_files.get_bench_outputdir()
        abs_output_path = os.path.join(self.benchmark_path, outpath)

        j_job = JubeRun(self.benchmark, self.platform)
        j_job.run(abs_output_path, self.benchmark_path)

        if not j_job.result_path:
            raise RuntimeError('Error getting the directory number')

        return (j_job, updated_params)


    def _set_custom_nodes(self, nodes_list):
        """  Modify benchmark xml file to set custom nodes configurations.

        Args:
            nodes_list (list): list of tuples ex: [(6, None), (1, 'cn184'), (4, 'cn[380,431-433]')]
        """
        nodes_id_list = [name for num, name in nodes_list]
        nnodes_list = [num for num, name in nodes_list]

        self.jube_files.substitute_element_text('parameter', 'nodes', '.*', '$custom_nodes')
        if nodes_id_list:
            for subcmd in ['submit', '{submit}', 'submit_singleton', '{submit_singleton}']:
                self.jube_files.substitute_element_text('do', None,
                                                        re.escape('$' + subcmd + ' '),
                                                        '$custom_' + subcmd + ' ')

        # Add an xml section describing custom nodes configurations
        self.jube_files.add_custom_nodes_stub(nnodes_list, nodes_id_list)


    def list_parameters(self, default_values):
        """  List benchmark customisable parameters

        Args:
            default_values:

        Returns:
            (list) List of tuples [(param1,value),(param2,value),....]
        """

        platform_params = self.jube_files.get_params_platform(self.platform)
        benchmark_params = self.jube_files.get_params_bench()

        if default_values:
            eval_platform_params = self.parse_jube_parameter(platform_params)
            eval_benchmark_params = self.parse_jube_parameter(benchmark_params)
            parameters_list = {'platform' : eval_platform_params,
                               'benchmark' : eval_benchmark_params}
        else:
            parameters_list = {'platform' : platform_params,
                               'benchmark' : benchmark_params}

        return  parameters_list


    def get_bench_rundir(self, benchmark_id, outpath):
        """ Internal method  """

        path_id = 0
        abs_output_path = os.path.join(self.benchmark_path, outpath)

        if os.path.isdir(abs_output_path):
            if benchmark_id == 'last':
                path_id, _ = self.get_max_id(os.listdir(abs_output_path))
            else:
                path_id = benchmark_id

        return os.path.join(abs_output_path, str(path_id).zfill(6))


    def parse_jube_parameter(self, list_jube_parameters):  # pylint: disable=too-many-locals
        """ Internal method """

        # Get constants
        const_hash = {}
        variable_hash = {}
        parameter_regex_sub = '(?<!\\$)(?:\\$\\$)*\\$(?!\\$)(\\{)?(.+?)(?(1)\\}|(?:\\w+|$))'
        parameter_regex_find = '(?<!\\$)(?:\\$\\$)*\\$(?!\\$)(\\{)?(.+?)(?(1)\\}|(?:\\W|$))'
        external_variables = []

        for k, v in list_jube_parameters:  # pylint: disable=invalid-name

            # pylint: disable=unused-variable
            variables = [m2 for m1, m2 in re.findall(parameter_regex_find, v)]

            if variables:

                # pylint: disable=unused-variable
                if len(set(variables) & set([var for var, value in list_jube_parameters])) \
                   != len(set(variables)):

                    external_variables.append(k)
                elif set(variables) & set(external_variables):
                    external_variables.append(k)

        # pylint: disable=expression-not-assigned
        [const_hash.update({k:v}) for k, v in list_jube_parameters
         if not re.findall(parameter_regex_find, v)]

        # pylint: disable=expression-not-assigned
        [variable_hash.update({k:v}) for k, v in list_jube_parameters
         if re.findall(parameter_regex_find, v)]

        # We get rid of variables that cannot be resolved, mostly Jube
        for var in external_variables:
            variable_hash.pop(var)

        self.jube_const_params.update(const_hash)
        parsed_data = []

        while variable_hash:
            temp_hash = {}
            for k, v in variable_hash.items():  # pylint: disable=invalid-name
                python_exp = re.sub(parameter_regex_sub, self.val_repl, v)
                if not re.findall(parameter_regex_find, python_exp):
                    try:
                        python_eval = eval(python_exp)  # pylint: disable=eval-used
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
        """ Internal method """

        match_variable_name = re.match(r'^\.*\$(\w+)\.*|^\.*\$\{(\w+)\\}\.*',
                                       matchobj.group(0)).group(1, 2)

        name = [x for x in match_variable_name if x is not None][0]
        if name in self.jube_const_params:
            return str(self.jube_const_params[name])

        return matchobj.group(0)

    def _get_jubexmlconfig(self, benchmark_id):
        outpath = self.jube_files.get_bench_outputdir()
        benchmark_runpath = os.path.join(self.benchmark_path,
                                         outpath,
                                         self.get_bench_rundir(benchmark_id, outpath))

        configuration_file_path = os.path.join(benchmark_runpath, 'configuration.xml')

        try:
            jube_xml_config = jube_xml_parser.JubeXMLConfig(configuration_file_path)
        except IOError:
            raise IOError('Cannot find: '+configuration_file_path+' file.')

        return jube_xml_config


    @staticmethod
    def get_max_id(file_list): # pylint: disable=no-self-use
        """ Return max id directory"""
        max_id = -1
        ids_dict = {-1:'0000000'}
        if file_list:
            ids_dict = {int(id_str): id_str for id_str in file_list if id_str.isdigit()}
            max_id = max(ids_dict.keys())
        return max_id, ids_dict[max_id]


class JubeRun(object):
    """This class handles jube execution"""
    def __init__(self, benchmark, platform):
        self.benchmark = benchmark
        self.platform = platform
        self.jube_process = None
        self.result_path = None
        self.jubeid = None
        self._job_ids = []
        self._jube_returncode = None
        self._exec_dir = {}

    @property
    def job_ids(self):
        """ Returns the jobs id associated to a JubeRun"""
        if not self._job_ids:
            if self.jube_returncode == 0:
                job_ids = [j_id for j_id in self.extract_job_ids().values() if j_id.isdigit()]
                self._job_ids = job_ids
        return self._job_ids


    @property
    def exec_dir(self):
        if not self._exec_dir:
            if self.jube_returncode == 0:
                self._exec_dir = self.extract_job_ids()
        return self._exec_dir


    @property
    def jube_returncode(self):
        """Returns returned code of jube:
        if the process is running the value is None"""

        if not self._jube_returncode:
            self._jube_returncode = self.jube_process.poll()

        return self._jube_returncode


    def run(self, output_dir, benchmark_path):
        """ Execute benchmark"""
        max_id = None
        numdir = None

        if os.path.isdir(output_dir):
            max_id, _ = JubeBenchmarkingAPI.get_max_id(os.listdir(output_dir))

        input_str = 'jube run --hide-animation {}.xml --tag {}'.format(self.benchmark,
                                                                       self.platform)

        popen_obj = utils.run_cmd_bg(input_str, benchmark_path)

        while popen_obj.returncode is None:
            time.sleep(1)
            popen_obj.poll()
            new_id, numdir = JubeBenchmarkingAPI.get_max_id(os.listdir(output_dir))
            if new_id != max_id:
                break

        if popen_obj.returncode:
            stdout, stderr = popen_obj.communicate()
            msg = '''Error when executing command: {}
            stdout:
            --------
            {}
            stderr:
            --------
            {}'''.format(input_str, stdout, stderr)
            raise RuntimeError(msg)

        self.jubeid = new_id
        self.jube_process = popen_obj
        self.result_path = os.path.join(output_dir, numdir)


    def kill(self):
        """Kill jube process"""
        #Warning! by killing jube process we dont kill all child process
        self.jube_process.kill()


    def extract_job_ids(self):
        """ Get jobs' ids from directory"""
        ## we have to get the id directory elsewhere
        id_dir = self.result_path
        dir_exec_info = {}
        dir_exec_rex = re.compile(r'^\d{6}_execute$')
        job_id_rex = re.compile(r'^\w+\s\w+\s\w+\s(\d+)$')
        for files in os.listdir(id_dir):
            mat = dir_exec_rex.match(files)
            if mat:
                exec_dir = mat.group()
                dir_exec_info[exec_dir] = ""
                job_file_name = os.path.join(id_dir, mat.group(), "work", "stdout")
                with  open(job_file_name, 'r') as job_file:
                    for line in job_file:
                        job_mat = job_id_rex.match(line)
                        if job_mat:
                            dir_exec_info[exec_dir] = job_mat.group(1)
        return dir_exec_info
