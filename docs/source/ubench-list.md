% ubench-list(1)

# NAME


ubench-list -  List benchmarks runs information

# SYNOPSIS


    ubench list -p <platform> -b <bench> [<bench> ...]

    ubench list -h

# DESCRIPTION


*ubench list*  lists runs information for a given platform and a given list of benchmarks.

# OPTIONS


# -p <platform>
  Name of the platform from which benchmark runs should be listed.


# -b <bench> [<bench> ...]
  Names of the benchmarks whose executions should be listed.
  

# ENVIRONMENT


## UBENCH_RUN_DIR_BENCH
   **default :** /scratch/<user>/Ubench/benchmarks
   Path where benchmarks are looked for.


# SEE ALSO

ubench-fetch(1), ubench-result(1), ubench-run(1), ubench-log(1), ubench-report(1), ubench-listparams(1)