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

class UbenchComparator:

  def __init__(self,context_fields_list=None,additional_fields_list=None,threshold=None):
    """ Constructor """
    self.context_fields=context_fields_list
    self.additional_fields=additional_fields_list
    self.dstore=dsy.DataStoreYAML()
    self.threshold=threshold


    

  def print_comparison(self,result_directories):

    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'expand_frame_repr', False):
      print(self.compare(result_directories))

  def compare(self,result_directories):
    """
    compare results of each result_directory, first directory is considered to contain reference results
    """
    # Build pandas and retrieve associated context fields from result directories
    pandas_and_context=self.build_pandas(result_directories)
    pandas=[item[0] for item in pandas_and_context]

    if not pandas:
      return("No ubench results data found in given directories or not well-formated data")

    if all(panda.empty for panda in pandas):
      return("")  

    # Get intesection of all context fields found in data files
    context_fields=list(set.intersection(*map(set,[item[1] for item in pandas_and_context ])))
    panda_ref=pandas[0]

    for key_f in context_fields:
      if key_f not in panda_ref:
        print('    '+str(key_f)+\
              ' is not a valid context field, valid context fields for given directories are:')
        for cfield in panda_ref:
          print('     - '+str(cfield))
        return "No result"

    result_columns_pre_merge=[ x for x in list(panda_ref.columns.values) if x not in context_fields]

    # Do all but last merges keeping the original result field name unchanged
    idx=0
    pd_compare=panda_ref
    for pdr in pandas[1:-1]:
      pd_compare=pd.merge(pd_compare,pdr,on=context_fields,suffixes=['', '_post_'+str(idx)])
      idx+=1

    # At last merge add a _pre suffix to reference result
    if len(pandas)>1:
      pd_compare=pd.merge(pd_compare,pandas[-1],on=context_fields,suffixes=['_pre', '_post_'+str(idx)])
    else:
      pd_compare=panda_ref

    pd_compare_columns_list=list(pd_compare.columns.values)

    result_columns=[ x for x in pd_compare_columns_list if x not in context_fields]

    ctxt_columns_list= context_fields

    if "nodes" in ctxt_columns_list:
      ctxt_columns_list.insert(0, ctxt_columns_list.pop(ctxt_columns_list.index("nodes")))

    pd_compare=pd_compare[ctxt_columns_list+result_columns]

    pd.options.mode.chained_assignment = None # avoid useless warning
    # Convert numeric columns to float
    for ccolumn in context_fields:
      try:
        pd_compare[ccolumn]=pd_compare[ccolumn].apply(lambda x: float(x))
      except:
        continue

    # Add difference columns in % for numeric result columns
    diff_columns=[]

    for rcolumn in result_columns_pre_merge:
      pre_column=rcolumn+'_pre'
      for i in range(0,len(pandas[1:])):
        post_column=rcolumn+'_post_'+str(i)
        try:
          diff_column_name=rcolumn+'_diff_'+str(i)#+'(%)'
          pd_compare[diff_column_name]=((pd_compare[post_column].apply(lambda x: float(x))-pd_compare[pre_column].apply(lambda x: float(x)))*100)/pd_compare[pre_column].apply(lambda x: float(x))
        except:
          continue
        else:
          diff_columns.append(diff_column_name)

    # Remove rows with no difference above given threshold
    if self.threshold:
      # Add a column with max :
      pd_compare['max_diff']=pd_compare[diff_columns].max(axis=1).abs()
      # Use it as a filter :
      pd_compare=pd_compare[ pd_compare.max_diff > float(self.threshold)]
      pd_compare.drop('max_diff', 1,inplace=True)


    pd.options.mode.chained_assignment = 'warn' #reactivate warning


    return(pd_compare.sort(ctxt_columns_list).to_string(index=False))


  def _dir_to_data(self,result_dir):
    data_files=[]
    data_list=[]
    dstore=dsy.DataStoreYAML()

    if not os.path.isdir(result_dir):
      print("Cannot find "+result_dir+" directory")
      exit(1)

    for (dirpath, dirnames, filenames) in os.walk(result_dir):
      for fname in filenames:
        data_files.append(os.path.join(dirpath,fname))

    for dfile in data_files:
      dstore.load(dfile)
      if (dstore.runs_info):
        data_list.append((dstore.runs_info,dstore.metadata))

    return data_list

  def build_pandas(self,result_directories):
    pandas_list=[]
    for result_dir in result_directories:
      data_dic=self._dir_to_data(result_dir)
      if(data_dic):
        pandas_list.append(self.dstore.data_to_pandas(data_dic,self.context_fields,self.additional_fields))

    return pandas_list
