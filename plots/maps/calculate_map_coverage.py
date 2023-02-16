import os

print("Controller;Map;Coverage")
for controller in ["REF", "CPG"]:
    for niche in [5,10,20,40,80]:
        for map in range(1,11):
            map_file = open(os.path.join(os.path.dirname(__file__), "..", "..",  "maps", f"{controller}", f"{niche}k", f"map_{map}.dat"))
            # count number of lines
            num_lines = len(map_file.readlines())
            coverage = num_lines / (niche * 1000)
            coverage *= 100
            # print(f"{controller} \t{niche}k map_{map} \t{coverage:.2f}% coverage")
            print(f"{controller};{niche}k map_{map};{coverage:.2f}% coverage")

