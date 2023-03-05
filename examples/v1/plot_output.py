import matplotlib.pyplot as plt
import sys
sys.path.append('../..')
sys.path.append('..')
sys.path.append('../bio_components')
from bmtk.analyzer.compartment import plot_traces
from bmtk.analyzer.spike_trains import plot_raster, plot_rates_boxplot
from bio_components.plot import plot_activity_3d, plot_activity_distance, plot_activity_distance

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

plot_activity_3d(
    nodes_dir = 'networks_rebuilt/network10/v1_nodes.h5',
    electrodes_dir = None,
    spikes_dir = 'output_xstim/0_10/spikes.csv',
    spikes_bg_dir = 'output/spikes.csv',
    v1=True
)

plot_activity_3d(
    nodes_dir = 'networks_rebuilt/network10/v1_nodes.h5',
    electrodes_dir = None,
    spikes_dir = 'output_comsol/0_10/spikes.csv',
    spikes_bg_dir = 'output/spikes.csv',
    v1=True
)