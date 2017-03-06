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
import os,sys
import re
from subprocess import call, Popen, PIPE
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import ubench.benchmark_managers.graphical_benchmark_manager as gbm

class LocalBenchmarkManager(gbm.GraphicalBenchmarkManager):

    def __init__(self,benchmark_name,platform):
        """ Constructor """
        gbm.GraphicalBenchmarkManager.__init__(self,benchmark_name,platform)
        self.title='IOR'
        self.description='IOR is a parallel file systems benchmark.'
        self.print_array=False
        self.print_transposed_array=False
        self.print_plot=True
        self.plot_list=[0,1] # Plot one graph for each benchmark


    def plot(self,output_file,transfer_idx):
        """  Plots IOR performances and returns a title and a legend"""
        self.format_input([3,4],5,keep_nthocc_from_field=(2,transfer_idx)) # Gather results for a single transfer size
        fig = plt.figure(figsize=(14,6))
        ax = fig.add_subplot(111); ax.set_position([0.1,0.1,0.5,0.8])

        if self.nb_variants>0:
            self.build_lines(ax) # Plot lines
   #         self.build_legend(ax,"Nodes","Bandwidth MiB/s",'Write and read speed transfering chunks of size '+str(self.filtered_field_value)+' Mbytes')
            self.build_legend(ax,"Nodes","Bandwidth MiB/s",'')
        fig.savefig(output_file)

        return ('Xfer size : '+str(self.filtered_field_value)+' Mbytes',
                'IOR benchmark bandwidth (xfersize: '+str(self.filtered_field_value)+' Mbytes)')
