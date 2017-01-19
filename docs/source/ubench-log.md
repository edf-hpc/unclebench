% ubench-log(1)

# NAME


ubench-log -  Print log of a benchmark run

# SYNOPSIS


    ubench log -p <platform> -b <bench> [<bench> ...] -i <run_id>

    ubench log -h

# DESCRIPTION


*ubench log*  Print log of a benchmark run given its name, the platform on which it has been run and its id.
              Avaible benchmarks runs and their IDs can be found using *ubench list* command.

# OPTIONS

# -p <platform>
  Name of the platform where benchmarks were run 


# -b <bench> [<bench> ...]
  Names of the benchmarks whose logs should be printed

# -i <bench_id>
  Id of the benchmarks whose logs should be printed


# ENVIRONMENT


## UBENCH_RUN_DIR_BENCH
   **default :** /scratch/<user>/Ubench/benchmarks
   Path where benchmarks are looked for.


# SEE ALSO

ubench-fetch(1), ubench-result(1), ubench-run(1), ubench-log(1), ubench-report(1), ubench-listparams(1)