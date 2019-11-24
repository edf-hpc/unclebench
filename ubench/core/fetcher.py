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
# pylint: disable=superfluous-parens
""" Implements fetcher class """


import getpass
import os
import shutil

from subprocess import Popen
from six.moves import urllib


class Fetcher(object):
    """ Methods to enable Unclebench functionality.

    Contains the methods necessary to collect benchmark files
    and assemble them into a local directory. Files can be downloaded
    from url's, git, svn or simply copied from local directory.

    Attributes:
        benchmark_name: string containing benchmark to be fetched
        resource_dir: where to store benchmarks source code
        login: credentials used to download benchmarks from scm
        password: credentials used to download benchmarks from scm
    """


    def __init__(self,
                 resource_dir='',
                 benchmark_name='',
                 login=getpass.getuser()):
        self.login = login
        self.password = ''
        self.benchmark_name = benchmark_name
        self.resource_dir = resource_dir


    def get_credentials(self):
        """ Internal method """

        print('Enter password for user: ' + self.login)
        self.password = getpass.getpass()
        print('')


    def parse_env_variable(self, path):  # pylint: disable=no-self-use
        """ Internal method """

        new_path = os.popen('echo ' + path).read().strip()
        return new_path


    def git_fetch(self,
                  url,
                  repo_name,
                  benchresource_dir,
                  commit=None,
                  branch=None):

        """ Internal method """
        # pylint: disable=no-self-use, too-many-arguments

        fetch_command = 'git clone '

        if branch:
            fetch_command += '--branch {0} '.format(branch)

        fetch_command += '--single-branch {0} '.format(url)

        if commit :
            git_dir = os.path.join(benchresource_dir, repo_name)
            fetch_command += '; ( cd {0}; git reset --hard {1} )'.format(
                git_dir, commit)

        return fetch_command


    def svn_fetch(self,
                  url,
                  svn_file,
                  svn_login=None,
                  svn_password=None,
                  revision=''):

        """ Internal method """
        # pylint: disable=no-self-use, too-many-arguments

        print("ER: svn_fetch")
        fetch_command = 'svn export '
        if revision:
            fetch_command += '-r {0} '.format(revision)

        # pylint: disable=too-many-format-args
        svn_options = ['{url}',
                       '{svn_file}',
                       '--username {user}',
                       '--password \'{passw}\'',
                       '--trust-server-cert',
                       '--non-interactive',
                       '--no-auth-cache']
        fetch_command += ' '.join(svn_options).format(url=url,
                                                      svn_file=svn_file,
                                                      user=svn_login,
                                                      passw=svn_password)


        return fetch_command


    def scm_fetch(self,
                  url,
                  files,
                  scm_name='svn',
                  revision=[''],
                  branch=None,
                  do_cmds=None):
        """ Fetches benchmark resource files from SCM.

        Args:
            url: (list) where to download benchmark
            files: (list)
            scm_name: (string) name of the SCM system
            revision: (string) revision of the benchmark to download
            branch: (string) name of the branch to download benchmark
            do_cmds: (list) execute additional action after having downloaded the benchmark that
                     may be needed to install the benchmark
        """
        # pylint: disable=too-many-locals, too-many-arguments, too-many-branches

        fetch_message = 'Fetching benchmark {0} from {1}:'.format(
            self.benchmark_name, scm_name)
        print(fetch_message)
        print('-' * len(fetch_message))

        if scm_name == 'svn':
            self.get_credentials()

        # create scm directory if it does not exist
        for rev in revision:
            if rev:
                benchresource_dir = os.path.join(self.resource_dir,
                                                 self.benchmark_name, scm_name,
                                                 rev)
            else:
                benchresource_dir = os.path.join(self.resource_dir,
                                                 self.benchmark_name, scm_name)

            if not os.path.exists(benchresource_dir):
                os.makedirs(benchresource_dir)
            fetched = False

            for file_bench in files:
                urlparsed = urllib.parse.urlparse(url)
                if not os.path.isabs(file_bench):
                    file_bench = '/' + file_bench

                url_file = urllib.parse.urljoin(url,
                                                urlparsed.path + file_bench)
                base_name = os.path.basename(file_bench)

                fetch_command = ''
                if scm_name == 'svn':
                    fetch_command = self.svn_fetch(url_file, base_name,
                                                   self.login, self.password,
                                                   rev)

                elif scm_name == 'git':

                    # Get the name of the global repository
                    benchs_name = os.path.join(
                        url.split('/')[-1].split('.')[0])

                    fetch_command = self.git_fetch(url, benchs_name,
                                                   benchresource_dir, rev,
                                                   branch)
                if not fetched:
                    # Execute the fetch command just one time
                    fetch_process = Popen(fetch_command,
                                          cwd=benchresource_dir,
                                          shell=True,
                                          universal_newlines=True)
                    fetch_process.wait()
                    fetched = True

                fetch_dir = os.path.join(self.resource_dir,
                                         self.benchmark_name, scm_name)

                # Create symbolic link to the file bench with its full path
                if rev:
                    dest_symlink = os.path.join(fetch_dir,
                                                rev + '_' + base_name)
                    if not os.path.exists(dest_symlink):
                        os.symlink(
                            os.path.join(benchresource_dir + file_bench),
                            dest_symlink)

                # Check if the files exist in the directory
                if not os.path.isdir(
                        os.path.join(benchresource_dir + file_bench)):
                    print('WARNING :',
                          os.path.join(benchresource_dir + file_bench),
                          ' does not exist')

                # execute actions from do tags
                if do_cmds:
                    for do_cmd in do_cmds:
                        do_process = Popen(do_cmd,
                                           cwd=os.path.join(
                                               benchresource_dir,
                                               file_bench[1:]),
                                           shell=True,
                                           universal_newlines=True)
                        do_process.wait()

        print('Benchmark {0} fetched'.format(self.benchmark_name))

    def local(self, files, do_cmds=None):
        """ Fetches benchmark resource files

        Args:
            files: () list
            do_cmds: (list) execute additional action after having downloaded the benchmark that
                            may be needed to install the benchmark.
        """

        fetch_message = 'Fetching benchmark {0} from local:'.format(
            self.benchmark_name)
        print(fetch_message)
        print('-' * len(fetch_message))
        benchresource_dir = os.path.join(self.resource_dir,
                                         self.benchmark_name)
        if not os.path.exists(benchresource_dir):
            os.mkdir(benchresource_dir)

        for file_bench in files:
            file_bench = self.parse_env_variable(file_bench)
            basename = os.path.basename(file_bench)
            print('Copying file: {0} into {1} '.format(basename,
                                                       benchresource_dir))
            destfile_path = os.path.join(benchresource_dir, basename)
            shutil.copyfile(file_bench, destfile_path)

        if do_cmds:
            for do_cmd in do_cmds:
                do_process = Popen(do_cmd,
                                   cwd=benchresource_dir,
                                   shell=True,
                                   universal_newlines=True)
                do_process.wait()

        print('Benchmark {0} fetched'.format(self.benchmark_name))


    def https(self, url, files):
        """ Fetches benchmark resource files using https protocol

        Args:
            url: (string) containing path to files
            files: (list) of files to be downloaded
        """
        # pylint: disable=too-many-locals

        # Connect to http server where benchmarks are located
        if len(url.split(' ')) > 1:
            url_bench = url.split(' ')[0]
            self.get_credentials()
            self.__connect(url_bench, self.login, self.password)
            print('Connected')
        else:
            url_bench = url

        if not os.path.exists(self.resource_dir):
            os.makedirs(self.resource_dir)

        fetch_message = 'Fetching benchmark {0} from web:'.format(
            self.benchmark_name)
        print(fetch_message)
        print('-' * len(fetch_message))
        benchresource_dir = os.path.join(self.resource_dir,
                                         self.benchmark_name)
        if not os.path.exists(benchresource_dir):
            os.mkdir(benchresource_dir)

        for file_bench in files:

            path_bench = os.path.basename(file_bench)
            destfile_path = os.path.join(benchresource_dir, path_bench)
            downloaded = False
            num_retries = 0
            max_retries = 5
            while num_retries < max_retries:
                try:
                    urlparsed = urllib.parse.urlparse(url_bench)
                    urlsrc = urllib.parse.urljoin(url_bench,
                                                  urlparsed.path + file_bench)
                    destdir_path = os.path.dirname(destfile_path)
                    if not os.path.exists(destdir_path):
                        os.mkdir(destdir_path)

                    self.__download(urlsrc, destfile_path)
                except urllib.error.HTTPError as err:
                    print('      HTTP Error ' + str(err.code) +
                          ' downloading file ' + urlsrc + ' : ' + err.reason)
                    print('retrying ({0}/{1})'.format(num_retries,
                                                      max_retries))
                    num_retries += 1
                else:
                    downloaded = True
                    break

        if downloaded:
            print('Benchmark {0} fetched'.format(self.benchmark_name))


    def __connect(self, url, username, password):
        """ Connect to a http server using authentification """
        # pylint: disable=no-self-use

        proxy_handler = urllib.request.ProxyHandler({})
        auth = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        auth.add_password(None, url, user=username, passwd=password)

        handler = urllib.request.HTTPBasicAuthHandler(auth)

        opener = urllib.request.build_opener(proxy_handler, handler)
        urllib.request.install_opener(opener)  # pylint: disable=too-many-function-args


    def __download(self, urlsrc, destfile_path):
        """ Download a file from an url or just do a standard copy if url is a
        path and not an url """
        # pylint: disable=no-self-use

        print('')
        print('  Source: ' + urlsrc)
        print('  --> Destination: ' + destfile_path)

        try:
            file_src = urllib.request.urlopen(urlsrc)

        except urllib.error.HTTPError as err:  # pylint: disable=unused-variable
            raise
        else:
            file_dest = open(destfile_path, 'w+')
            file_dest.write(file_src.read())
