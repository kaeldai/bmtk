import pandas as pd
from hdf5 import HDF5
import matplotlib.pyplot as plt
import numpy as np
import h5py as h5
from statistical_analysis import centroid_cov
from scipy.ndimage import gaussian_filter, rotate
import os

def plot_activity_3d(nodes_dir, electrodes_dir, spikes_dir, save_dir=None, square_axis=False, spikes_bg_dir=None, v1=False, show=False):
    if v1 == True:
        node_pos = HDF5(nodes_dir).get_positions_v1()
    elif v1 == False:
        node_pos = HDF5(nodes_dir).get_positions()
    n_spikes = np.zeros((np.shape(node_pos)[0]))

    spikes = pd.read_csv(spikes_dir, sep='\s+')
    for ind in spikes.index:
        n_spikes[spikes['node_ids'][ind]] += 1

    if spikes_bg_dir is not None:
        spikes_bg = pd.read_csv(spikes_bg_dir, sep='\s+')
        for ind in spikes_bg.index:
            n_spikes[spikes_bg['node_ids'][ind]] = n_spikes[spikes_bg['node_ids'][ind]] - 1

    fig = plt.figure(figsize=(9,12))
    ax = plt.axes(projection="3d")
    
    active = node_pos[n_spikes!=0,:]
    inactive = node_pos[n_spikes==0,:]

    p = ax.scatter(active[:,0], active[:,1], active[:,2], marker='o', s=n_spikes[n_spikes!=0], alpha=0.5, cmap='cool', c=n_spikes[n_spikes!=0], label='activated neuron')
    if v1:
        subset = np.random.choice(np.shape(inactive)[0], round(0.01*np.shape(inactive)[0]))
        inactive = inactive[subset,:]
    # ax.scatter(inactive[:,0], inactive[:,1], inactive[:,2], marker='o', s=1, c='0.05', alpha=0.05, label='non-activated neuron')
    centroid = centroid_cov(nodes_dir, spikes_dir=spikes_dir, background_dir=spikes_bg_dir, v1=True)[0]
    ax.scatter(centroid[0], centroid[1], centroid[2], marker = '8', s=30, color = 'b', label = 'centroid')
    cbar = plt.colorbar(p, label='# spikes [-]', shrink=0.5, pad=-0.1, anchor=(0.5, 1.0), panchor=(0.5, 0.0), orientation='horizontal')
    if len(n_spikes[n_spikes!=0]) > 0:
        cbar.set_ticks(range(int(min(n_spikes[n_spikes!=0])),int(max(n_spikes))+1))
    
    if electrodes_dir is not None:
        elec_pos = pd.read_csv(electrodes_dir, sep=' ')
        elec_pos = elec_pos[['pos_x', 'pos_y', 'pos_z']].to_numpy()
        ax.scatter(elec_pos[0,0], elec_pos[0,1], elec_pos[0,2], marker = 's', s=50, color = 'r', label = 'electrode')
        ax.scatter(elec_pos[1:,0], elec_pos[1:,1], elec_pos[1:,2], marker = 's', s=50, color = 'k', label = 'electrode')
    
    ax.view_init(elev=5., azim=-90)
    labels = ['X [$\mu m$]', 'Y [$\mu m$]', 'Z [$\mu m$]']
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_zlabel(labels[2])
    ax.legend(loc='center', bbox_to_anchor=(1, 0.5))

    if square_axis:
        # Create cubic bounding box to simulate equal aspect ratio
        X = node_pos[:,0]
        Y = node_pos[:,1]
        Z = node_pos[:,2]
        # max_range = np.array([X.max()-X.min(), Y.max()-Y.min(), Z.max()-Z.min()]).max()
        max_range = np.array([X.max(), Y.max(), Z.max()]).max()
        Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(X.max()+X.min())
        Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(Y.max()+Y.min())
        Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(Z.max()+Z.min())
        # Comment or uncomment following both lines to test the fake bounding box:
        for xb, yb, zb in zip(Xb, Yb, Zb):
            ax.plot([xb], [yb], [zb], 'w')

    if save_dir is not None:
        plt.savefig(save_dir, bbox_inches='tight', transparent=True)
    if show:
        plt.show()


def plot_positions(nodes_dir, save_dir=None):
    node_pos = HDF5(nodes_dir).get_positions()
    labels = ['X [$\mu m$]', 'Y [$\mu m$]', 'Z [$\mu m$]']

    fig = plt.figure(figsize=(9,12))
    ax = plt.axes(projection="3d")

    p = ax.scatter(node_pos[:,0], node_pos[:,1], node_pos[:,2], marker='o', s=20)
    ax.view_init(elev=5., azim=0)
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_zlabel(labels[2])
    ax.legend(loc='center', bbox_to_anchor=(1, 0.5))
    if save_dir is not None:
        plt.savefig(save_dir, bbox_inches='tight', transparent=True)
    plt.show()


