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

import sys
import re
from subprocess import call, Popen, PIPE
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import ubench.benchmark_managers.benchmark_manager as bm
import matplotlib.patches as mpatches
import itertools

class GraphicalBenchmarkManager(bm.BenchmarkManager):

    def __init__(self,benchmark_name,benchmark_path):
        """ Constructor """
        bm.BenchmarkManager.__init__(self,benchmark_name,benchmark_path)
        self.list_variants=[]
        self.list_nodes=[]
        self.plot_handles=[]
        self.rects_list=[]
        self.field_legends=[]
        self.env_legends=[]
        self.fields={}
        self.nb_variants=0
        self.nb_nodes=0
        self.nb_fields=0
        self.filtered_field_value=None

    def clear_input_formating(self):
        """ Clear data associated to the graphical manager. Need a call to format_input
        to collect new ones."""
        del self.list_variants[:]
        del self.list_nodes[:]
        del self.plot_handles[:]
        del self.rects_list[:]
        del self.field_legends[:]
        del self.env_legends[:]
        self.fields.clear()
        self.nb_variants=0
        self.nb_nodes=0
        self.nb_fields=0
        self.filtered_field_value=None

    def keep_nth_occurence_from_field(self,id_column,nth_occurence,array):
        """ Filter array of results to keep only lines where the field id_column has got
        its nth appearing value"""
        filtered_array=[]
        values_encountered=[]
        occurence_encountered=0
        value_to_keep=None
        found=False

        for s_line in array:
            if (occurence_encountered==nth_occurence and found==False):
                found=True
                value_to_keep=s_line[id_column]
            elif ((not s_line[id_column] in values_encountered) and found==False):
                occurence_encountered+=1
                values_encountered.append(s_line[id_column])

            if(found==True and s_line[id_column]==value_to_keep):
                filtered_array.append(s_line)

        if found==False:
            raise UserWarning('Field number '+str(id_column)+' does not have '+str(nth_occurence)+ ' distinct values.')
        self.filtered_field_value=value_to_keep

        return filtered_array

    def format_input(self,field_columns,env_column,\
                     nnodes_column=0,variant_name_column=1,keep_nthocc_from_field=()):
        """ Format Jube results """

        self.clear_input_formating() # Erase old data if present


        # Potentialy apply filters to Jube data
        if(keep_nthocc_from_field):
            values_to_plot_array=self.keep_nth_occurence_from_field(keep_nthocc_from_field[0],keep_nthocc_from_field[1],self.result_array[1:])
        else:
            values_to_plot_array=self.result_array[1:]

        self.nb_fields=len(field_columns)

        # Parse result array
        for s_line in values_to_plot_array:
            try:
                for field_column in field_columns:
                    float(s_line[field_column].rstrip())
            except ValueError:
                print s_line[variant_name_column]+" variant run with "+s_line[nnodes_column]+" nodes did not finish"
                continue

            # Keep initial variants listing order (no set can be used here)
            if s_line[variant_name_column] not in self.list_variants:
                self.list_variants.append(s_line[variant_name_column])

            # Keep initial node listing order (no set can be used here)
            if s_line[nnodes_column] not in self.list_nodes:
                self.list_nodes.append(s_line[nnodes_column])

            # Gather values which need to be plotted
            line_fields=[]
            for field_column in field_columns:
                line_fields.append(float(s_line[field_column].rstrip()));
                if (self.nb_fields!=1):
                    self.field_legends.append(s_line[variant_name_column]+'-'+\
                                            self.result_array[0][field_column])
                else:
                    self.field_legends.append(s_line[variant_name_column])

                self.env_legends.append(re.sub(r'\s+','\n',s_line[env_column]))


            self.fields[s_line[nnodes_column],s_line[variant_name_column]]=line_fields

            self.nb_variants=len(self.list_variants)
            self.nb_nodes=len(self.list_nodes)

    def build_bars(self,ax):
        """ Build barchart """
        self.width = min(0.2*self.nb_nodes,1.0/(self.nb_variants+2))
        id_variant=0;self.rects_list=[];self.labels_list=[]

        for variant in self.list_variants:
            data_time_elapsed=[]
            # Add time elapsed (special treatment for unfinished runs)
            for node in self.list_nodes:
                try:
                    data_time_elapsed.append(self.fields[node,variant][0])
                except KeyError:
                    data_time_elapsed.append(0)

            self.labels_list.append(data_time_elapsed)
            ind=np.arange(self.nb_nodes)+((id_variant+0.5)*self.width)

           # ind=np.arange(self.nb_nodes)+((id_variant+0.5)*self.width)#+0.1
            colors=cm.jet(1.*id_variant/self.nb_variants)
            self.rects_list.append(ax.bar(ind,tuple(data_time_elapsed),width=self.width,color=colors))
            self.plot_handles.append(self.rects_list[-1])
            id_variant+=1

        # Each node area is 1 unit length.
        ax.set_xlim(0.0,1.0*self.nb_nodes+self.width)

        # Build grid to help readers
        ax.grid()

    def build_lines(self,ax):
        """ Build a line for each variant"""
        id_line=0
        id_variant=0
        for variant in self.list_variants:
            x=[]
            y=[]
            for id_field in range(0,self.nb_fields):
                x.append([])
                y.append([])

            for nodes in self.list_nodes:
                for id_field,field in zip(list(range(0,self.nb_fields)),self.fields[nodes,variant]):
                    try:
                        y[id_field].append(field)
                    except KeyError: # In case a run did not finish
                        pass
                    else:
                        x[id_field].append(float(nodes))


            marker = itertools.cycle(( 'o','^','8','H','*',','))
            for id_field in range(0,self.nb_fields):
                #variant_color=cm.jet(1.*id_line/(self.nb_variants*self.nb_fields))
                variant_color=cm.jet(1.*id_variant/(self.nb_variants))
                p,=ax.plot(x[id_field],y[id_field],linestyle='-',marker=marker.next(),\
                           linewidth=2,markersize=8,color=variant_color,clip_on=False)
                self.plot_handles.append(p)
                id_line+=1
            id_variant+=1

        # Build grid to help readers
        ax.grid()


    def build_legend(self,ax,xlabel,ylabel,title):
        """ Build Legend associated to the graph"""
        legends=[]

