import os

from bmtk.utils.sonata.circuit import load_path

def test_load_files():
    fdir = os.path.dirname(os.path.realpath(__file__))

    net = load_path(file_path=os.path.join(fdir, 'examples/v1_nodes.h5'),
                    node_types_path=os.path.join(fdir, 'examples/v1_node_types.csv'))
    assert(net.has_nodes)
    assert(len(net.nodes) == 1)
    assert(not net.has_edges)
    assert(len(net.edges) == 0)
    assert(net.nodes.population_names == ['v1'])

    net = load_path(file_path=os.path.join(fdir, 'examples/v1_v1_edges.h5'),
                    edge_types_path=os.path.join(fdir, 'examples/v1_v1_edge_types.csv'))
    assert(not net.has_nodes)
    assert(len(net.nodes) == 0)
    assert(net.has_edges)
    assert(len(net.edges) == 1)
    assert(net.edges.population_names == ['v1_to_v1'])


def test_load_hdf5_nocsv():
    fdir = os.path.dirname(os.path.realpath(__file__))

    net = load_path(file_path=os.path.join(fdir, 'examples/v1_nodes.h5'))
    assert(net.has_nodes)
    assert(len(net.nodes) == 1)
    assert(not net.has_edges)
    assert(len(net.edges) == 0)
    assert(net.nodes.population_names == ['v1'])

    net = load_path(file_path=os.path.join(fdir, 'examples/v1_v1_edges.h5'))
    assert(not net.has_nodes)
    assert(len(net.nodes) == 0)
    assert(net.has_edges)
    assert(len(net.edges) == 1)
    assert(net.edges.population_names == ['v1_to_v1'])


fdir = os.path.dirname(os.path.realpath(__file__))
net = load_path(file_path=os.path.join(fdir, 'examples/v1_nodes.h5'))
#print(net.nodes['v1'].node_ids)
#print(net.nodes['v1'].get_row(0))
#print(net.nodes['v1'].get_node_id(0))
#print(net.nodes['v1'].get_node_id(5))
print(net.nodes['v1'].groups[0].group_id)




"""
if __name__ == '__main__':
    #test_load_files()
    #test_load_hdf5_nocsv()
"""