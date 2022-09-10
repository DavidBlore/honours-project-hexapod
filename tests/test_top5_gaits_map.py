"""View top 5 gaits in a map

Takes in the following command line arguments:
    Flag    Flag (long)             Description
    _____   _____________________   ____________________________________________
    -c      --controller            : Which controller to use ("CPG"/"REF")
    -n      --niches                : Number of niches (20 or 40)k
    -m      --map                   : Which map number to plot
"""
import sys
import os

sys.path.append(os.path.abspath("."))

from hexapod.controllers.cpg_controller import CPGParameterHandlerMAPElites
import controller_tools
import argparse
import adapt.MBOA as map_handler
import numpy as np

# S0 = [[]]
# S1 = [[1],[2],[3],[4],[5],[6]]
# S2 = [[1,4],[2,5],[3,6]]
# S3 = [[1,3],[2,4],[3,5],[4,6],[5,1],[6,2]]
# S4 = [[1,2],[2,3],[3,4],[4,5],[5,6],[6,1]]

FAILED_LEGS = []

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Plots a MAP-Elites map and saves it to figures folder.')
	parser.add_argument('-c','--controller', required=True, type=str,  default="CPG", help='Which controller to use ("CPG"/"REF")')
	parser.add_argument('-n','--niches',     required=True, type=int,  default=20, help='Number of niches (20 or 40)k')
	parser.add_argument('-m','--map',     required=True, type=int,  default=1, help='Which map number to plot')
    
	args = parser.parse_args() 
	
	if "CPG" not in args.controller and "REF" not in args.controller:
		raise Exception("Invalid controller - use \"CPG\" or \"REF\"")
	if args.niches != 20 and args.niches != 40:
		raise Exception(f"Only niches sizes of 20 and 40 are allowed (20k and 40k).\nYou put {args.niches}")

	if args.controller == "CPG":
		# get path to data
		centroid_path = os.path.join(os.path.dirname(__file__), "..",  "centroids", f"centroids_{args.niches}000_6.dat")
		map_path = os.path.join(os.path.dirname(__file__), "..", "maps", "CPG", f"{args.niches}k", f"map_{args.map}.dat")
		# load in data
		centroids = map_handler.load_centroids(centroid_path)
		fits, descs, ctrls = map_handler.load_map(map_path, centroids.shape[1])
		# show top 5 controllers in the map
		for top in range(5):
			index_best_controller = np.argmax(fits)
			x = CPGParameterHandlerMAPElites.convert_non_mapelites_parameters(ctrls[index_best_controller])
			print(controller_tools.evaluate_gait_cpg(x, visualiser=True, collision_fatal=False, delay=0.003, failed_legs=FAILED_LEGS)[0])
			np.delete(fits, index_best_controller)
			np.delete(ctrls, index_best_controller)
	else:
		# get path to data
		centroid_path = os.path.join(os.path.dirname(__file__), "..",  "centroids", f"centroids_{args.niches}000_6_reference.dat")
		map_path = os.path.join(os.path.dirname(__file__), "..", "maps", "REF", f"{args.niches}k", f"map_{args.map}.dat")
		# load in data
		centroids = map_handler.load_centroids(centroid_path)
		fits, descs, ctrls = map_handler.load_map(map_path, centroids.shape[1])
		for top in range(5):
			index_best_controller = np.argmax(fits)
			print(controller_tools.evaluate_gait_ref(ctrls[index_best_controller], visualiser=True, collision_fatal=False, delay=0.003, failed_legs=FAILED_LEGS)[0])
			np.delete(fits, index_best_controller)
			np.delete(ctrls, index_best_controller)