import sys
from pathlib import Path
import argparse

from bmtk.utils.integration_tester import get_return_code
from bmtk.utils.integration_tester import NodesFile, EdgesFile


def check_lgn_nodes(network_dir):
    nodes = NodesFile(network_dir / 'lgn_nodes.h5', network_dir / 'lgn_node_types.csv')
    return nodes['lgn'].run_checks([
        {'check': 'is_valid', 'expected': True},
        {'check': 'n_nodes', 'expected': 84},
        {'check': 'n_node_types', 'expected': 3},
        {'check': 'n_groups', 'expected': 1},
        {'check': 'n_attributes', 'expected': 10},
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-to', nargs='?', type=str, default=None)
    parser.add_argument('--network-dir', nargs='?', type=str, default='network')
    parser.add_argument('--hide-results', action='store_true')
    args, unknown = parser.parse_known_args()
    network_dir = Path(args.network_dir)

    results = check_lgn_nodes(network_dir)

    if args.save_to:
        results.save_to(args.save_to)
    
    if not args.hide_results:
        results.display()
    
    sys.exit(get_return_code(results))
