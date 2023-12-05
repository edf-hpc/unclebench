% ubench-result(1)

# NAME


ubench-result -  Print result of a benchmark run

# SYNOPSIS


    ubench result -p <platform> -b <bench> -i <run_id> -o <output_file>

    ubench result -h

# DESCRIPTION


*ubench result*   Print results of a benchmark run given its name, the platform on which it has been run and its id.
		  Additionally, it will generate a file in YAML format which contains data related to the environment of executions and results.
		  These files are used as input for *ubench compare* comand. 
              Available benchmarks runs and their IDs can be found using *ubench list* command.

# OPTIONS

# -p <platform>
  Name of the platform where benchmarks were run 


# -b <bench> [<bench> ...]
  Names of the benchmarks whose results should be printed


# -i <bench_id>
  Id of the benchmarks whose results should be printed

# -o <output_file>
  Name of the file to output results in wiki syntax to, instead of the terminal

# ENVIRONMENT


## UBENCH_RUN_DIR_BENCH
   **default :** /scratch/<user>/Ubench/benchmarks
   Path where benchmarks are looked for.

# SEE ALSO

ubench-fetch(1), ubench-run(1), ubench-list(1), ubench-log(1), ubench-report(1), ubench-listparams(1)
