% ubench-fetch(1)

# NAME

ubench-fetch -  Fetch remote sources and test cases

# SYNOPSIS

    ubench fetch -b <bench> [<bench> ...] 
    ubench fetch -h

# DESCRIPTION

*ubench fetch* fetch remote sources and test cases from HTTP servers, local paths or revision control repositories (git,svn).


# ENVIRONMENT
  
## UBENCH_RESOURCE_DIR

  **default :** /scratch/<user>/Ubench/resource
  Local path where the resource files are fetched.
  

# SEE ALSO

ubench-run(1), ubench-result(1), ubench-list(1), ubench-log(1), ubench-report(1), ubench-listparams(1)
