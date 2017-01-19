#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright (C) 2015 EDF SA                                                 #
#                                                                            #
#  This file is part of UncleBench                                           #
#                                                                            #
#  This software is governed by the CeCILL license under French law and      #
#  abiding by the rules of distribution of free software. You can use,       #
#  modify and/ or redistribute the software under the terms of the CeCILL    #
#  license as circulated by CEA, CNRS and INRIA at the following URL         #
#  "http://www.cecill.info".                                                 #
#                                                                            #
#  As a counterpart to the access to the source code and rights to copy,     #
#  modify and redistribute granted by the license, users are provided only   #
#  with a limited warranty and the software's author, the holder of the      #
#  economic rights, and the successive licensors have only limited           #
#  liability.                                                                #
#                                                                            #
#  In this respect, the user's attention is drawn to the risks associated    #
#  with loading, using, modifying and/or developing or reproducing the       #
#  software by the user in light of its specific status of free software,    #
#  that may mean that it is complicated to manipulate, and that also         #
#  therefore means that it is reserved for developers and experienced        #
#  professionals having in-depth computer knowledge. Users are therefore     #
#  encouraged to load and test the software's suitability as regards their   #
#  requirements in conditions enabling the security of their systems and/or  #
#  data to be ensured and, more generally, to use and operate it in the      #
#  same conditions as regards security.                                      #
#                                                                            #
#  The fact that you are presently reading this means that you have had      #
#  knowledge of the CeCILL license and that you accept its terms.            #
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

     
