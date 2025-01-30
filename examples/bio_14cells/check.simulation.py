import sys
from pathlib import Path
import argparse

from bmtk.utils.integration_tester import get_return_code
from bmtk.utils.integration_tester import ReportFile, SpikesFile, ECPFile, ConfigJSON



def check_membrane_report(file_path):
    vm_report = ReportFile(file_path)
    return vm_report['v1'].run_checks([
        {'check': 'is_valid_sonata', 'expected': True},
        {'check': 'is_valid_report', 'expected': True},
        {'check': 'n_nodes', 'expected': 10},
        {'check': 'n_elements', 'expected': 10},
    ])


def check_spikes(file_path):
    spikes_report = SpikesFile(file_path)
    return spikes_report['v1'].run_checks([
        {'check': 'n_spikes', '>': 100},
        {'check': 'n_nodes', '==': 14}
    ])


def check_syn_report(file_path):
    syn_report = ReportFile(file_path)
    return syn_report['v1'].run_checks([
        {'check': 'is_valid_sonata', 'expected': True},
        {'check': 'is_valid_report', 'expected': True},
        {'check': 'n_nodes', 'expected': 4},
        {'check': 'n_elements', 'expected': 3280},
        {'check': 'is_empty', 'expected': False},
    ])


def check_calcium_report(file_path):
    cai_report = ReportFile(file_path)
    return cai_report['v1'].run_checks([
        {'check': 'is_valid_sonata', 'expected': True},
        {'check': 'is_valid_report', 'expected': True},
        {'check': 'n_nodes', 'expected': 10},
        {'check': 'n_elements', 'expected': 10},
        {'check': 'is_empty', 'expected': False},
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', nargs='?', type=str, default='config.simulation.json')
    # parser.add_argument('--uuid', nargs='?', type=str, default='')
    parser.add_argument('--save-to', nargs='?', type=str, default=None)
    
    args, unknown = parser.parse_known_args()

    config = ConfigJSON(args.config_file)
    results = check_membrane_report(config.get_report_file('membrane_potential'))
    results += check_spikes(config.get_spikes_file(ext='csv'))
    results += check_spikes(config.get_spikes_file(ext='h5'))
    # results += check_ecp(config.get_report_file('ecp'))
    results += check_syn_report(config.get_report_file('syn_report'))
    results += check_calcium_report(config.get_report_file('calcium_concentration'))
    results.save_to(args.save_to)
    sys.exit(get_return_code(results))