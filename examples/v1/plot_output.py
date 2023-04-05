import matplotlib.pyplot as plt
import sys
import numpy as np
sys.path.append('../..')
sys.path.append('..')
sys.path.append('../bio_components')
from bmtk.analyzer.compartment import plot_traces
from bmtk.analyzer.spike_trains import plot_raster, plot_rates_boxplot
from bio_components.plot import plot_activity_3d, plot_activity_2d, plot_activity_distance, plot_activity_distance
from bio_components.statistical_analysis import centroid_cov

config_comsol = 'config_comsol_0c.json'
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

# plot_raster(config_file=config_xstim)

stdvs = centroid_cov(
    nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
    spikes_dir = 'output_comsol/z+/spikes.csv',
    background_dir = 'output/25/spikes.csv',
    v1 = True
)
print(stdvs[0],stdvs[1])

stdvs = centroid_cov(
    nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
    spikes_dir = 'output_comsol/z+_L/spikes.csv',
    background_dir = 'output/25/spikes.csv',
    v1 = True
)
print(stdvs[0],stdvs[1])

# plot_raster('9/config_comsol_z+.json', show=False)
# plot_raster('9/config_comsol_z+_L.json', show=False)

plot_activity_2d(
    nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
    electrodes_dir = '../bio_components/stimulations/z+.csv',
    spikes_dir = 'output_comsol_z+/z+_gnd_+-/spikes.csv',
    spikes_bg_dir = 'output/25/spikes.csv',
    v1=True,
    show=False,
    save_dir='figures/z+'
)

plot_activity_2d(
    nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
    electrodes_dir = '../bio_components/stimulations/z+.csv',
    spikes_dir = 'output_comsol_z+/z+_gnd_+0/spikes.csv',
    spikes_bg_dir = 'output/25/spikes.csv',
    v1=True,
    show=False,
    save_dir='figures/x+'
)

# plot_activity_2d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/z-.csv',
#     spikes_dir = 'output_comsol/z-_L/spikes.csv',
#     spikes_bg_dir = 'output/25/spikes.csv',
#     v1=True,
#     show=False,
#     save_dir='figures/z-'
# )

# plot_activity_2d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/x-.csv',
#     spikes_dir = 'output_comsol/x-_L/spikes.csv',
#     spikes_bg_dir = 'output/25/spikes.csv',
#     v1=True,
#     show=False,
#     save_dir='figures/x-'
# )

# plot_activity_2d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/z+x-.csv',
#     spikes_dir = 'output_comsol/z+x-_L/spikes.csv',
#     spikes_bg_dir = 'output/25/spikes.csv',
#     v1=True,
#     show=True,
#     save_dir='figures/x+z-'
# )

# plot_activity_2d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/z+x-.csv',
#     spikes_dir = 'output_comsol/z+x-_L/spikes.csv',
#     spikes_bg_dir = 'output/25/spikes.csv',
#     v1=True,
#     show=True,
#     save_dir='figures/x+z-'
# )

# plot_activity_2d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/z+x-.csv',
#     spikes_dir = 'output_comsol/z+x-_L/spikes.csv',
#     spikes_bg_dir = 'output/25/spikes.csv',
#     v1=True,
#     show=True,
#     save_dir='figures/x+z-'
# )

# plot_activity_2d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/z+x-.csv',
#     spikes_dir = 'output_comsol/z+x-_L/spikes.csv',
#     spikes_bg_dir = 'output/25/spikes.csv',
#     v1=True,
#     show=True,
#     save_dir='figures/x+z-'
# )

# plot_activity_2d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/x-.csv',
#     spikes_dir = 'output_comsol/x-_L/spikes.csv',
#     spikes_bg_dir = 'output/25/spikes.csv',
#     v1=True,
#     show=False
# )

# plot_activity_3d(
#     nodes_dir = 'networks_rebuilt/network25/v1_nodes.h5',
#     electrodes_dir = '../bio_components/stimulations/x-.csv',
#     spikes_dir = 'output_comsol/x-/spikes.csv',
#     spikes_bg_dir = 'output/25/spikes.csv',
#     v1=True,
#     show=True
# # )


plt.show()