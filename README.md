# UncleBench

[![Build Status](https://travis-ci.org/camilo1729/unclebench.svg?branch=master)](https://travis-ci.org/camilo1729/unclebench)

UncleBench is a tool for automating the running of complex benchmarks on HPC infrastructures.
The whole cycle is automated: downlading of necessary files, compilation and preparation of code,
execution, analysis and generation of reports.
It uses [Jube](http://www.fz-juelich.de/ias/jsc/EN/Expertise/Support/Software/JUBE/_node.html)
as a benchmark engine but it can be customized to work with any benchmark engine.


# Setting up a development environment

In order to carry out test, you should do the following:

    sudo apt-get install python-virtualenv
    mkdir unclebench_env/
    virtualenv unclebench_env/
    cd unclebench_env
    source bin/activate
    pip install pytest
    source dev_env.sh
    pytest

## Features

- fetch: download benchmark source codes, binaries and input files.
- run: run benchmark with parameter modification on the fly.
- list: list runs for given benchmark and platform.
- log/status: follow benchmark progress.
- result: print raw results.
- report: generate html annotated performance report.

Licence
-------

UncleBench is distributed under the terms of the GPL v3 licence.
