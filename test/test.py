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
from scipy.interpolate import NearestNDInterpolator as NNip
from neuron import h

r05 = 500*np.random.rand(10000,3)

def get_vext(r05):
    COMSOL = pd.read_csv("COMSOL.txt", sep="\s+", header=8, usecols=[0,1,2,3], names=['x','y','z','V'])
    interp = NNip(COMSOL[['x','y','z']], COMSOL['V'])
    v_extracellular = interp(r05)
    vext_vec = v_extracellular
    return vext_vec

v_ext = get_vext(r05)
# print(v_ext)
# print(np.hstack((r05[:25],v_ext[:25])))
# print(r05[:25])

COMSOL = pd.read_csv("COMSOL.txt", sep="\s+", header=8, usecols=[0,1,2,3], names=['x','y','z','V'])

def get_NN(r05):
    COMSOL = pd.read_csv("COMSOL.txt", sep="\s+", header=8, usecols=[0,1,2,3], names=['x','y','z','V'])
    interp = NNip(COMSOL[['x','y','z']], np.arange(0,len(COMSOL['V'])))
    _NN = interp(r05)
    return _NN

_NN = get_NN(r05)
_NN = COMSOL['V'].iloc[_NN].to_numpy()
# print(_NN)

def get_NN2(r05):
    COMSOL = pd.read_csv("COMSOL.txt", sep="\s+", header=8, usecols=[0,1,2,3], names=['x','y','z','V'])
    interp = NNip(COMSOL[['x','y','z']], COMSOL[['V']])
    _NN = interp(r05)
    return _NN

_NN = get_NN2(r05)
# print(_NN)

class comsol():
    def __init__(self, comsol_file):
        self._comsol = pd.read_csv(comsol_file, sep="\s+", header=8, usecols=[0,1,2,3], names=['x','y','z','V'])
        self._NN = {}

    def get_NN(self):
        for gid in range(0,100):
            interp = NNip(self._comsol[['x','y','z']], np.arange(len(self._comsol['V'])))
            r05 = r05 = 100*np.random.rand(3,100)
            self._NN[gid] = interp(r05.T)

        return self._NN
            
    def get_V(self,gid):
            NN = self._NN[gid]
            return self._comsol['V'].iloc[NN].to_numpy()

test = comsol('biophys_components/stimulations/COMSOL copy.txt')
test.get_NN()
out = test.get_V(4)
vec = h.Vector(out)
for x in vec: 
    print(x)


