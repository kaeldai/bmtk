#!/bin/bash
source /users/students/r0754386/Documents/bmtk/bin/activate
module load mpi
cd /users/students/r0754386/Documents/bmtk/examples/v1
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_0.json
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_200.json
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_-200.json

