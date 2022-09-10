"""Runs adaptation experiments on the best NEAT-produce CPG controller
"""
import sys
import os
sys.path.append(os.path.abspath("."))

import controller_tools
from hexapod.controllers.cpg_controller import CPGParameterHandlerMAPElites

SHOW_VISUAL = False

S0 = [[]]
S1 = [[1],[2],[3],[4],[5],[6]]
S2 = [[1,4],[2,5],[3,6]]
S3 = [[1,3],[2,4],[3,5],[4,6],[5,1],[6,2]]
S4 = [[1,2],[2,3],[3,4],[4,5],[5,6],[6,1]]
scenarios = [S0, S1, S2, S3, S4]
inds = controller_tools.read_in_individuals(["all-best-genomes.txt"])

for scenario in range(5):
	failure_scenario = scenario
	failures = scenarios[failure_scenario]

	path = os.path.join(os.path.dirname(__file__), "..", "output", "CPG", "neat-no-adpatation", f"NEAT-CPG-{failure_scenario}.dat")
	fout = open(path, 'w')
	for failure_index, failed_legs in enumerate(failures):
		print("Failed legs:", failed_legs)
		x = inds[-1].copy()
		fitness = controller_tools.evaluate_gait_cpg(x,visualiser=SHOW_VISUAL,collision_fatal=False,failed_legs=failed_legs)[0]
		# print("{:3.5f}\n".format(fitness))
		fout.write("{:3.5f}\n".format(fitness))
		
	fout.flush()
	fout.close()


