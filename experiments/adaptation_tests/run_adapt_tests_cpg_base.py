"""Runs adaptation experiments on every single NEAT controller

NOTE: This was done more for interest sake. It's not necessary and is computationally expensive.
"""
import sys
import os
sys.path.append(os.path.abspath("."))

from hexapod.controllers.cpg_controller import CPGController
from hexapod.controllers.cpg_controller import CPGParameterHandlerMAPElites
from hexapod.simulator import Simulator
import numpy as np
import controller_tools

SHOW_VISUAL=False

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
	fout = open(os.path.join(os.path.dirname(__file__), "..", "output", "CPG", "neat-no-adpatation", "all-gaits", f"NEAT-CPG-{failure_scenario}.dat"), 'w')
	for i in range(len(inds)):
		avg_fitness = 0
		count = 0
		
		for failure_index, failed_legs in enumerate(failures):
			print("Failed legs:", failed_legs)
			x = inds[i].copy()
			fitness = controller_tools.evaluate_gait_cpg(x,visualiser=SHOW_VISUAL,collision_fatal=False,failed_legs=failed_legs)[0]
			# print("Gait {0},{1}".format(i,fitness))
			avg_fitness += fitness
			count+=1

		avg_fitness = avg_fitness/count
		fout.write("Gait {0},{1}\n".format(i,avg_fitness))
	fout.flush()
	fout.close()


