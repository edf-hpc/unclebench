% ubench(1)

# NAME

ubench -  benchmarking tool

# SYNOPSIS

    ubench <command> [options]
        ubench <command> --help
	    ubench [--version]
	        ubench [--help]

# DESCRIPTION

UncleBench is a high level benchmarking tool using Jube benchmarking environment by default.

# UBENCH COMMANDS

Ubench provides the following commands:

    ubench-fetch
	Fetch benchmarks sources and test cases from a distant server to UBENCH_RESOURCE_DIR.
    
    ubench-run
	Execute benchmarks located in UBENCH_BENCHMARK_DIR in UBENCH_RUN_DIR_BENCH.

    ubench-result
	Print raw results array from a benchmark run.

    ubench-list
	List existing runs information for a given benchmark.

    ubench-log
	Print log of a benchmark run given its ID.

    ubench-report
	Build a performance report in UBENCH_REPORT_DIR from the last executed set of benchmark.

    ubench-listparams
        List customizable parameters of a benchmark.

# SEE ALSO

ubench-fetch(1), ubench-run(1), ubench-result(1), ubench-list(1), ubench-log(1), ubench-report(1), ubench-listparams(1)
