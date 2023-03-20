#!/bin/bash
source /users/students/r0754386/Documents/bmtk/bin/activate
module load mpi
cd /users/students/r0754386/Documents/bmtk/examples/v1
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z+_L.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z-_L.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_x+_L.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_x-_L.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z+x+_L.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z+x-_L.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z-x+_L.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z-x-_L.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z+.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z-.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_x+.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_x-.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z+x+.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z+x-.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z-x+.json
mpirun -np 12 nrniv -mpi -python run_bionet.py 9/config_comsol_z-x-.json


