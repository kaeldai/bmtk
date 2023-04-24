import matplotlib.pyplot as plt
import sys
import numpy as np
sys.path.append('../../..')
sys.path.append('../..')
sys.path.append('..')
sys.path.append('../../bio_components')
sys.path.append('../bio_components')
from bmtk.analyzer.compartment import plot_traces
from bmtk.analyzer.spike_trains import plot_raster, plot_rates_boxplot
from bio_components.plot import plot_activity_3d, plot_activity_2d, plot_activity_distance, plot_activity_2d_smooth, plotting_params
from bio_components.statistical_analysis import centroid_cov, manova

config_comsol = 'exp1/config/1/-/20/config_01-_20_0.json'
config_xstim = 'xstim/config_xstim_0.json'
config_file = 'config.json'
# config_file = 'config.simulation_vm.json'
# config_file = 'config.simulation_ecp.json'

# Setting show to False so we can display all the plots at the same time
# plot_raster(config_file=config_file, show=False) # , group_by='model_name', show=False)
# plot_rates_boxplot(config_file=config_file, group_by='model_name', show=False)
# if config_file == 'config.simulation_vm.json':
#     plot_traces(
#         config_file='config.simulation_vm.json', report_name='membrane_potential', group_by='model_name',
#         times=(0.0, 200.0), show=False
#     )

# plt.show()

# plot_raster(config_file=config_comsol)

# stdvs = centroid_cov(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     spikes_dir = 'output_comsol_z+/z+_gnd_+-/spikes.csv',
#     background_dir = 'output/25/spikes.csv',
#     v1 = True
# )
# print(stdvs[0],stdvs[1])

# plot_activity_2d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/elec_loc/1.csv',
#     spikes_dir = 'exp1/output/1/-/30/01-_30_0/spikes.csv',
#     spikes_bg_dir = 'exp1/output/bkg/bkg_0/spikes.csv',
#     v1=True,
#     show=False,
# )

for t in [200]: 
    grid1 = plot_activity_2d_smooth(**plotting_params('1','-','30',['0','1','2']),
        v1=True,
        show=False,
        t_stop=t,
        save_dir=True
    )

    grid2 = plot_activity_2d_smooth(**plotting_params('7','-','30',['0','1','2']),
        v1=True,
        show=False,
        t_stop=t,
        save_dir=True
    )

    fig = plt.figure(figsize=(9,12))
    ax1 = plt.subplot(1,2,1)
    grid = grid1-grid2
  
    # grid = np.abs(grid)

    # for i in range(len(grid)):
    #     for j in range(len(grid)):
    #         if grid[i,j,1] < 0:
    #             grid[i,j,:] = -grid[i,j,1]
    #         else:
    #             grid[i,j,:] = grid[i,j,1]


    ax1.imshow(grid)

    ax2 = plt.subplot(1,2,2)
    grid = grid2-grid1
    ax2.imshow(grid)

    # plot_activity_2d(
    #     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
    #     electrodes_dir = '../bio_components/stimulations/elec_loc/1.csv',
    #     spikes_dir = 'exp1/output/1/-/30/01-_30_0/spikes.csv',
    #     spikes_bg_dir = 'exp1/output/bkg/bkg_0/spikes.csv',
    #     v1=True,
    #     show=False,
    # )

    print(centroid_cov(
        nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
        spikes_dir = 'exp1/output/1/-/30/01-_30_0/spikes.csv',
        spikes_bg_dir = 'exp1/output/bkg/bkg_0/spikes.csv',
        t_stop = t,
        v1 = True
    )[0])


# plot_activity_3d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/elec_loc/1.csv',
#     spikes_dir = 'exp1/output/1/g/30/01g_30_0/spikes.csv',
#     spikes_bg_dir = 'exp1/output/bkg/bkg_0/spikes.csv',
#     v1=True,
#     show=False,
# )



plt.show(block=False)
plt.pause(0.001)
input('')
plt.close('all')
