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

import data_store
import yaml

class DataStoreYAML(data_store.DataStore):

  def __init__(self,metadata,runs_info):
    data_store.DataStore.__init__(self,metadata,runs_info)

  def write(self, output_file):
    with open(output_file, 'w') as outfile:
      benchdata = self.metadata
      benchdata['runs'] = self.runs_info
      yaml.dump(benchdata, outfile, default_flow_style=False)

  def load(self,input_file):
    with open(input_file, 'w') as inputfile:
      yaml.load(inputfile)
