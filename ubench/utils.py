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
''' Provides useful methods '''

from subprocess import Popen, PIPE

def run_cmd(cmd_string, cwd, env=None):
    ''' Wrapper for Popen with communicate method '''
    cmd = Popen(cmd_string,
                cwd=cwd,
                shell=True,
                env=env,
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True)

    stdout, stderr = cmd.communicate()
    ret_code = cmd.returncode
    # we remove empty lines
    stdout_stream = [line for line in stdout.split('\n') if line]
    stderr_stream = [line for line in stderr.split('\n') if line]

    return ret_code, stdout_stream, stderr_stream

def run_cmd_bg(cmd_string, cwd, env=None):
    ''' Wrapper for Popen no blocking '''
    cmd = Popen(cmd_string,
                cwd=cwd,
                shell=True,
                env=env,
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True)

    return cmd

def get_bench_rundir(base_path, platform, benchmark, benchmark_id=None, fill=6):
    ''' Returns benchmark running directory up to the benchmark id

    If no benchmark_id is specified, returns the path to the last
    executed benchmark. It uses a base_path argument which prevents
    the loading of unclebench related classes (UbenchConfig in this case).

    The need for such funcionality is now beyond the scope of the
    execution of the benchmark itself and therefore it makes sense to
    have this function implemented outside JubeBenchmarkingAPI class.
    In future releases this functionality could cease to exist in
    JubeBenchmarkinkAPI class with small refactoring.

    Args:
        base_path (string)
        platform (string)
        benchmark (string)
        benchmark_id (integer, optional)
    Returns:
        string
    Example:
        `get_bench_rundir(base_path, ironman, hpl)` will return
        'base_path/ironman/hpl/benchmarkruns/000007' if 7 is
        the total number of hpl benchmarks executed in ironman.
    '''
    abs_path = os.path.join(base_path, platform, benchmark, 'benchmark_runs')

    if os.path.isdir(abs_path):
        if benchmark_id is None:
            dir_list = clean_list(os.listdir(abs_path))
            path_id = max(dir_list)
        else:
            path_id = benchmark_id
    else:
        print 'Could not find benchmarks directory'
        exit(1)

    return os.path.join(abs_path, str(path_id).zfill(fill))

def clean_list(dir_list):
    ''' Removes entries not matching six 6 digit strings

    Args:
        list of strings
    Returns:
        list of strings
    Example:
        clean_list(['000111', 'aaabcd'] -> ['000111']
    '''
    return [x for x in dir_list if re.match(r'[0-9]{6}$', x) is not None]

def trim_tail(path_string, count=1):
    ''' Returns path after having trimmed `count` directories in the end

    Args:
        path_string
        count - number of directories to remove
    Returns:
        string
    Example:
        trim_tail('/home/of/et', 2) -> '/home'
    '''
    for i in range(count):
        path_string = os.path.split(path_string)[0]
    return path_string

def trim_head(path_string, count=1):
    ''' Returns path after having trimmed initial `count` directories

    Args:
        path_string
        count - number of directories to remove
    Returns:
        string
    Example:
        trim_head('/home/of/et/the/alien', 2) -> 'et/the/alien'
    '''
    return os.sep.join(path_string.split(os.sep)[count+1:])

def mkdir(dir_name, abs_path=None, err_msg=None, ok_msg=None):
    ''' Creates directory

    If an absolute path is given, mkdir will append the directory `dir_name`
    at the end of this path. Otherwise, `dir_name` is assumed to be an
    absolute path.

    `dir_name` can be a directory tree.

    Args:
        dir_name - name of the directory (or tree) to be created.
        abs_path - location where to create the directory (or tree).
    Returns:
        boolean - status of operation
    Example:
        mkdir('/home/a') -> Will create the directory /home/a
        mkdir('b/c', '/home') -> Will create the directory /home/b/c
    '''
    def print_msg(msg):
        if abs_path is None:
            path = dir_name
        else:
            path = os.path.join(abs_path, dir_name)
        print(msg + ' : {}'.format(path))
        
    try:
        if abs_path:
            os.chdir(abs_path)
        os.makedirs(dir_name)
    except OSError:
        print_msg('Unable to create directory')
        if err_msg is not None:
            print err_msg
        exit(1)
    else:
        print_msg('Directory created')
        if ok_msg is not None:
            print ok_msg
        result = True

    return result
