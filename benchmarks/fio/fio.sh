#!/bin/bash

echoerr() { echo "$@" 1>&2; }

################################################################################
# Help                                                                         #
################################################################################
Help()
{
   # Display Help
   echo "fIO lancer Script"
   echo
   echo "usage: fio.sh <r|w|rw> [Size] [NumJobs]"
   echo "options:"
   echo "   h\t\tPrint this Help."
   echo
}

exec_fio()
{
    ./xfio -name $1 -rw $2 -runtime 10  -direct 1 -bs 1M --group_reporting -size $3 -directory $4 -numjobs $5
}


while getopts ":h" option; do
   case $option in
      h) # display Help
         Help
         exit;;
   esac
done



if [ "$#" -ge 1 ]; then 
    echo "==================================================== FIO Benchmark $(hostname) ===================================================="
    echo "Checking..."
    
    nodes=${SLURM_JOB_NODELIST-"$(hostname)"}
    echo "Nodes=$nodes"

    arg=$1
    size=${2:-1G}
    jobs=${3:-4}
    fileDir=${5:-"$SCRATCHDIR/fileDir"}
    host=${4:-"$(hostname)"}
    filename="testDDR-$host"
    filenameW="testDDW-$host"

    mkdir -vp $fileDir

    if [ "$arg" = "r" ]; then
        echo "Read fIO"
        exec_fio $filename "read" $size $fileDir $jobs
    fi
    if [ "$arg" = "rw" ]; then
        echo "Read/Write fIO"
        exec_fio $filename "read" $size $fileDir $jobs
        echo    
        echo "============================================================================================================================"
        echo
        exec_fio $filenameW "write" $size $fileDir $jobs
    fi
    if [ "$arg" = "w" ]; then
        echo "Write fIO"
        exec_fio $filenameW "write" $size $fileDir $jobs
    fi

    # [ -z "$5" ] && rm -vf $fileDir/$filename* > clean.out
    echo
    echo "...done."
    echo "=====================================================   End FIO Benchmark  ====================================================="
else 
    echoerr "No Arguments specified"
    echo
    Help
    exit
fi