def plot_activity_distance(nodes_dir, electrodes_dir, spikes_dirs, save_dir=None, legend=None):
    node_pos = HDF5(nodes_dir).get_positions_v1()
    elec_pos = pd.read_csv(electrodes_dir, sep=' ')
    elec_pos = elec_pos[['pos_x', 'pos_y', 'pos_z']].to_numpy()[0]

    r = np.zeros(np.size(node_pos, axis=0))
    for i in range(np.size(r)):
        r[i] = np.sqrt(((elec_pos-node_pos[i,:])**2).sum())

    fig = plt.figure()
    for spikes_dir in spikes_dirs:
        spikes = pd.read_csv(spikes_dir, sep='\s+')
        n_spikes = np.zeros((np.shape(node_pos)[0]))
        for ind in spikes.index:
            n_spikes[spikes['node_ids'][ind]] += 1
        plt.scatter(r[n_spikes!=0], n_spikes[n_spikes!=0], s=20, marker='o')
    
    plt.xlabel('distance to electrode [$\mu m$]')
    plt.ylabel('# spikes [-]')
    plt.title('Number of spikes per neuron')
    plt.yticks(range(0,int(np.max(n_spikes)+1)))
    if legend is not None:
        plt.legend(legend, loc='best')
    if save_dir is not None:
        plt.savefig(save_dir, transparent=True, bbox_inches='tight')
    plt.show()

def plot_activity_2d(nodes_dir, spikes_dir, electrodes_dir=None, save_dir=None, square_axis=True, spikes_bg_dir=None, v1=False, show=False):
    if v1 == True:
        node_pos = HDF5(nodes_dir).get_positions_v1()
    elif v1 == False:
        node_pos = HDF5(nodes_dir).get_positions()
    n_spikes = np.zeros((np.shape(node_pos)[0]))

    spikes = pd.read_csv(spikes_dir, sep='\s+')
    for ind in spikes.index:
        n_spikes[spikes['node_ids'][ind]] += 1

    if spikes_bg_dir is None:
        spikes_bg_dir = 'exp1/output/bkg/bkg_' + spikes_dir[14] + '/spikes.csv',
        
    spikes_bg = pd.read_csv(spikes_bg_dir, sep='\s+')
    for ind in spikes_bg.index:
        n_spikes[spikes_bg['node_ids'][ind]] = n_spikes[spikes_bg['node_ids'][ind]] - 1

    fig = plt.figure(figsize=(9,12))
    ax = fig.add_subplot()

    active = node_pos[n_spikes!=0,:]
    inactive = node_pos[n_spikes==0,:]

    p = plt.scatter(active[:,0], active[:,2], marker='o', s=2*n_spikes[n_spikes!=0], alpha=0.5, cmap='cool', c=n_spikes[n_spikes!=0], label='activated neuron')
    circle = np.sqrt(inactive[:,0]**2 + inactive[:,2]**2)
    inactive = inactive[circle<400,:]
    if v1:
        subset = np.random.choice(np.shape(inactive)[0], round(0.5*np.shape(inactive)[0]))
        inactive = inactive[subset,:]
    plt.scatter(inactive[:,0], inactive[:,2], marker='o', s=1, c='0.05', alpha=0.05, label='non-activated neuron')
    centroid = centroid_cov(nodes_dir, spikes_dir=spikes_dir, spikes_bg_dir=spikes_bg_dir, v1=True)[0]
    plt.scatter(centroid[0], centroid[2], marker = '8', s=50, color = 'b', label = 'centroid')
    cbar = plt.colorbar(p, label='# spikes [-]', orientation='vertical')
    if len(n_spikes[n_spikes!=0]) > 0:
        cbar.set_ticks(range(int(min(n_spikes[n_spikes!=0])),int(max(n_spikes))+1))
    
    if electrodes_dir is not None:
        elec_pos = pd.read_csv(electrodes_dir, sep=' ')
        elec_pos = elec_pos[['pos_x', 'pos_y', 'pos_z']].to_numpy()
        plt.scatter(elec_pos[0,0], elec_pos[0,2], marker = 's', s=100, color = 'r', label = 'electrode')
        plt.scatter(elec_pos[1:,0], elec_pos[1:,2], marker = 's', s=100, color = 'k', label = 'electrode')
    
    labels = ['X [$\mu m$]', 'Y [$\mu m$]', 'Z [$\mu m$]']
    plt.xlabel(labels[0])
    plt.ylabel(labels[2])
    plt.legend(loc='upper right')

    if square_axis:
        plt.axis(xmin=-400, xmax=400, ymin=-400, ymax=400)
        ax.set_aspect('equal', adjustable='box')
        
    if save_dir is not None:
        plt.savefig(save_dir, bbox_inches='tight', transparent=True)
    if show:
        plt.show()


