import sys
from pathlib import Path
import argparse

from bmtk.utils.integration_tester import get_return_code
from bmtk.utils.integration_tester import ReportFile, SpikesFile, ConfigJSON


def check_spikes(file_path):
    spikes_report = SpikesFile(file_path)
    return spikes_report['biocell'].run_checks([
        {'check': 'n_nodes', 'expected': 1},
        {'check': 'n_spikes', '>=': 20},
    ])


def check_membrane_potential(file_path):
    vm_report = ReportFile(file_path)
    return vm_report['biocell'].run_checks([
        {'check': 'is_valid_sonata', 'expected': True},
        {'check': 'is_valid_report', 'expected': True},
        {'check': 'n_nodes', 'expected': 1},
        {'check': 'n_elements', 'expected': 1},
        {'check': 'n_active_cells', 'expected': 1},
        {'check': 'n_inactive_cells', 'expected': 0},
        {'check': 'is_empty', 'expected': False},
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', nargs='?', type=str, default='config.simulation_iclamp.json')
    parser.add_argument('--save-to', nargs='?', type=str, default=None)
    parser.add_argument('--hide-results', action='store_true')
    args, unknown = parser.parse_known_args()


    config = ConfigJSON(args.config_file)
    results = check_spikes(config.get_spikes_file(ext='csv'))
    results += check_spikes(config.get_spikes_file(ext='h5'))
    results += check_membrane_potential(config.get_report_file('membrane_potential'))
    
    if args.save_to:
        results.save_to(args.save_to)
    
    if not args.hide_results:
        results.display()
    
    sys.exit(get_return_code(results))