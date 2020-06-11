% ubench-publish-download(1)

# NAME

ubench-publish-download - Downloads repository to local machine

# SYNOPSIS

    ubench publish download [-h]

# DESCRIPTION

*ubench publish download* will download the repository to local machine.
The location of the repository in the local machine is defined by the variable
UBENCH_RESULTS_DIR. This variable should contain the whole path, including the
name of the repository to download as it is known by the VCS. As an example,
suppose the name of the repository is benchmarks. Then UBENCH_RESULTS_DIR must
contain some string like /path/to/repository/benchmarks.

## UBENCH_PUBLISH_VCS

  UncleBench will download the remote repository using the VCS defined in this
  variable.

## UBENCH_PUBLISH_REPOSITORY

  UncleBench will use the string defined in this variable to doanload the remote
  repository.

# SEE ALSO

ubench(1), ubench-publish(1)
