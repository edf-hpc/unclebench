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


class SchedulerInterface:
    
     def __init__(self):
          """ Constructor """

     def get_available_nodes(self,slices_size=1):
          """ Returns a list of currently available nodes by slice of slices_size
          ex: for slices of size 4 ['cn[100-103]','cn[109,150-152]'].
          :param slices_size: slices size
          :param type: int
          :returns: list of nodes_id 
          :rtype: str """
          pass          

     def get_truncated_nodes_lists(self,nnodes_list,nodes_id):
          """ From a list of nodes number and a list of nodes id returns a list of nodes_id 
          truncated according to nodes number.
          :param nnodes_list: ex [2,4]
          :type nnodes_list: list of int
          :param nodes_id: ex ['cn[100-104]','cn[50-84]']
          :type nodes_id: list of str
          :returns: truncated node list ex: ['cn[100-101]','cn[50-53]']
          :rtype: list of str
          """
          pass

     def get_nnodes_from_string(self,nodes_id):
          """ From a string reprenting a set of nodes returns the number of nodes
          the set contains.
          :param nodes_id: nodes id
          :type nodes_id: str
          :returns: number of nodes  
          :rtype: int
          """
          pass

     
