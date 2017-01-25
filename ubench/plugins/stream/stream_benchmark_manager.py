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

import ubench.benchmark_managers.benchmark_manager as bm


class LocalBenchmarkManager(bm.BenchmarkManager):

    def __init__(self,benchmark_name,platform):
        """ Constructor """
        bm.BenchmarkManager.__init__(self,benchmark_name,platform)
        self.title='STREAM benchmark (v 5.10)'
        self.description='STREAM is a memory bandwidth benchmark (https://www.cs.virginia.edu/stream/).'
        self.print_array=False
        self.print_transposed_array=True
        self.print_plot=False
