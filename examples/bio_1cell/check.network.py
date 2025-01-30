import sys
from pathlib import Path
import argparse

from bmtk.utils.integration_tester import get_return_code
from bmtk.utils.integration_tester import NodesFile, EdgesFile


def check_biocell_nodes(network_dir):
    nodes = NodesFile(network_dir / 'biocell_nodes.h5', network_dir / 'biocell_node_types.csv')
    return nodes['biocell'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_nodes', 'expected': 1},
        {'check': 'n_node_types', 'expected': 1},
        {'check': 'n_groups', 'expected': 1},
        {'check': 'n_attributes', 'expected': 12},
    ])


def check_virt_nodes(network_dir):
    nodes = NodesFile(network_dir / 'virt_nodes.h5', network_dir / 'virt_node_types.csv')
    return nodes['virt'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_nodes', 'expected': 1},
        {'check': 'n_node_types', 'expected': 1},
        {'check': 'n_groups', 'expected': 1},
        {'check': 'n_attributes', 'expected': 1},
    ])


def check_virt_biocell_edges(network_dir):
    edges = EdgesFile(network_dir / 'virt_biocell_edges.h5', network_dir / 'virt_biocell_edge_types.csv')
    return edges['virt_to_biocell'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_connections', 'expected': 12},
        {'check': 'n_edge_groups', 'expected': 1},
        {'check': 'n_edge_type_ids', 'expected': 1},
        {'check': 'n_attributes', 'expected': 8},
        {'check': 'source_node_population', 'expected': 'virt'},
        {'check': 'target_node_population', 'expected': 'biocell'},
        {'check': 'hdf5_attributes_contains', 'expected': False, 'args': ['nsyns']},
        {'check': 'hdf5_attributes_contains', 'expected': True, 'args': ['afferent_section_id']},
        {'check': 'hdf5_attributes_contains', 'expected': True, 'args': ['afferent_section_pos']},
        {'check': 'csv_attributes_contains', 'expected': False, 'args': ['target_sections']},
        {'check': 'csv_attributes_contains', 'expected': False, 'args': ['distance_range']},
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-to', nargs='?', type=str, default=None)
    parser.add_argument('--network-dir', nargs='?', type=str, default='network')
    parser.add_argument('--hide-results', action='store_true')
    args, unknown = parser.parse_known_args()
    network_dir = Path(args.network_dir)

    results = check_biocell_nodes(network_dir)
    results += check_virt_nodes(network_dir)
    results += check_virt_biocell_edges(network_dir)

    if args.save_to:
        results.save_to(args.save_to)
    
    if not args.hide_results:
        results.display()
    
    sys.exit(get_return_code(results))
