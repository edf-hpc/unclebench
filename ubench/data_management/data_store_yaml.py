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
from collections import OrderedDict

class DataStoreYAML(data_store.DataStore):
    """
    Load Yaml to dictionnary / write dictionnary to Yaml files.
    """
    def __init__(self):
        data_store.DataStore.__init__(self)

    def write(self, metadata, runs_info, output_file):
        with open(output_file, 'w') as outfile:
          benchdata = metadata
          benchdata['runs'] = runs_info
          yaml.dump(benchdata, outfile, default_flow_style=False)

    def load(self, input_file):
        metadata=None
        runs_info=None
        with open(input_file, 'r') as inputfile:
            try:
                data = yaml.load(inputfile)
                runs_info = data['runs']
                data.pop('runs',None)
                metadata = data
            except Exception as e:
                data = None
                runs_info = None
                metadata = None
        return(metadata,runs_info)
