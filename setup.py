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

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
        
setup(name='ubench',
      version='0.3',
      description="Unclebench is a tool for automating the running of complex benchmarks on HPC clusters."\
                   "It is currently based on (JUBE http://www.fz-juelich.de/ias/jsc/EN/Expertise/Support/Software/JUBE/_node.html) but any benchmarking engine can be easily integrated."\
                   "Its architecture make it easier to handle platforms settings, benchmark descriptions, sources and test cases as separate resources."\
                   "It provides useful commands to modify parameters on the fly without having to modify the benchmark or platform description files',",
       install_requires=['clustershell>=1.6'],
      url='https://github.com/edf-hpc/unclebench',
      author='CCN HPC',
      author_email='dsp-cspito-ccn-hpc@edf.fr',
      scripts = ['bin/ubench'],
      license='GPLv3',
      packages=['ubench','ubench.core',
                'ubench.benchmark_managers',
                'ubench.benchmarking_tools_interfaces',
                'ubench.plugins',
                'ubench.scheduler_interfaces'],
      zip_safe=False)