# First legend: variant names
        first_legend=ax.legend(tuple([item for item in self.plot_handles]),tuple(self.field_legends),shadow=True, fancybox=True,bbox_to_anchor=(1.005, 1), loc=2, borderaxespad=0.02,prop={'size':12})
        ax.add_artist(first_legend)

#Second legend: envrionment (modules)
        ax.legend(tuple([item for item in self.plot_handles]),tuple(self.env_legends),shadow=True, fancybox=True,bbox_to_anchor=(1.005, 0.5), loc=2, borderaxespad=0.02,prop={'size':9})

        ax.set_xlabel(xlabel,fontsize=12)
        ax.set_ylabel(ylabel,fontsize=12)
        ax.set_title(title)

        if (self.rects_list):
            self.build_barchart_legend(ax)

    def build_barchart_legend(self,ax):
        """ Build complementary legend associated with a bar graph (is called by build_legend). """
        ind=np.arange(self.nb_nodes)
        ax.set_xticks(ind+((self.nb_variants+2)/2)*self.width)
        ax.set_xticklabels(tuple(self.list_nodes))

        max_height=0
        for rects,labels in zip(self.rects_list,self.labels_list):
            for rect, label in zip(rects,labels):
                height = rect.get_height()
                max_height=max(max_height,height)
                ax.text(rect.get_x() + rect.get_width()/2, height*1.02, label , ha='center', va='bottom',fontsize=12)
#                min(,max(11,(80/(self.nb_nodes*self.nb_variants))
        ax.set_ylim([0,(max_height*1.10)])
