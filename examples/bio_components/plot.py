import pandas as pd
from hdf5 import HDF5
import matplotlib.pyplot as plt
import numpy as np
import h5py as h5

def plot_activity_3d(nodes_dir, electrodes_dir, spikes_dir, save_dir=None, square_axis=False, spikes_bg_dir=None, v1=False):
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
            n_spikes[spikes_bg['node_ids'][ind]] = np.max([n_spikes[spikes_bg['node_ids'][ind]] - 1, 0])


    fig = plt.figure(figsize=(9,12))
    ax = plt.axes(projection="3d")
    
    active = node_pos[n_spikes!=0,:]
    inactive = node_pos[n_spikes==0,:]

    p = ax.scatter(active[:,0], active[:,1], active[:,2], marker='o', s=20, cmap='cool', c=n_spikes[n_spikes!=0], label='activated neuron')
    ax.scatter(inactive[:,0], inactive[:,1], inactive[:,2], marker='o', s=1, c='0.2', alpha=0.2, label='non-activated neuron')
    if electrodes_dir is not None:
        elec_pos = pd.read_csv(electrodes_dir, sep=' ')
        elec_pos = elec_pos[['pos_x', 'pos_y', 'pos_z']].to_numpy()[0]
        ax.scatter(elec_pos[0], elec_pos[1], elec_pos[2], marker = 'd', s=100, color = 'r', label = 'electrode')
    ax.view_init(elev=5., azim=0)
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
        max_range = np.array([X.max()-X.min(), Y.max()-Y.min(), Z.max()-Z.min()]).max()
        Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(X.max()+X.min())
        Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(Y.max()+Y.min())
        Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(Z.max()+Z.min())
        # Comment or uncomment following both lines to test the fake bounding box:
        for xb, yb, zb in zip(Xb, Yb, Zb):
            ax.plot([xb], [yb], [zb], 'w')

    cbar = plt.colorbar(p, label='# spikes [-]', shrink=0.5, pad=-0.1)
    cbar.set_ticks(range(1,int(max(n_spikes))+1))
    if save_dir is not None:
        plt.savefig(save_dir, bbox_inches='tight', transparent=True)
    print(n_spikes[n_spikes!=0])
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

# plot_activity_distance(
#     nodes_dir = 'network/slice_nodes.h5',
#     electrodes_dir = 'biophys_components/stimulations/50.csv',
#     spikes_dirs = ['outputs/output_xstim50/spikes.csv'],
#     save_dir = 'figures/a_d_20',
#     legend = ['I = 20 $\mu A$']
# )

# plot_activity_distance(
#     nodes_dir = 'network/slice_nodes.h5',
#     electrodes_dir = 'biophys_components/stimulations/50.csv',
#     spikes_dirs = ['outputs/output_xstim50/spikes.csv', 'outputs/output_xstim/spikes.csv'],
#     save_dir = 'figures/a_d_20_50',
#     legend = ['I = 20 $\mu A$', 'I = 50 $\mu A$']
# )

# plot_activity_3d(
#     nodes_dir = 'network/slice_nodes.h5',
#     electrodes_dir = 'biophys_components/stimulations/50.csv',
#     spikes_dir = 'outputs/output_xstim/spikes.csv',
#     save_dir = 'figures/3d_50',
# )

# plot_activity_3d(
#     nodes_dir = 'network/slice_nodes.h5',
#     electrodes_dir = 'biophys_components/stimulations/50.csv',
#     spikes_dir = 'outputs/output_xstim50/spikes.csv',
#     save_dir = 'figures/3d_20',
# )

# plot_activity_3d(
#     nodes_dir = '../network/slice_nodes.h5',
#     electrodes_dir = 'stimulations/50.csv',
#     spikes_dir = '../outputs/output_comsol/spikes.csv',
#     save_dir = None,
# )

# plot_positions(nodes_dir = '../comsol/network/column_nodes.h5')

# plot_positions('network/slice_nodes.h5')


### PLOT V1 MOUSE MODEL 
# v1 = h5.File('/users/students/r0754386/Documents/bmtk/examples/v1/network/v1_nodes.h5')['nodes']['v1']['0']
# x_pos = v1['x']
# y_pos = v1['y']
# z_pos = v1['z']
# labels = ['X [$\mu m$]', 'Y [$\mu m$]', 'Z [$\mu m$]']
#
# fig = plt.figure(figsize=(9,12))
# ax = plt.axes(projection="3d")
#
# p = ax.scatter(x_pos, y_pos, z_pos, marker='o', s=20)
# ax.view_init(elev=5., azim=0)
# ax.set_xlabel(labels[0])
# ax.set_ylabel(labels[1])
# ax.set_zlabel(labels[2])
# ax.legend(loc='center', bbox_to_anchor=(1, 0.5))
# plt.show()


# plot_activity_3d(
#     nodes_dir = '../comsol/network/column_nodes.h5',
#     electrodes_dir = './stimulations/elec_comsol.csv',
#     spikes_dir = '../comsol/output/spikes.csv',
#     save_dir = '../comsol/figures/3d_50',
# )