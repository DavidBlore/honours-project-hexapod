# Automated Damage Control in a Hexapod Robot - CPG Controller

This repository contains all of the code necessary to replicate the simulated experiments from the paper we submitted to the Gecco 2023 conference. This repo is for the CPG controller in the paper.

To view the code for NEAT, [click here](https://github.com/DavidBlore/honours-project-NEAT).

# Python package dependencies

```shell
pip install -r requirements.txt
```

- numpy
- pybullet
- matplotlib
- sklearn
- mpi4py
- GPy
- scipy

# Videos

[Click here](https://youtu.be/zb89rz9omFI) to see the different controllers adapting to the various failure scenarios.

# How to run code

Please note that you must be in the highest level in the directory tree before running any code. Do not change into sub-directories or else you'll have to adjust import statements

## Generating maps using MAP-Elites

To generate a map for MAP-Elites, run the following command:

```bash
python3 generate_map  -ne <num_evals> -m <map_size> -nrun <name_of_run> -b <batch_size> -r <restore_checkpoint> -c <controller>
```

The command takes in the following command line arguments:
| Flag | Flag (long) | Description |
|-------|-----------------------|---------------------------------------------------|
| -ne | --num_evals | the number of generations to run for |
| -m | --map_size | the size of the map |
| -nrun | --name_of_run | the name of the run |
| -b | --batch_size | how often to save checkpoints + archive (optional)|
| -r | --restore_checkpoint | the name of the checkpoint to restore (optional) |
| -c | --controller | which controller to use ("CPG"/"REF") |

EXAMPLE: To generate a map with 20k niches for the CPG controller, for 8 million evaluations:

```bash
python3 generate_map  -ne 8_000_000 -m 20 -nrun 20k8m-CPG-1 -b 2390 -c CPG
```

## Running the adaptation experiments

There are 3 types of adaptation experiments:

1. Adaptation for the best NEAT-produced non-adapting CPG controller (doesn't use IT&E)
2. Adaptation for the non-adapting reference controller's tripod gait (doesn't use IT&E)
3. Adaptation for the reference/CPG controller (does us IT&E)

To run the adaptation experiments for the best NEAT-produced CPG controller _without_ using IT&E to adapt (1.):

```bash
python3 experiments/adaptation_tests/run_adapt_tests_cpg_base_best.py
```

To run the adaptation experiments for the reference controller's tripod gait _without_ using IT&E to adapt (2.):

```bash
python3 experiments/adaptation_tests/run_tripod_tests.py
```

To run the adaptation experiments for the **reference** controller using IT&E to adapt (3.1):

```bash
python3 experiments/adaptation_tests/run_adapt_tests.py
```

To run the adaptation experiments for the **CPG** controller using IT&E to adapt (3.2):

```bash
python3 experiments/adaptation_tests/run_adapt_tests_cpg.py
```

## Generating plots and running statistical tests

All plots can be generated using the files in the plots folder.
To plot a map: `plots/maps/plot_2d_map.py`
To plot a performance graph: `plots/performance_adaption/MOBA-graphs.py`

# Directory structure

Below is a description of the **important** folders.
Note: not all files and folders are listed

```
honours-project
├── adapt                        <--- MBOA algorithm
├── centroids                    <--- centroids used in paper
├── cluster_scripts              <--- scripts for running MAP-Elites on clusters
│   ├── CHPC
│   └── UCT HPC
├── experiments
│   ├── adaptation_tests         <--- experiment files
│   └── output                   <--- experiment output
├── figures                      <--- output of plotting tools
│   ├── maps
│   └── performance_adaption
├── hexapod                      <--- simulation + controller files
├── maps                         <--- all maps used in paper
│   ├── CPG
│   │   ├── 1k
│   │   ├── 20k
│   │   └── 40k
│   └── REF
│       ├── 20k
│       └── 40k
├── plots                         <--- plotting tools
│   ├── maps
│   └── performance_adaption
├── pymap_elites                  <--- pymap_elites framework
└── tests                         <--- for viewing gaits
```
