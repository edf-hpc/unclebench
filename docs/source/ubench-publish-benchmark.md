% ubench-publish-benchmark(1)

# NAME

ubench-publish-benchmark - Publishes benchmark to local repository

# SYNOPSIS

    ubench publish benchmark -p <platform> -b <bench>
    -d <directory> [-i <integer>] -m <commit_msg>

    ubench publish benchmark -h

# DESCRIPTION

*ubench publish benchmark* copies benchmark to local repository

# OPTIONS

# -p <platform>
  Name of the test platform.

# -b <benchmark>
  Name of the benchmark to publish. This parameter\
  is used to search the benchmark and also to publish\
  it under a directory with its name.

# -d <directory>
  Directory where to store the benchmark results file.\
  This directory will be created under the `results`\
  directory located in the local benchmark repository.

# -m <commit-message>
  Message describing the benchmark or rather the\
  intent of the benchmark being commited.

# -i <bench-run-id>
  Benchmark run id. If not given, the last benchmark\
  will be published, ie, the one with greater run id.

# SEE ALSO

ubench-publish(1)
