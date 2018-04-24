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

import pandas as pd

class DataStore():

  def __init__(self,metadata,runs_info):

    self.metadata = metadata
    self.runs_info = runs_info

  def write(self, output_file):
    pass

  def load(self,input_file):
    pass
    
  def data_to_pandas(self,data_list,context_fields_filter=None,additional_fields=None):
    """
    context fields are read in data files but fields can be given as argument to select
    only part of available fields.
    Return a tuple (context_list,panda) 
    """
    report_info={}

    if not additional_fields:
      additional_fields=[]
          
    if not data_list:
      # return empty DataFrame
      return (pd.DataFrame(),[])
  
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
    if context_fields_filter:
      context_columns=context_fields_filter
    else:
      context_fields_filter=list(context_columns)
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

    for res in additional_fields:
      if res in context_columns:
        print("Error : {} is part of the context and is also a result field, cannot interpret data.".format(res))
        # return empty DataFrame
        return(pd.DataFrame(),[])
        

    for data_b,metadata_b in data_list:
      for id_exec in sorted(data_b.keys()): # this guarantees the order of nodes
        value = data_b[id_exec]
        # Only one value for hpl, multiple for hpcc
        for key, result in value['results_bench'].items():
          for column in context_columns+additional_fields:
            if column in value:
              if not column in report_info:
                report_info[column]=[]
              report_info[column].append(value[column])
            
          report_info['result'].append(result)
          if result_name_column:
            report_info[result_name_column].append(key)

    if result_name_column:
      return(pd.DataFrame(report_info),context_fields_filter+[result_name_column])
    else:
      return(pd.DataFrame(report_info),context_fields_filter)

    
    
    

