import pandas as pd
from hdf5 import HDF5
import matplotlib.pyplot as plt
import numpy as np
import h5py as h5

def centroid_cov(nodes_dir, spikes_dir, background_dir=None, v1=False):

    if v1 == True:
        node_pos = HDF5(nodes_dir).get_positions_v1()
    elif v1 == False:
        node_pos = HDF5(nodes_dir).get_positions()
    
    n_spikes = np.zeros((np.shape(node_pos)[0]))
    spikes = pd.read_csv(spikes_dir, sep='\s+')['node_ids'].to_numpy()
    for spike in spikes:
        n_spikes[spike] += 1
    if background_dir is not None:
        bg_spikes = pd.read_csv(background_dir, sep='\s+')['node_ids'].to_numpy()
        for bg_spike in bg_spikes:
            n_spikes[bg_spike] = max(n_spikes[bg_spike]-1,0)
    
    centroid = np.average(node_pos[n_spikes!=0], axis=0, weights=n_spikes[n_spikes!=0])
    cov = np.cov(node_pos[n_spikes!=0].T, fweights=n_spikes[n_spikes!=0])

    return centroid, cov