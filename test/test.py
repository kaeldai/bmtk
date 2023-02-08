""" COMSOL -> NEURON link
IN: 
    - COMSOL: 
        - file containing positions and extracellular potential distribution
        - mesh file
    - NEURON:
        - position of NEURON node (=compartment)

OUTPUT: (interpolated/nearest neighbour) extracellular potential at NEURON node
"""

import pandas as pd
import numpy as np
from scipy.interpolate import NearestNDInterpolator as NN

r05 = 500*np.random.rand(10000,3)

def get_vext(r05):
    COMSOL = pd.read_csv("COMSOL.txt", sep="\s+", header=8, usecols=[0,1,2,3], names=['x','y','z','V'])
    interp = NN(COMSOL[['x','y','z']], COMSOL['V'])
    v_extracellular = interp(r05)
    vext_vec = v_extracellular
    return vext_vec

v_ext = get_vext(r05)
print(v_ext)
print(np.hstack((r05[:25],v_ext[:25])))
print(r05[:25])


