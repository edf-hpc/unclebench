% ubench-publish(1)

# NAME

ubench-publish - Publish results to repository

# SYNOPSIS

    ubench publish <command> [options]
    ubench publish <command> --help
    ubench publish --help

# DESCRIPTION

*ubench publish* enables Unclebench to publish benchmark results to repository.

# AVAILABLE COMMANDS

The following commands are available:

    benchmark
        Publishes a benchmark into local repository.

    campaign
        Publishes a whole campaign into local repository.

    download
        Copies remote repository to local machine.

    update-remote
        Updates remote repository with local data.

## UBENCH_PUBLISH_REPOSITORY
   String used to download remote repository. Can be decomposed into protocol, \
   server, path and repository name.

   Example: protocol://server.com/path/to/repository

## UBENCH_PUBLISH_VCS
   Command used to operate VCS.

   Example: for Github use git, for Mercurial use hg, etc.

# SEE ALSO

ubench-publish-benchmark(1), ubench-publish-campaign(1), ubench-publish-download(1), \
ubench-publish-update-remote(1)
