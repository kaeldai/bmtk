import sys
from pathlib import Path
import argparse

from bmtk.utils.integration_tester import get_return_code
from bmtk.utils.integration_tester import NodesFile, EdgesFile


def check_v1_nodes(network_dir):
    nodes = NodesFile(network_dir / 'v1_nodes.h5', network_dir / 'v1_node_types.csv')
    return nodes['v1'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_nodes', 'expected': 14},
        {'check': 'n_node_types', 'expected': 7},
        {'check': 'n_groups', 'expected': 4},
        {'check': 'n_attributes', 'expected': 14},
    ])


def check_lgn_nodes(network_dir):
    nodes = NodesFile(network_dir / 'lgn_nodes.h5', network_dir / 'lgn_node_types.csv')
    return nodes['lgn'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_nodes', 'expected': 90},
        {'check': 'n_node_types', 'expected': 3},
        {'check': 'n_groups', 'expected': 1},
        {'check': 'n_attributes', 'expected': 6},
    ])


def check_tw_nodes(network_dir):
    nodes = NodesFile(network_dir / 'tw_nodes.h5', network_dir / 'tw_node_types.csv')
    return nodes['tw'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_nodes', 'expected': 30},
        {'check': 'n_node_types', 'expected': 1},
        {'check': 'n_groups', 'expected': 1},
        {'check': 'n_attributes', 'expected': 4},
    ])


def check_v1_v1_edges(network_dir):
    edges = EdgesFile(network_dir / 'v1_v1_edges.h5', network_dir / 'v1_v1_edge_types.csv')
    return edges['v1_to_v1'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_connections', 'expected': 196},
        {'check': 'n_edge_groups', 'expected': 1},
        {'check': 'n_edge_type_ids', 'expected': 11},
        {'check': 'n_attributes', 'expected': 11},
        {'check': 'source_node_population', 'expected': 'v1'},
        {'check': 'target_node_population', 'expected': 'v1'},
        {'check': 'hdf5_attributes_contains', 'expected': True, 'args': ['nsyns']},
        {'check': 'hdf5_attributes_contains', 'expected': False, 'args': ['afferent_section_id']},
        {'check': 'hdf5_attributes_contains', 'expected': False, 'args': ['afferent_section_pos']},
        {'check': 'csv_attributes_contains', 'expected': True, 'args': ['target_sections']},
        {'check': 'csv_attributes_contains', 'expected': True, 'args': ['distance_range']},
    ])


def check_lgn_v1_edges(network_dir):
    edges = EdgesFile(network_dir / 'lgn_v1_edges.h5', network_dir / 'lgn_v1_edge_types.csv')
    return edges['lgn_to_v1'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_connections', 'expected': 660},
        {'check': 'n_edge_groups', 'expected': 1},
        {'check': 'n_edge_type_ids', 'expected': 7},
        {'check': 'n_attributes', 'expected': 10},
        {'check': 'source_node_population', 'expected': 'lgn'},
        {'check': 'target_node_population', 'expected': 'v1'},
        {'check': 'hdf5_attributes_contains', 'expected': True, 'args': ['nsyns']},
        {'check': 'csv_attributes_contains', 'expected': True, 'args': ['target_sections']},
        {'check': 'csv_attributes_contains', 'expected': True, 'args': ['distance_range']},
    ])


def check_tw_v1_edges(network_dir):
    edges = EdgesFile(network_dir / 'tw_v1_edges.h5', network_dir / 'tw_v1_edge_types.csv')
    return edges['tw_to_v1'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_connections', 'expected': 420},
        {'check': 'n_edge_groups', 'expected': 1},
        {'check': 'n_edge_type_ids', 'expected': 7},
        {'check': 'n_attributes', 'expected': 10},
        {'check': 'source_node_population', 'expected': 'tw'},
        {'check': 'target_node_population', 'expected': 'v1'},
        {'check': 'hdf5_attributes_contains', 'expected': True, 'args': ['nsyns']},
        {'check': 'csv_attributes_contains', 'expected': True, 'args': ['target_sections']},
        {'check': 'csv_attributes_contains', 'expected': True, 'args': ['distance_range']},
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-to', nargs='?', type=str, default=None)
    parser.add_argument('--network-dir', nargs='?', type=str, default='network')
    parser.add_argument('--hide-results', action='store_true')
    args, unknown = parser.parse_known_args()
    network_dir = Path(args.network_dir)

    results = check_v1_nodes(network_dir)
    results += check_lgn_nodes(network_dir)
    results += check_tw_nodes(network_dir)
    results += check_v1_v1_edges(network_dir)
    results += check_lgn_v1_edges(network_dir)
    results += check_tw_v1_edges(network_dir)

    if args.save_to:
        results.save_to(args.save_to)
    
    if not args.hide_results:
        results.display()
    
    sys.exit(get_return_code(results))
