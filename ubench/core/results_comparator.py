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
import os
import pandas as pd
import ubench.data_store.data_store_yaml as dsy

class ResultsComparator:
    
  def __init__(self,context_field_list,result_field_list):
    """ Constructor """
    self.context_fields=context_field_list
    self.context_fields_extended=context_field_list
    self.result_field_list=result_field_list
    self.dstore=dsy.DataStoreYAML()

  def print_comparison(self,result_directories):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'expand_frame_repr', False):
      print(self.compare(result_directories))

  def compare(self,result_directories):

    #result_name_column = 'hpcc_bench'

    pandas=self.build_pandas(result_directories)
    panda_pre=pandas[0]
    panda_post=pandas[1]

    if panda_pre.empty or panda_post.empty:
      return "No corresponding results found, comparison is not possible"

    for key_f in self.context_fields_extended:
      if key_f not in panda_pre or key_f not in panda_post:
        print('    '+str(key_f)+\
              ' is not a valid context field, valid context fields for given directories are :')
        for cfield in panda_pre:
          print('     - '+str(cfield))
        return "No result"

    result_columns_pre_merge=[ x for x in list(panda_pre.columns.values) if x not in self.context_fields_extended]
    pd_compare=pd.merge(panda_pre,panda_post,how="inner",on=self.context_fields_extended,suffixes=['_pre', '_post'])
    pd_compare_columns_list=list(pd_compare.columns.values)

    result_columns=[ x for x in pd_compare_columns_list if x not in self.context_fields_extended]
        
    context_first_columns_list= self.context_fields_extended
    pd_compare=pd_compare[context_first_columns_list+result_columns]

    # Convert numeric columns to float
    for ccolumn in self.context_fields_extended:
      try:
        pd_compare[ccolumn]=(pd_compare[ccolumn].apply(lambda x: float(x)))
      except:
        continue
      
    # Add a difference in % for numeric result columns
    for rcolumn in result_columns_pre_merge:
      pre_column=rcolumn+'_pre'
      post_column=rcolumn+'_post'
      try:
        pd_compare[rcolumn+' diff(%)']=((pd_compare[post_column].apply(lambda x: float(x))-pd_compare[pre_column].apply(lambda x: float(x)))*100)/pd_compare[pre_column].apply(lambda x: float(x))
      except:
        continue
    
    return(pd_compare.sort(context_first_columns_list).to_string(index=False))



  def _dir_to_data(self,result_dir):
    data_files=[]
    data_list=[]
    dstore=dsy.DataStoreYAML()

    for (dirpath, dirnames, filenames) in os.walk(result_dir):
      for fname in filenames:
        data_files.append(os.path.join(dirpath,fname))
        
    for dfile in data_files:
      try:
        dstore.load(dfile)
        data_list.append((dstore.runs_info,dstore.metadata))
      except Exception, e:
        print(dfile+" is not a data file and will be ignored : "+str(e))

    return data_list

  def build_pandas(self,result_directories):
    pandas_list=[]
    for result_dir in result_directories:
      pandas_list.append(self._data_to_pandas(self._dir_to_data(result_dir)))

    return pandas_list

  def _data_to_pandas(self,data_list):

    report_info={}
          
    if not data_list:
      # return empty DataFrame
      return pd.DataFrame()
  
    # Choose context fields as an intersection of context fields found in results
    first=True
    for data_b,metadata_b in data_list:
      for id_exec in sorted(data_b.keys()): # this guarantees the order of nodes
        if first:
          context_columns=set(data_b[id_exec]['context_fields'])
        else:
          first=False
          context_columns=context_columns.intersection(set(data_b[id_exec]['context_fields']))

    # Add custom context_columns
    if self.context_fields:
      for key in self.context_fields:
        context_columns=set(self.context_fields)

    if not(self.context_fields):
      self.context_fields=list(context_columns)
    else:
      for key in self.context_fields:
        context_columns.add(key)

    context_columns=list(context_columns)

    result_name_column=None
    
    for data_b,metadata_b in data_list:
      for id_exec in sorted(data_b.keys()): # this guarantees the order of nodes
        if (len(data_b[id_exec]['results_bench'].items())>1):
          result_name_column=metadata_b['Benchmark_name']+'_bench'

    for column in context_columns+['result']:
      report_info[column] = []

    if result_name_column:
      report_info[result_name_column] = []

    for data_b,metadata_b in data_list:
      for id_exec in sorted(data_b.keys()): # this guarantees the order of nodes
        value = data_b[id_exec]
        # Only one value for bundle, multiple for hpcc
        for key, result in value['results_bench'].items():
          for column in context_columns:
            report_info[column].append(value[column])
            
          report_info['result'].append(result)
          if result_name_column:
            report_info[result_name_column].append(key)


    self.context_fields_extended=self.context_fields+[result_name_column]
    
    return(pd.DataFrame(report_info))

        


