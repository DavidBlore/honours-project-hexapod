"""Runs adaptation tests for the non-adapting reference controller's tripod gait and saves results.

Results saved to experiments/output/REF/tripod-no-adapatation/
"""
import sys
import os
sys.path.append(os.path.abspath("."))

from hexapod.controllers.reference_controller import Controller, reshape, tripod_gait
from hexapod.simulator import Simulator
import numpy as np
import time

S0 = [[]]
S1 = [[1],[2],[3],[4],[5],[6]]
S2 = [[1,4],[2,5],[3,6]]
S3 = [[1,3],[2,4],[3,5],[4,6],[5,1],[6,2]]
S4 = [[1,2],[2,3],[3,4],[4,5],[5,6],[6,1]]

SHOW_VISUAL = True
FAILED_LEGS = [1,2]
DELAY = 0.003 # slows down simulation


# runs through all of the failure scenarios and tests the performance of the tripod gait

def simulate_gait(leg_params, body_velocity, body_height, failed_legs, duration=5.0):
	try:
		controller = Controller(leg_params, body_height=body_height, velocity=body_velocity, crab_angle=-np.pi/6)
	except:
		return 0
	simulator = Simulator(controller, visualiser=SHOW_VISUAL, collision_fatal=False, failed_legs=failed_legs)
	# simulator.set_foot_friction(1.0)
	fitness = 0
	for t in np.arange(0, duration, step=simulator.dt):
		simulator.step()
		time.sleep(DELAY)
	fitness = simulator.base_pos()[0]
	simulator.terminate()
	return fitness


# runs through all of the failure scenarios and tests the performance of the tripod gait

print(simulate_gait(tripod_gait, 0.3, 0.14, failed_legs=FAILED_LEGS, duration=5.0))