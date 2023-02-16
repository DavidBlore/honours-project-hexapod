"""Generates maps for the CPG or Reference controller using the MAP-Elites algorithm

Takes in the following command line arguments:
    Flag    Flag (long)             Description
    _____   _____________________   ____________________________________________
    -ne     --num_evals             : the number of generations to run for
    -m      --map_size              : the size of the map
    -nrun   --name_of_run           : the name of the run
    -b      --batch_size            : how often to save checkpoints + archive
    -r      --restore_checkpoint    : the name of the checkpoint to restore
    -c      --controller            : which controller to use ("CPG"/"REF")
"""
from hexapod.controllers.reference_controller import Controller, reshape
from hexapod.controllers.cpg_controller import CPGController
from hexapod.controllers.cpg_controller import CPGParameterHandlerMAPElites
from hexapod.simulator import Simulator
import pymap_elites.cvt as cvt_map_elites
import numpy as np
import argparse
import controller_tools

COLLISION_FATAL = True
RANDOM_INIT_BATCH = 2390

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run MAP-Elites algorithm.')
    parser.add_argument('-ne','--num_evals' ,        required=True,  type=int,   default=10_000_000, help='the number of generations to run for')
    parser.add_argument('-m','--map_size' ,          required=True,  type=int,   default=10_000, help='the size of the map')
    parser.add_argument('-nrun','--name_of_run',     required=True,  type=str,   default="", help='the name of the run')
    parser.add_argument('-b','--batch_size',         required=False, type=int,   default=2390, help='how often to save checkpoints + archive')
    parser.add_argument('-r','--restore_checkpoint', required=False, type=str,   default="", help='the name of the checkpoint to restore')
    parser.add_argument('-c','--controller',         required=False, type=str,  default="CPG", help='which controller to use ("CPG"/"REF")')
    args = parser.parse_args() 

    if "CPG" not in args.controller and "REF" not in args.controller:
        raise Exception("Invalid controller - use \"CPG\" or \"REF\"")
    if args.controller=="REF" and args.batch_size < RANDOM_INIT_BATCH:
        raise Exception(f"Batch size needs to be greater than the random init batch size (increase batch size to {RANDOM_INIT_BATCH})")

    params = \
        {
            # more of this -> higher-quality CVT
            "cvt_samples": 1_000_000, # 1_000_000
            # "cvt_samples": 1000000,
            # we evaluate in batches to parallelise
            "batch_size": args.batch_size, # 2390
            # proportion of niches to be filled before starting (400)
            "random_init": 0.01, # 0.01
            # batch for random initialization
            "random_init_batch": RANDOM_INIT_BATCH, # 2390
            # when to write results (one generation = one batch)
            "dump_period": 1e6, # 5e6
            # do we use several cores?
            "parallel": True,
            # do we cache the result of CVT and reuse?
            "cvt_use_cache": True,
            # min/max of parameters
            "min": 0,
            "max": 1,
        }

    
    # read in the seeded individuals from files
    individuals = None
    #if args.controller=="CPG":
    #    individuals = controller_tools.read_in_individuals(['all-best-genomes.txt'])

    if args.restore_checkpoint == "": # standard run
        archive = cvt_map_elites.compute(
            6,
            156 if args.controller=="CPG" else 32,
            controller_tools.evaluate_gait_cpg if args.controller=="CPG" else controller_tools.evaluate_gait_ref,
            checkpoint_filenameprefix="mapelites-checkpoint-{0}-".format(args.name_of_run),
            seeded_individuals=individuals,
            n_niches=args.map_size,
            max_evals=args.num_evals,
            log_file=open('log-{0}.dat'.format(args.name_of_run),'w'),
            params=params
        )
    else: # restore from a checkpoint run
        archive = cvt_map_elites.compute_from_checkpoint(
            "{0}".format(args.restore_checkpoint),
            controller_tools.evaluate_gait_cpg if args.controller=="CPG" else controller_tools.evaluate_gait_ref,
            continue_checkpointing=True,
            params=params,
            max_evals=args.num_evals
        )
