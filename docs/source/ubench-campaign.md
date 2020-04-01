% ubench-campaign(1)

# NAME


ubench-campaign -  Run benchmarks campaigns

# SYNOPSIS

    ubench campaign -f <campaign_file>

    ubench campaign -h


# DESCRIPTION


*ubench campaign*  execute benchmarks campaigns described in the campaign file.
The execution will create a directory `campaign-$NAME-$DATE` under the directory defined in
`UBENCH_RUN_DIR_BENCH` variable.

# OPTIONS


# -f <campaign_file>
  Path to campaign file which describes benchmark campaign (benchmarks to be executed and parameters)


## UBENCH_PLATFORM_DIR
   **default :** /usr/share/unclebench/platform
   Path to platform files.


## UBENCH_BENCHMARK_DIR
   **default :** /usr/share/unclebench/benchmarks'
   Path where the benchmark configuration files are located.


## UBENCH_RUN_DIR_BENCH
   **default :** /scratch/<user>/Ubench/
   Path where benchmark campaign is executed.


## UBENCH_RESOURCE_DIR
   **default :** /scratch/<user>/Ubench/resource
   Path where ubench can find the benchmark resource files.

# SEE ALSO

ubench-fetch(1), ubench-result(1), ubench-list(1), ubench-log(1), ubench-report(1), ubench-listparams(1), ubench-run(1)
