#!/bin/sh
#SBATCH --account commerce
#SBATCH --partition=swan
#SBATCH --time=:10:00
#SBATCH --nodes=2 --ntasks=8 --ntasks-per-node=4
#SBATCH --job-name="Test-20k8m"
#SBATCH --mail-user=blrdav002@myuct.ac.za
#SBATCH --mail-type=ALL
module load mpi/openmpi-4.0.1
module load python/anaconda-python-3.7

srun python3 -m mpi4py.futures generate_map.py