import os
import math
import pandas as pd
import numpy as np
import six
from neuron import h

from scipy.interpolate import NearestNDInterpolator as NNip
from scipy.interpolate import LinearNDInterpolator as Lip

comsol_file = '../bio_components/stimulations/z+.txt'

header = pd.read_csv(comsol_file, sep="\s{3,}", header=None, skiprows=8, nrows=1, engine='python').to_numpy()[0] # load header row of .txt file
header[0] = header[0][2:]                               # remove '% ' before first column name
for i,col in enumerate(header):                         # remove superfluous characters before actual time value
    if col[0] == "V":
            header[i] = 0
timepoints = np.array(header[3:], dtype=float)    # create array of timepoints  

# load data in COMSOL output .txt file.  
comsol = pd.read_csv(comsol_file, sep="\s+", header=None, skiprows=9, names=header)           # load data from .txt file

_Lip = Lip(comsol[['x','y','z']], comsol[0])
L = {}

for i in range(2):
    test = np.random.rand(3,100)
    L[i] = _Lip(test.T)

print(L[1])