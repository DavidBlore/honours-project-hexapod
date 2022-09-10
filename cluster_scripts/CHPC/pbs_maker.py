"""
Creates PBS file for CHPC Cluster
"""
import argparse
import os
from datetime import datetime

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run MAP-Elites on CPG controller.')
    parser.add_argument('-ni','--num_instances',            required=True, type=int, default=5, help='the number of cores to use')
    parser.add_argument('-ne','--num_evals' ,            required=True, type=int, default=10_000_000, help='the number of generations to run for')
    parser.add_argument('-m','--map_size' ,            required=True, type=int, default=10_000, help='the size of the map')
    parser.add_argument('-nrun','--name_of_run',        required=True, type=str, default="", help='the name of the run')
    parser.add_argument('-b','--batch_size',   required=False, type=int, default=2390, help='how often to save checkpoints + archive')
    parser.add_argument('-r','--restore_checkpoint',    required=False, type=str, default="", help='the name of the checkpoint to restore')
    args = parser.parse_args() 

    pbs_file ="""
#!/bin/bash

#PBS -l select={num_instances}:ncpus=24:mpiprocs=24:nodetype=haswell_reg
#PBS -P CSCI1142
#PBS -q normal
#PBS -l walltime=12:00:00
#PBS -o /mnt/lustre/users/dblore/job-{name_of_run}.out
#PBS -e /mnt/lustre/users/dblore/job-{name_of_run}.err
#PBS -m abe
#PBS -M blrdav002@myuct.ac.za
#PBS -N {name_of_run}

ulimit -s unlimited

module purge
module load chpc/python/3.7.0

cd $PBS_O_WORKDIR
nproc=`cat $PBS_NODEFILE | wc -l`
mpirun -np $nproc python3 -m mpi4py.futures generate_map.py -ne {num_evals} -m {map_size} -nrun {name_of_run} -b {batch_size} -r "{restore_checkpoint}"
    """.format(
        num_instances           =args.num_instances,
        num_evals               =args.num_evals,
        map_size                =args.map_size,
        name_of_run             =args.name_of_run,
        batch_size              =args.batch_size,
        restore_checkpoint      =args.restore_checkpoint
    )

    local_dir = os.path.dirname(__file__)
    path = os.path.join(local_dir, os.pardir, "{name_of_run}.pbs".format(name_of_run=args.name_of_run+datetime.strftime(datetime.now(), '-%d%b%H%M')))
    open(path, "w").write(pbs_file)
    print("Created pbs file: {name_of_run}.pbs".format(name_of_run=args.name_of_run+datetime.strftime(datetime.now(), '-%d%b%H%M')))
    # os.system("qsub {path}".format(path=path))
