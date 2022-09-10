# View gaits

## See Top 5 gaits in a map
To visualize the top 5 best gaits in a map:
```bash
python3 tests/test_top5_gaits_map.py -c <controller> -n <number of niches> -m <number of map> 
```

Eg:
```bash
python3 tests/test_top5_gaits_map.py -c CPG -n 20 -m 1
```

## See Top 3 gaits from NEAT's CPPNs
To visualize the top 3 best gaits produced by CPPNs using NEAT:
```bash
python3 tests/test_top3_neat_gaits.py
```