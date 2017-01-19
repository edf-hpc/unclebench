% ubench-fetch(1)

# NAME

ubench-fetch -  Fetch remote sources and test cases

# SYNOPSIS

    ubench fetch -b <bench> [<bench> ...] 
    ubench fetch -h

# DESCRIPTION

*ubench fetch* fetch remote sources and test cases from http servers, local paths or git repository.


# ENVIRONMENT

## UBENCH_CONF_DIR
  **default :** /etc/unclebench/conf  
  Path to a directory containing a conf.ini files listing servers, paths, or repositories where to
  find benchmark resources. It also contains benchmark subdirectories with .ini files giving
  the path of each file needed to run the benchmark.
  

## UBENCH_RESOURCE_DIR

  **default :** /scratch/<user>/Ubench/resource
  Local path where the resource files are fetched.
  

# SEE ALSO

ubench-run(1), ubench-result(1), ubench-list(1), ubench-log(1), ubench-report(1), ubench-listparams(1)