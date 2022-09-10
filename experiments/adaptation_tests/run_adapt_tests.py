"""Runs adaptation tests for the reference controller and saves results.

Results saved to experiments/output/REF/<niches>k/
"""
import sys
import os
sys.path.append(os.path.abspath("."))

from hexapod.controllers.reference_controller import Controller, reshape
from adapt.MBOA import MBOA
import numpy as np
import controller_tools

# parameters
map_count = 10
niches = 40#k
SHOW_VISUAL = False

S0 = [[]]
S1 = [[1],[2],[3],[4],[5],[6]]
S2 = [[1,4],[2,5],[3,6]]
S3 = [[1,3],[2,4],[3,5],[4,6],[5,1],[6,2]]
S4 = [[1,2],[2,3],[3,4],[4,5],[5,6],[6,1]]
scenarios = [S0, S1, S2, S3, S4]

def mboa_gait_evaluation(x):
	"""Takes parammeters from MBOA and returns fitness value for that controller/gait
	"""
	return controller_tools.evaluate_gait_ref(x, visualiser=SHOW_VISUAL,collision_fatal=False,failed_legs=failed_legs)[0]

for scenario in range(5):
	failures = scenarios[scenario]

	num_its = np.zeros((len(failures), map_count))
	best_indexes = np.zeros((len(failures), map_count))
	best_perfs = np.zeros((len(failures), map_count))

	for failure_index, failed_legs in enumerate(failures):
		print("Failed legs:", failed_legs)
		for map_num in range(1, map_count+1):
			print("Testing map:", map_num)
            # get paths
			centroid_path = os.path.join(os.path.dirname(__file__), "..",  "..", "centroids", f"centroids_{niches}000_6_reference.dat")
			map_path = os.path.join(os.path.dirname(__file__), "..", "..", "maps", "REF", f"{niches}k", f"map_{map_num}.dat")
            # run adaptation algorithm
			num_it, best_index, best_perf, new_map = MBOA(map_path, centroid_path, mboa_gait_evaluation, max_iter=40, print_output=False)

			num_its[failure_index, map_num-1] = num_it
			best_indexes[failure_index, map_num-1] = best_index
			best_perfs[failure_index, map_num-1] = best_perf

	path = os.path.join(os.path.dirname(__file__), "..", "output", "REF", f"{niches}k", f"trials_{scenario}.dat")
	path2 = os.path.join(os.path.dirname(__file__), "..", "output", "REF", f"{niches}k", f"perfs_{scenario}.dat")
	np.savetxt(path, num_its, '%d')
	np.savetxt(path2, best_perfs, '%3.5f')
