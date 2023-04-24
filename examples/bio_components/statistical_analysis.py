import pandas as pd
from hdf5 import HDF5
import matplotlib.pyplot as plt
import numpy as np
import h5py as h5
from statsmodels.multivariate.manova import MANOVA
import statsmodels.api as sm
from statsmodels.formula.api import ols

def centroid_cov(nodes_dir, spikes_dir, spikes_bg_dir=None, v1=False, t_stop = 200):

    if v1 == True:
        node_pos = HDF5(nodes_dir).get_positions_v1()
    elif v1 == False:
        node_pos = HDF5(nodes_dir).get_positions()
    
    n_spikes = np.zeros((np.shape(node_pos)[0]))
    spikes = pd.read_csv(spikes_dir, sep='\s+')
    for ind in spikes.index:
        if spikes['timestamps'][ind] < t_stop:
            n_spikes[spikes['node_ids'][ind]] += 1

    if spikes_bg_dir is not None:
        spikes_bg = pd.read_csv(spikes_bg_dir, sep='\s+')
        for ind in spikes_bg.index:
            if spikes_bg['timestamps'][ind] < t_stop:
                n_spikes[spikes_bg['node_ids'][ind]] = max(0, n_spikes[spikes_bg['node_ids'][ind]] - 1)
    
    centroid = np.average(node_pos[n_spikes!=0], axis=0, weights=n_spikes[n_spikes!=0])
    cov = np.cov(node_pos[n_spikes!=0].T, fweights=n_spikes[n_spikes!=0])

    return centroid, cov


def manova(nodes_dirs, spikes_dirs, spikes_bg_dirs, electrodes_dir=None, t_stop=200):

    df = pd.DataFrame(columns=['x','y','z','i'])

    for i in range(len(nodes_dirs)):
        nodes_dir = nodes_dirs[i]
        spikes_dir = spikes_dirs[i]
        elec = spikes_dir[12]
        spikes_bg_dir = spikes_bg_dirs[i]
        node_pos = HDF5(nodes_dir).get_positions_v1()
        n_spikes = np.zeros(np.shape(node_pos)[0])
        spikes = pd.read_csv(spikes_dir, sep='\s+')
        for ind in spikes.index:
            if spikes['timestamps'][ind] < t_stop:
                n_spikes[spikes['node_ids'][ind]] += 1
        spikes_bg = pd.read_csv(spikes_bg_dir, sep='\s+')
        for ind in spikes_bg.index:
            n_spikes[spikes_bg['node_ids'][ind]] = max(0, n_spikes[spikes_bg['node_ids'][ind]] - 1)
        for j in range(len(n_spikes)):
            for k in range(np.int(n_spikes[j])):
                if node_pos[j,0]**2 + node_pos[j,2]**2 < 100**2:
                    df.loc[len(df)] = [node_pos[j,0],node_pos[j,1],node_pos[j,2],elec]

    # mod = ols('x ~ i', data=df).fit()
    # return sm.stats.anova_lm(mod)

    maov = MANOVA.from_formula('x + z ~ i', data=df)
    return maov.mv_test() 


def extract(names):
    
    nodes = []
    spikes = []
    spikes_bg =[]
    
    for name in names:
        electrode = name[1] 
        stim_type = name[2] 
        amplitude = name[4:6]
        network = name[7]

        nodes.append('networks_25/network' + network + '/v1_nodes.h5')
        spikes.append('exp1/output/'+ electrode + '/' + stim_type + '/' + amplitude + '/0' + electrode + stim_type + '_' + amplitude + '_' + network + '/spikes.csv')
        spikes_bg.append('exp1/output/bkg/bkg_' + network + '/spikes.csv')
    
    electrodes = '../bio_components/stimulations/elec_loc/' + electrode + '.csv'

    return dict(nodes_dirs=nodes, spikes_dirs=spikes, spikes_bg_dirs=spikes_bg, electrodes_dir=electrodes)

def do_manova(amplitudes, electrodes, stim_types, networks):
    
    nodes = []
    spikes = []
    spikes_bg =[]
    
    for amplitude in amplitudes:
        for electrode in electrodes:
            for stim_type in stim_types:
                for network in networks:

                    nodes.append('networks_25/network' + network + '/v1_nodes.h5')
                    spikes.append('exp1/output/'+ electrode + '/' + stim_type + '/' + amplitude + '/0' + electrode + stim_type + '_' + amplitude + '_' + network + '/spikes.csv')
                    spikes_bg.append('exp1/output/bkg/bkg_' + network + '/spikes.csv')
    
    electrodes = '../bio_components/stimulations/elec_loc/' + electrode + '.csv'

    return manova(nodes_dirs=nodes, spikes_dirs=spikes, spikes_bg_dirs=spikes_bg, electrodes_dir=electrodes)

if __name__ == "__main__":
    res = do_manova(
        amplitudes=['30'],
        electrodes=['1','6','8','2'],
        stim_types=['-'],
        networks=['0','1','2'],
    )
    print(res)