% ubench-publish-campaign(1)

# NAME

ubench-publish-campaign - Publishes campaign to local repository

# SYNOPSIS

    ubench publish campaign -c <campaign-dir>
    -d <publish-dir> -m <commit-msg>

    ubench publish campaign -h

# DESCRIPTION

*ubench publish campaign* copies campaign to local repository

# OPTIONS

# -c <campaign-dir>
  Name of the directory of the campaign to publish. This
  directory should be entered as it appears under the
  benchmark run directory given by UBENCH_RUN_DIR_BENCH.
  
# -d <publish-dir>
  Directory where to store the campaign result files. This
  directory will be created under the `results` directory
  located in the local benchmark repository.

# -m <commit-msg>
  Commit message synthesizing the intent of the campaign.

# SEE ALSO

ubench(1), ubench-publish(1)
