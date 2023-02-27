#!/bin/bash
source /users/students/r0754386/Documents/bmtk/bin/activate
module load mpi
cd /users/students/r0754386/Documents/bmtk/examples/v1
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_0_0.json --overwrite True
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_400_400.json
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_-400_-400.json