def plot_activity_2d_smooth(nodes_dirs, spikes_dirs, spikes_bg_dirs=None, electrodes_dir=None, save_dir=None, square_axis=True, v1=False, show=False, t_stop=200):
    factor = 1
    size = int(800/factor)
    for i in range(len(nodes_dirs)):
        nodes_dir = nodes_dirs[i]
        if v1 == True:
            node_pos = HDF5(nodes_dir).get_positions_v1()
        elif v1 == False:
            node_pos = HDF5(nodes_dir).get_positions()
        n_spikes = np.zeros((np.shape(node_pos)[0]))

        spikes_dir = spikes_dirs[i]
        spikes_bg_dir = spikes_bg_dirs[i]

        spikes = pd.read_csv(spikes_dir, sep='\s+')
        for ind in spikes.index:
            if spikes['timestamps'][ind] < t_stop:
                n_spikes[spikes['node_ids'][ind]] += 1

        if spikes_bg_dirs is None:
            spikes_bg_dir = 'exp1/output/bkg/bkg_' + spikes_dir[26] + '/spikes.csv'
        if os.path.exists(spikes_bg_dir):
            spikes_bg = pd.read_csv(spikes_bg_dir, sep='\s+')
            for ind in spikes_bg.index:
                n_spikes[spikes_bg['node_ids'][ind]] = max(0, n_spikes[spikes_bg['node_ids'][ind]] - 1)
            
        active = node_pos[n_spikes!=0,:]/factor
        circle = np.sqrt(active[:,0]**2 + active[:,2]**2)
        active = active[circle<size/2,:]


        grid = np.zeros((size,size,3))    
        for node in range(len(active[:,1])):
            grid_el = (np.floor(active[node,[0,2]] + size/2)).astype(np.int)
            grid[size-grid_el[1],grid_el[0],1] += n_spikes[n_spikes!=0][node]
    
    grid[:,:,1] = gaussian_filter(grid[:,:,1],10/factor)
    grid[:,:,1] /= np.max(grid[:,:,1], axis=None)

    grid_bg = np.zeros((size,size,3))
    for i in range(len(grid)):
        for j in range(len(grid)):
            if (i-size/2)**2 + (j-size/2)**2 > (size/2)**2:
                grid_bg[i,j,:] = 0.99

    grid_bg[:,:,:] = gaussian_filter(grid_bg[:,:,:],1)

    fig = plt.figure(figsize=(9,12))
    ax = fig.add_subplot()
    ax.imshow(grid+grid_bg)
    plt.xticks(np.arange(0,size,size/8), (np.arange(0,size,size/8)-size/2).astype(int))
    plt.yticks(np.arange(0,size,size/8), (np.arange(size,0,-size/8)-size/2).astype(int))

    if electrodes_dir is None:
        electrodes_dir = '../bio_components/stimulations/elec_loc/' + spikes_dir[12] + '.csv'
    elec_pos = pd.read_csv(electrodes_dir, sep=' ')
    elec_pos = change_coord(elec_pos[['pos_x', 'pos_y', 'pos_z']].to_numpy(),factor=factor)
    ax.scatter(elec_pos[0,0], elec_pos[0,2], marker = '+', s=100, color = 'red', label = 'central electrode')
    ax.scatter(elec_pos[1:,0], elec_pos[1:,2], marker = '+', s=100, color = 'white', label = 'return electrode')

    centroid = change_coord(centroid_cov(nodes_dir, spikes_dir=spikes_dir, spikes_bg_dir=spikes_bg_dir, v1=True)[0],factor=factor)
    ax.scatter(centroid[0], centroid[2], marker = '+', s=100, color = 'b', label = 'centroid')

    plt.title('return electrode: ' + spikes_dir[12] + ', stimulation type: ' + spikes_dir[14] + ', amplitude: ' + spikes_dir[16:18] + ' uA')

    if save_dir is not None:
        if save_dir == True:
            plt.savefig(spikes_dirs[0][0:4]+'/figures/'+spikes_dirs[0][-19:-11]) 

    ax.legend(facecolor='black',framealpha=0.3)
    if show:
        ax.show()

    return grid+grid_bg

        
def change_coord(array, factor=1):

    array = (array+400)/factor
    if len(np.shape(array)) > 1:
        array[:,2] = 800/factor-array[:,2]
    else:
        array[2] = 800/factor-array[2]
    return array


def plotting_params(electrode, stim_type, amplitude, networks):

    nodes = []
    spikes = []
    spikes_bg =[]

    for network in networks:
        nodes.append('networks_25/network' + network + '/v1_nodes.h5')
        spikes.append('exp1/output/'+ electrode + '/' + stim_type + '/' + amplitude + '/0' + electrode + stim_type + '_' + amplitude + '_' + network + '/spikes.csv')
        spikes_bg.append('exp1/output/bkg/bkg_' + network + '/spikes.csv')
    electrodes = '../bio_components/stimulations/elec_loc/' + electrode + '.csv'

    return dict(nodes_dirs=nodes, spikes_dirs=spikes, spikes_bg_dirs=spikes_bg, electrodes_dir=electrodes)