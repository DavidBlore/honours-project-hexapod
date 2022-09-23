"""Runs MBOA adptation for the CPG Controller with GUI visual.

Used for seeing the gaits. Use experiments/adaptation_tests/run_adapt_tests_cpg.py for actual experiments
"""
import sys
import os
sys.path.append(os.path.abspath("."))

from hexapod.controllers.cpg_controller import CPGParameterHandlerMAPElites
from adapt.MBOA import MBOA
import controller_tools

# parameters
map_num = 8 # which map to use
niches = 40 #k

# failure scenarios for reference
# S0 = [[]]
# S1 = [[1],[2],[3],[4],[5],[6]]
# S2 = [[1,4],[2,5],[3,6]]
# S3 = [[1,3],[2,4],[3,5],[4,6],[5,1],[6,2]]
# S4 = [[1,2],[2,3],[3,4],[4,5],[5,6],[6,1]]

SHOW_VISUAL =  True
FAILED_LEGS = [1,2]

def mboa_convert_and_eval(x_non01):
    """Takes CPG parammeters from MBOA and returns fitness value for that controller/gait

    Converts parameters into correct range expected by the CPG first before evaluating the gait.

    Args:
        The parameters output by MBOA
    
    Returns:
        Fitness value for the given controller/gait
    """
    x = CPGParameterHandlerMAPElites.convert_non_mapelites_parameters(x_non01)
    return controller_tools.evaluate_gait_cpg(x,visualiser=SHOW_VISUAL,collision_fatal=False,failed_legs=FAILED_LEGS, delay=0.003)[0]


if __name__ == "__main__":
    # get paths
    centroid_path = os.path.join(os.path.dirname(__file__),  "..", "centroids", f"centroids_{niches}000_6.dat")
    map_path = os.path.join(os.path.dirname(__file__), "..", "maps", "CPG", f"{niches}k", f"map_{map_num}.dat")
    # run adaptation algorithm
    num_it, best_index, best_perf, new_map = MBOA(map_path, centroid_path, mboa_convert_and_eval, max_iter=40, print_output=False)
    print(f"Took {num_it} iterations, settled with gait that walked at {best_perf/5} m/s")
