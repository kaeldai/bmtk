import sys
import argparse
import logging
from pathlib import Path

from .test_suite import EnvVariables, TestSuite, parse_json, display_results

logger = logging.getLogger()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs=1, type=str, choices=['run', 'check', 'clean', 'setup', 'list'])
    parser.add_argument('test_names', nargs='*', type=str)
    parser.add_argument('--tests-file', nargs='?', type=str, default='integration_tests.json')
    
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('-n', '--no-run', action='store_true')
    parser.add_argument('-q', '--quiet-tests', action='store_true')
    
    parser.add_argument('--use-nrniv', action='store_true')
    parser.add_argument('--use-mpi', action='store_true')
    parser.add_argument('--ncores', nargs='?', type=int, default=1)
    parser.add_argument('-m', '--memory', nargs='?', type=str, default=None)
    parser.add_argument('--env-name', nargs='?', type=str, default=None)
    parser.add_argument('--run-with-conda', action='store_true')


    parser.add_argument('--uuid', nargs='?', type=str, default='')
    parser.add_argument('--no-uuid', action='store_true')
    parser.add_argument('--use-slurm', action='store_true', default=False)
    parser.add_argument('--slurm-job-name', nargs='?', type=str, default=None)
    parser.add_argument('--filter-keyword', action='append', type=str)

    parser.add_argument('--save-results', nargs='?', type=str, default=None)
    parser.add_argument('--append-saves', action='store_true')
    parser.add_argument('-f', '--force', action='store_true')
    
    args = parser.parse_args()
   
    logger.setLevel(logging.INFO if not args.debug else logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s: %(message)s"))
    logger.addHandler(console_handler)

    tests_file = Path(args.tests_file)
    if not tests_file.exists() or not tests_file.is_file():
        raise ValueError(f'Could not find valid json file {tests_file}. See -h option for proper usage.')       

    env_vars = EnvVariables.generate_from_args(args)

    json_path = tests_file.resolve()
    test_cases = parse_json(
        json_path=Path(args.tests_file), 
        name_filters=args.test_names if args.command[0] != 'list' else None, 
        keyword_filters=args.filter_keyword,
        env_vars=env_vars,
    )

    ts = TestSuite(no_run=args.no_run, quiet_tests=args.quiet_tests)

    if args.command[0] == 'list':
        show_opt = 'names' if len(args.test_names) == 0 else args.test_names[0]
        ts.display_tests(test_cases=test_cases, show_by=show_opt)
    else:
        ts.execute_tests(test_cases=test_cases, cmd_type=args.command[0])
        display_results(ts, args.command[0], env_vars)
        # if args.command[0] == 'check' and env_vars['']
