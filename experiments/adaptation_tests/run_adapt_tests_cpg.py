"""Contains methods to run the adaptation experiments for the CPG Controller.

See research paper for more details on the experiments
"""
import sys
import os
sys.path.append(os.path.abspath("."))

from hexapod.controllers.cpg_controller import CPGParameterHandlerMAPElites
from adapt.MBOA import MBOA
import numpy as np
import controller_tools

# parameters
map_count = 10 # how many maps (i.e., unqiue runs/samples) did we have
niches = 20 #k

# failure scenarios
S0 = [[]]
S1 = [[1],[2],[3],[4],[5],[6]]
S2 = [[1,4],[2,5],[3,6]]
S3 = [[1,3],[2,4],[3,5],[4,6],[5,1],[6,2]]
S4 = [[1,2],[2,3],[3,4],[4,5],[5,6],[6,1]]

SHOW_VISUAL =  False

def mboa_convert_and_eval(x_non01):
    """Takes CPG parammeters from MBOA and returns fitness value for that controller/gait

    Converts parameters into correct range expected by the CPG first before evaluating the gait.

    Args:
        The parameters output by MBOA
    
    Returns:
        Fitness value for the given controller/gait
    """
    x = CPGParameterHandlerMAPElites.convert_non_mapelites_parameters(x_non01)
    return controller_tools.evaluate_gait_cpg(x,visualiser=SHOW_VISUAL,collision_fatal=False,failed_legs=failed_legs)[0]

for scenario in range(5):
    scenarios = [S0, S1, S2, S3, S4]
    failures = scenarios[scenario]

    num_its = np.zeros((len(failures), map_count))
    best_indexes = np.zeros((len(failures), map_count))
    best_perfs = np.zeros((len(failures), map_count))

    for failure_index, failed_legs in enumerate(failures):
        print("Failed legs:", failed_legs)
        for map_num in range(1, map_count+1):
            print("Testing map:", map_num)
            # get paths
            centroid_path = os.path.join(os.path.dirname(__file__), "..",  "..", "centroids", f"centroids_{niches}000_6.dat")
            map_path = os.path.join(os.path.dirname(__file__), "..", "..", "maps", "CPG", f"{niches}k", f"map_{map_num}.dat")
            # run adaptation algorithm
            num_it, best_index, best_perf, new_map = MBOA(map_path, centroid_path, mboa_convert_and_eval, max_iter=40, print_output=False)

            num_its[failure_index, map_num-1] = num_it
            best_indexes[failure_index, map_num-1] = best_index
            best_perfs[failure_index, map_num-1] = best_perf

    path = os.path.join(os.path.dirname(__file__), "..", "output", "CPG", f"{niches}k", f"trials_{scenario}.dat")
    path2 = os.path.join(os.path.dirname(__file__), "..", "output", "CPG", f"{niches}k", f"perfs_{scenario}.dat")
    fout = open(path, 'wb')
    fout2 = open(path2, 'wb')
    np.savetxt(fout, num_its, '%d')
    np.savetxt(fout2, best_perfs,"%3.5f")
    fout.flush()
    fout2.flush()
    fout.close()
    fout2.close()

