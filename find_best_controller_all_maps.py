"""
Finds the fastest controller across all maps for each map size and each controller
"""
import sys
import os
sys.path.append(os.path.abspath("."))

import numpy as np

# get paths
# CPG
PATH_TO_CPG_MAPS_20k = os.path.join(os.path.dirname(__file__), "maps", "CPG", "20k")
PATH_TO_CPG_MAPS_40k = os.path.join(os.path.dirname(__file__), "maps", "CPG", "40k")
map_files_cpg_20k = os.listdir(PATH_TO_CPG_MAPS_20k)
map_files_cpg_40k = os.listdir(PATH_TO_CPG_MAPS_40k)
# REF
PATH_TO_REF_MAPS_20k = os.path.join(os.path.dirname(__file__), "maps", "REF", "20k")
PATH_TO_REF_MAPS_40k = os.path.join(os.path.dirname(__file__), "maps", "REF", "40k")

mapping = {
    "cpg":  [
        PATH_TO_CPG_MAPS_20k,
        PATH_TO_CPG_MAPS_40k,
    ],
    "ref":  [
        PATH_TO_REF_MAPS_20k,
        PATH_TO_REF_MAPS_40k,
    ]
}


def get_max(controller,mapsize):
    try:
        global_max = 0 
        global_percentage_niches_filled = 0
        num_maps_evaluated = 0

        base_path = mapping[controller][0] if mapsize==20 else mapping[controller][1]
        map_files = os.listdir(base_path)
        for map in map_files:
            max=0
            if (".dat" in map and ".icloud" not in map):
                num_maps_evaluated += 1
                path = os.path.join(base_path, map)
                f = open(path)
                lines = f.readlines()
                percentage_niches_filled = len(lines)/(mapsize*1000)
                global_percentage_niches_filled += percentage_niches_filled
                for line in lines:
                    fitness = float(line.split(" ")[0])
                    if fitness > max:
                        max = fitness
                print(f"percentage_niches_filled: {percentage_niches_filled:.5f}")
            if max > global_max:
                global_max=max
        print("Average % niches filled:",global_percentage_niches_filled/num_maps_evaluated)
        return global_max
    except:
        print("use proper controller+mapsize")

print("CPG-20K: {0:.3f} m/s".format(get_max("cpg",20)/5))
print("CPG-40K: {0:.3f} m/s".format(get_max("cpg",40)/5))
print("Ref-20K: {0:.3f} m/s".format(get_max("ref",20)/5))
print("Ref-20K: {0:.3f} m/s".format(get_max("ref",40)/5))