#!/bin/bash
source /users/students/r0754386/Documents/bmtk/bin/activate
module load mpi
cd /users/students/r0754386/Documents/bmtk/examples/v1
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_0a.json
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_0b.json
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_0c.json
mpirun -np 12 nrniv -mpi -python run_bionet.py config_comsol_0d.json

