import nest

from bmtk.simulator.pointnet.pyfunction_cache import add_cell_model, add_cell_processor


def loadNESTModel(cell, template_name, dynamics_params):
    return nest.Create(template_name, cell.n_nodes, dynamics_params)


add_cell_model(loadNESTModel, directive='nest', model_type='point_neuron', overwrite=False)
