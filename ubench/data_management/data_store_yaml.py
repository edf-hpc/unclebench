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
""" Provides DataStoreYAML class """


import yaml
from . import data_store
import collections
from yaml.representer import Representer

class DataStoreYAML(data_store.DataStore):
    """ Provides methods to load and write configuration from and to YAML files

    Methods:
        write(metadata, runs_info, output_file)
        load(input_file)
    """


    def __init__(self):
        """ Class constructor """
        data_store.DataStore.__init__(self)
        yaml.add_representer(collections.defaultdict, Representer.represent_dict)

    def write(self, metadata, runs_info, output_file):
        """

        Args:
            metadata
            runs_info
            output_file
        """

        with open(output_file, 'w') as outfile:
            benchdata = metadata
            benchdata['runs'] = runs_info
            yaml.dump(benchdata, outfile, default_flow_style=False)


    def load(self, input_file):
        """ Loads YAML configuration to dictionary

        Args:
            input_file (str): YAML file
        """

        metadata = None
        runs_info = None

        with open(input_file, 'r') as inputfile:
            try:
                data = yaml.load(inputfile)
                runs_info = data['runs']
                data.pop('runs', None)
                metadata = data
            except Exception as e:  # pylint: disable=invalid-name, broad-except, unused-variable
                data = None
                runs_info = None
                metadata = None

        return(metadata, runs_info)
