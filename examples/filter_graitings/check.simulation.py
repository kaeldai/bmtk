import sys
from pathlib import Path
import argparse

from bmtk.utils.integration_tester import get_return_code
from bmtk.utils.integration_tester import SpikesFile, ConfigJSON


def check_spikes(file_path):
    spikes_report = SpikesFile(file_path)
    return spikes_report['lgn'].run_checks([
        {'check': 'n_nodes', '>=': 80},
        {'check': 'n_spikes', '>=': 1700},
        {'check': 'mean_spikes_per_node', 'between': [15.0, 25.0]},
        {'check': 'min_timestamp', '>=': 0.0},
        {'check': 'max_timestamp', '<=': 2001.0},
        {'check': 'mean_firing_rate', 'between': [8.0, 12.0]},
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', nargs='?', type=str, default='config.simulation.json')
    parser.add_argument('--save-to', nargs='?', type=str, default=None)
    parser.add_argument('--hide-results', action='store_true')
    args, unknown = parser.parse_known_args()

    config = ConfigJSON(args.config_file)
    results = check_spikes(config.get_spikes_file(ext='csv'))
    results += check_spikes(config.get_spikes_file(ext='h5'))

    if args.save_to:
        results.save_to(args.save_to)
    
    if not args.hide_results:
        results.display()
    
    sys.exit(get_return_code(results))
