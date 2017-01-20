# UncleBench

UncleBench is a tool for automating the running of complex benchmarks on HPC infrastructures.
The whole cycle is automated: downlading of necessary files, compilation and preparation of code,
execution, analysis and generation of reports.
It uses [Jube](http://www.fz-juelich.de/ias/jsc/EN/Expertise/Support/Software/JUBE/_node.html)
as a benchmark engine but it can be customized to work with any benchmark engine.

## Features

- fetch: download benchmark source codes, binaries and input files.
- run: run benchmark with parameter modification on the fly.
- list: list runs for given benchmark and platform.
- log/status: follow benchmark progress.
- result: print raw results.
- report: generate html annotated performance report.

Licence
-------

UncleBench is distributed under the terms of the CeCILL v2 licence.
