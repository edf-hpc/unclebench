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
import getpass, time, os, urllib2
from urlparse import urlparse,urljoin
from subprocess import Popen,PIPE
import shutil

class Fetcher():

  def __init__(self, resource_dir = "", benchmark_name="",calibre_user =getpass.getuser()):
    self.calibre_user= calibre_user
    self.calibre_password=""
    self.benchmark_name = benchmark_name
    self.resource_dir = resource_dir


  def get_credentials(self):
    print 'Enter calibre password for user: ' + self.calibre_user
    self.calibre_password=getpass.getpass()
    print ''

  def parse_env_variable(self,path):
    new_path = os.popen("echo " + path).read().strip()
    return new_path

  def svn_checkout(self,url,files,revision=None):
    fetch_message = 'Fetching benchmark {0} from SVN:'.format(self.benchmark_name)
    print fetch_message
    print '-'*len(fetch_message)
    self.get_credentials()

    # create directory svn if it does not exist
    if revision is None:
      revision = [-1]

    for rev in revision:
      if rev is -1:
        benchresource_dir=os.path.join(self.resource_dir,self.benchmark_name,"svn")
      else:
        benchresource_dir=os.path.join(self.resource_dir,self.benchmark_name,"svn",rev)

      if not os.path.exists(benchresource_dir):
        os.makedirs(benchresource_dir)

      for file_bench in files:
        urlparsed = urlparse(url)
        if not os.path.isabs(file_bench):
          file_bench ="/"+file_bench
        url_file=urljoin(url,urlparsed.path+file_bench)
        base_name = os.path.basename(file_bench)
        svn_command = "svn export "
        if rev > 0:
          svn_command += "-r {0} ".format(rev)

        svn_command += "{0} {1} --username {2} --password '{3}' --trust-server-cert --non-interactive --no-auth-cache".format(url_file,base_name,self.calibre_user,self.calibre_password)
        print Popen(svn_command,cwd=benchresource_dir,stdout=PIPE,shell=True)
        svn_dir=os.path.join(self.resource_dir,self.benchmark_name,"svn")
        if rev > 0:
          dest_symlink = os.path.join(svn_dir,rev+"_"+base_name)
          if not os.path.exists(dest_symlink):
            os.symlink(os.path.join(svn_dir,rev,base_name),dest_symlink)

    print 'Benchmark {0} fetched'.format(self.benchmark_name)

  def local(self,files):
    fetch_message = 'Fetching benchmark {0} from local:'.format(self.benchmark_name)
    print fetch_message
    print '-'*len(fetch_message)
    benchresource_dir=os.path.join(self.resource_dir,self.benchmark_name)
    if not os.path.exists(benchresource_dir):
      os.mkdir(benchresource_dir)

    for file_bench in files:
      file_bench = self.parse_env_variable(file_bench)
      basename = os.path.basename(file_bench)
      print "Copying file: {0} into {1} ".format(basename,benchresource_dir)
      destfile_path=os.path.join(benchresource_dir,basename)
      shutil.copyfile(file_bench,destfile_path)

    print 'Benchmark {0} fetched'.format(self.benchmark_name)

  def https(self,url,files):

    # Connect to http server where benchmarks are located
    if(len(url.split(' '))>1):
      url_bench = url.split(' ')[0]
      self.get_credentials()
      self.__connect(url_bench,self.calibre_user,self.calibre_password)
      print "Connected to calibre"
    else:
      url_bench = url

    if not os.path.exists(self.resource_dir):
      os.makedirs(self.resource_dir)

    fetch_message = 'Fetching benchmark {0} from web:'.format(self.benchmark_name)
    print fetch_message
    print '-'*len(fetch_message)
    benchresource_dir=os.path.join(self.resource_dir,self.benchmark_name)
    if not os.path.exists(benchresource_dir):
      os.mkdir(benchresource_dir)

    for file_bench in files:

      path_bench = os.path.basename(file_bench)
      destfile_path=os.path.join(benchresource_dir,path_bench)
      downloaded=False
      num_retries = 0
      max_retries = 5
      while(num_retries < max_retries ):
        try:
          urlparsed = urlparse(url_bench)
          urlsrc=urljoin(url_bench,urlparsed.path+file_bench)
          destdir_path=os.path.dirname(destfile_path)
          if not os.path.exists(destdir_path):
            os.mkdir(destdir_path)

          self.__download(urlsrc,destfile_path)
        except urllib2.HTTPError as e:
          print '      HTTP Error '+str(e.code)+' downloading file '+urlsrc+' : '+e.reason
          print 'retrying ({0}/{1})'.format(num_retries,max_retries)
          num_retries+=1
        else:
          downloaded=True
          break

    if downloaded:
      print 'Benchmark {0} fetched'.format(self.benchmark_name)

  def __connect(self,url,username,password):
    """ Connect to a http server using authentification """
    proxy_handler = urllib2.ProxyHandler({})
    auth=urllib2.HTTPPasswordMgrWithDefaultRealm()

    auth.add_password(None,
                      url,
                      user=username,
                      passwd=password)

    handler=urllib2.HTTPBasicAuthHandler(auth)

    opener=urllib2.build_opener(proxy_handler,handler)
    urllib2.install_opener(opener)

  def __download(self,urlsrc,destfile_path):
    """ Download a file from an url or just do a standard copy if url is a
    path and not an url """

    print ''
    print '  Source: '+urlsrc
    print '  --> Destination: '+destfile_path

    try:
      file_src = urllib2.urlopen(urlsrc)

    except urllib2.HTTPError as e:
      raise
    else:
      file_dest=open(destfile_path,'w+')
      file_dest.write(file_src.read())
