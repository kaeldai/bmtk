import sys
from pathlib import Path
import argparse

from bmtk.utils.integration_tester import get_return_code
from bmtk.utils.integration_tester import NodesFile, EdgesFile


def check_cortex_nodes(network_dir):
    nodes = NodesFile(network_dir / 'cortex_nodes.h5', network_dir / 'cortex_node_types.csv')
    return nodes['cortex'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_nodes', 'expected': 120},
        {'check': 'n_node_types', 'expected': 2},
        {'check': 'n_groups', 'expected': 1},
        {'check': 'n_attributes', 'expected': 8},
    ])


def check_thalamus_nodes(network_dir):
    nodes = NodesFile(network_dir / 'thalamus_nodes.h5', network_dir / 'thalamus_node_types.csv')
    return nodes['thalamus'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_nodes', 'expected': 100},
        {'check': 'n_node_types', 'expected': 1},
        {'check': 'n_groups', 'expected': 1},
        {'check': 'n_attributes', 'expected': 3},
    ])


def check_cortex_cortex_edges(network_dir):
    edges = EdgesFile(network_dir / 'cortex_cortex_edges.h5', network_dir / 'cortex_cortex_edge_types.csv')
    return edges['cortex_to_cortex'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_connections', 'between': [1000, 2000]},
        {'check': 'n_edge_groups', 'expected': 1},
        {'check': 'n_edge_type_ids', 'expected': 2},
        {'check': 'n_attributes', 'expected': 7},
        {'check': 'source_node_population', 'expected': 'cortex'},
        {'check': 'target_node_population', 'expected': 'cortex'},
        {'check': 'hdf5_attributes_contains', 'expected': True, 'args': ['nsyns']}
    ])


def check_thalamus_cortex_edges(network_dir):
    edges = EdgesFile(network_dir / 'thalamus_cortex_edges.h5', network_dir / 'thalamus_cortex_edge_types.csv')
    return edges['thalamus_to_cortex'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_connections', '>=': 500},
        {'check': 'n_edge_groups', 'expected': 1},
        {'check': 'n_edge_type_ids', 'expected': 1},
        {'check': 'n_attributes', 'expected': 7},
        {'check': 'source_node_population', 'expected': 'thalamus'},
        {'check': 'target_node_population', 'expected': 'cortex'},
        {'check': 'hdf5_attributes_contains', 'expected': True, 'args': ['nsyns']}
    ])



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-to', nargs='?', type=str, default=None)
    parser.add_argument('--network-dir', nargs='?', type=str, default='network')
    parser.add_argument('--hide-results', action='store_true')
    args, unknown = parser.parse_known_args()
    network_dir = Path(args.network_dir)

    results = check_cortex_nodes(network_dir)
    results += check_thalamus_nodes(network_dir)
    results += check_cortex_cortex_edges(network_dir)
    results += check_thalamus_cortex_edges(network_dir)

    if args.save_to:
        results.save_to(args.save_to)
    
    if not args.hide_results:
        results.display()
    
    sys.exit(get_return_code(results))
