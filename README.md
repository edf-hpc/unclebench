# UncleBench

UncleBench is a tool for automating the running of complex benchmarks on HPC infrastructures.
It relies on [Jube](http://www.fz-juelich.de/ias/jsc/EN/Expertise/Support/Software/JUBE/_node.html)
as a benchmark engine but it can be customized to work with any benchmark engine.

In order to run a specific benchmark in a given platform you need to provide descriptions for both (benchmark and platform) in form of Jube files.
Unclebench provides Jube recipes for several well known benchmarks in HPC, these recipies describe the whole cycle: downlad of files, compilation and preparation of code,
execution, analysis and generation of reports.
List of provided bencmarks:

- HPCC: http://icl.cs.utk.edu/hpcc/
- HPCG: http://www.hpcg-benchmark.org/
- HPL: http://www.netlib.org/benchmark/hpl/
- IO500: https://www.vi4io.org/std/io500/start
- IOR: https://github.com/LLNL/ior
- NAS: https://www.nas.nasa.gov/publications/npb.html
- STREAM: https://www.cs.virginia.edu/stream/
- TENSORFLOW: https://www.tensorflow.org/performance/benchmarks

Unclebench provides HP Zbook15 laptop as a platform example, you can use it as a model to write a jube file which better fit your platform.
For a description of platform variables [see](https://github.com/edf-hpc/unclebench/blob/master/docs/source/platform_guide.asc)

# Getting started

Fetch a benchmark:

    $ubench fetch -b nas

Run a benchmark:

    $ubench run -b nas -p cluster  -w 2 4 8 16

Print benchmark result:

```bash
    $ubench result  -b nas -p cluster 
    Processing nas benchmark :
    ----analysing results
    benchmark_resulst_path: /scratch/cr3db69n/Ubench/benchmarks/porthos/nas/./benchmarks_runs/000002/
    ----extracting analysis

    processes  Mflops    mpi_version
    2          1358.23   OpenMPI-2.0.1
    4          2326.29   OpenMPI-2.0.1
    8          5173.65   OpenMPI-2.0.1
    16         9176.02   OpenMPI-2.0.1
```

Summary of UncleBench sub commands:

- fetch: download benchmark source codes, binaries and input files.
- run: run benchmark with parameter modification on the fly.
- list: list runs for given benchmark and platform.
- log/status: follow benchmark progress.
- result: print raw results.
- report: generate html annotated performance report.


For a complete documentation [see](https://github.com/edf-hpc/unclebench/blob/master/docs/source/user_guide.asc).

For a description of provided benchmarks and their parameters [see](https://github.com/edf-hpc/unclebench/blob/master/docs/source/benchmarks_guide.asc)

For a description of UncleBench architecture [see](https://github.com/edf-hpc/unclebench/blob/master/docs/source/developer_guide.asc)

# Setting up a development environment

We use virtualenv to setup a virtual environment for test:

    sudo apt-get install python-virtualenv
    mkdir unclebench_env/
    virtualenv unclebench_env/

To activate the virtual environment:

    cd unclebench_env
    source bin/activate

We install then 'pytest'

    pip install pytest

Finally, we load some UncleBench variables and execute the tests: 

    source dev_env.sh
    pytest

Licence
-------

UncleBench is distributed under the terms of the GPL v3 licence.
