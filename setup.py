from setuptools import setup

setup(name='ubench',
      version='0.3',
      description='Unclebench is a tool for automating the running of complex benchmarks on HPC clusters.
                   It is currently based on (JUBE http://www.fz-juelich.de/ias/jsc/EN/Expertise/Support/Software/JUBE/_node.html) but any benchmarking engine can be easily integrated.
                   Its architecture make it easier to handle platforms settings, benchmark descriptions, sources and test cases as separate resources.
                   It provides useful commands to modify parameters on the fly without having to modify the benchmark or platform description files',
      url='https://github.com/edf-hpc/unclebench',
      author='CCN HPC',
      author_email='dsp-cspito-ccn-hpc@edf.fr',
      scripts = ['bin/ubench'],
      license='CeCILL-C (French equivalent to LGPLv2+)'
      packages=['ubench'],
      zip_safe=False)
