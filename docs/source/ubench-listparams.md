% ubench-listparams(1)

# NAME


ubench-listparams -  List benchmark parameters that are customizable.

# SYNOPSIS

    ubench-listparams -b <bench>

    ubench-listparams -h

# DESCRIPTION


*ubench listparams*  lists benchmark parameters that can be modified through a
                     *ubench run -customp* command. 

# OPTIONS

# -b <bench> [<bench> ...]
  Names of the benchmarks whose executions should be listed.
  

# ENVIRONMENT

## UBENCH_BENCHMARK_DIR
   **default :** /usr/share/unclebench/benchmarks'
   Path where the benchmark configuration files are located.

# SEE ALSO

ubench-fetch(1), ubench-result(1), ubench-run(1), ubench-log(1), ubench-report(1), ubench-list(1)
