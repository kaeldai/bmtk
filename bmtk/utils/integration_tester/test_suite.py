import os
import sys
import subprocess
import json
import re
import copy
import glob
import uuid
import logging
from datetime import datetime
from pprint import pprint
from pathlib import Path


logger = logging.getLogger(__name__)


class TestCase(object):
    def __init__(self, name, run_cmd=None, run_opts=None, check_cmd=None, check_opts=None, 
                 setup_cmd=None, setup_opts=None, env_vars=None, working_dir='.', keywords=[], enabled=True):
        self.name = name
        self.working_dir = working_dir
        self.enabled = enabled
        self.keywords = keywords
        self.env_vars = env_vars

        self.cmds = {
            'run': {
                'cmd': run_cmd,
                'opts': run_opts,
                'available': run_cmd is not None and len(run_cmd) > 0
            },
            'check': {
                'cmd': check_cmd,
                'opts': check_opts,
                'available': check_cmd is not None and len(check_cmd) > 0
            },
            'setup': {
                'cmd': setup_cmd,
                'opts': setup_opts,
                'available': setup_cmd is not None and len(setup_cmd) > 0
            }
            # TODO: Need to add 'cleanup' command types
        }

    def can_execute(self, cmd_type):
        return self.cmds[cmd_type]['available']
    
    def get_command(self, cmd_type, aslist=True):
        can_exec = self.cmds[cmd_type]['available']
        cmd = self.cmds[cmd_type]['cmd']
        opts = self.cmds[cmd_type]['opts']

        if not can_exec or not cmd:
            return [] if aslist else ''
        
        if not isinstance(cmd, list):
            cmd = cmd.split()

        if opts:
            if not isinstance(opts, list):
                opts = opts.split()
            
            cmd.extend(opts)

        return cmd if aslist else ' '.join(cmd)

    @classmethod
    def build(cls, json_path, env_variables, **kwargs):       
        test_name = kwargs['name']
        env_variables = env_variables.push({'test-name': test_name})

        test_wd = kwargs.get('working-dir', None)
        test_wd = env_variables.resolve(test_wd)
        if test_wd is None:
            test_wd = json_path.parent.resolve()

        test_cmd = kwargs.get('run-cmd', None)
        test_cmd = env_variables.resolve(test_cmd)
        test_opts = kwargs.get('run-opts', [])
        test_opts = env_variables.resolve(test_opts)
        if not isinstance(test_opts, (list, tuple)):
            test_opts = [test_opts]

        check_cmd = kwargs.get('check-cmd', None)
        check_cmd = env_variables.resolve(check_cmd)
        check_opts = kwargs.get('check-opts', [])
        check_opts = env_variables.resolve(check_opts)
        if not isinstance(check_opts, list):
            check_opts = [check_opts]

        setup_cmd = kwargs.get('setup-cmd', None)
        setup_cmd = env_variables.resolve(setup_cmd)
        setup_opts = kwargs.get('setup-opts', [])
        setup_opts = env_variables.resolve(setup_opts)
        if not isinstance(setup_opts, list):
            setup_opts = [setup_opts]

        test_enabled = kwargs.get('enabled', True) or env_variables.get('force', False)
        return cls(
            name=test_name, 
            run_cmd=test_cmd, 
            run_opts=test_opts, 
            working_dir=test_wd,
            enabled=test_enabled,
            check_cmd=check_cmd,
            check_opts=check_opts,
            setup_cmd=setup_cmd,
            setup_opts=setup_opts,
            env_vars=env_variables,
            keywords=kwargs.get('keywords', [])
        )
    
    def __repr__(self):
        return self.name


def filter_test_by_name(test_dict, filters):
    if filters is None or len(filters) == 0:
        return True
    elif 'name' not in test_dict:
        return False
    else:
        test_name = test_dict['name']
        for filter in filters:
            if test_name == filter:
                return True
            elif filter in test_name:
                return True
        return False


def filter_test_by_keywords(test_dict, filters):
    if filters is None or len(filters) == 0:
        return True
    elif 'keywords' not in test_dict:
        return False
    else:        
        passed = [f in test_dict['keywords'] for f in filters]
        return all(passed)


def parse_json(json_path, name_filters=[], keyword_filters=[], env_vars=None,
               default_json_fname='integration_tests.json'):
    json_path_full = Path(json_path).resolve()
    if json_path_full.is_dir():
        json_path_full = json_path_full / default_json_fname
    
    if not json_path_full.is_file():
        raise FileExistsError(f'Could not find integration tests file "{json_path_full}"')

    collected_tests = []
    try:
        contents = json.load(open(json_path_full, 'r'))
    except json.decoder.JSONDecodeError as e:
        logger.critical(f'Unable to load {json_path_full}: {e}')
        exit(1)
    
    # This will add all the environment variables ${varname}s into EnvVariable object based on current json file. The
    # environmental variables are scoped so will only work on current json file commands as-well-as the one's this 
    # is imported. Will be lost when returning from current scope
    env_vars = env_vars.push(
        contents, 
        {'json-dir': Path(json_path_full).parent.as_posix()}
    )
    
    for sec_name, sec_vals in contents.items():
        if sec_name.lower() in ['import', 'imports']:
            # Recursively import tests from anther file/directory, each item in the list is a different
            # import and can either be a file (pointnet_tests/integration_tests.json), a directory 
            # (poinnet_test/) or an expresssion (**/integration_tests.json)
            import_file = [sec_vals] if isinstance(sec_vals, str) else sec_vals
            for sub_path_exp in import_file:
                for sub_path in glob.glob(sub_path_exp):
                    sub_tests = parse_json(
                        sub_path, 
                        name_filters=name_filters, 
                        keyword_filters=keyword_filters,
                        default_json_fname=default_json_fname,
                        env_vars=env_vars
                    )
                    collected_tests.extend(sub_tests)
            
        elif sec_name.lower() in ['tests']:
            sec_vals = [sec_vals] if isinstance(sec_vals, dict) else sec_vals
            for test_sec in sec_vals:
                # if not test_sec.get('enabled', True):
                #     continue

                if not filter_test_by_name(test_sec, name_filters):
                    continue

                if not filter_test_by_keywords(test_sec, keyword_filters):
                    continue
                
                test = TestCase.build(
                    json_path=json_path_full, 
                    env_variables=env_vars, 
                    **test_sec
                )
                collected_tests.append(test)

    return collected_tests


def display_results(test_cases, cmd, env_vars):
    if cmd == 'check' and os.path.exists(env_vars['results-output']):
        import pandas as pd
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.max_rows', None)
        
        results_df = pd.read_csv(env_vars['results-output'], sep=' ')
        name_max_len = results_df['caller'].str.len().max() + 3

        n_tests_recorded = results_df['caller'].nunique()
        logger.info(f'COLLATING RESULTS (from {n_tests_recorded} recorded test-cases)')
        logger.info('-----------------')
        max_checks = results_df['caller'].value_counts().max()
        ratio_str_max = len(f'{max_checks}/{max_checks}')
        
        for test_name, test_results_df in results_df.groupby('caller'):
            if len(test_results_df) == 0:
                continue

            name_len = len(test_name)
            dots_str = ''.join(['.']*(name_max_len - name_len))
            name_formated = f'{test_name}{dots_str}'
            
            failed_df = test_results_df[test_results_df['test-passed'] == False]
            n_tests = len(test_results_df)
            n_failed = len(failed_df)
            n_passed = n_tests - n_failed
            check_char = '\u2717' if n_failed > 0 else '\u2713'
            ratio_str =  f'{n_passed}/{n_tests}'
            ratio_padding = ' '*(ratio_str_max - len(ratio_str))
            logger.info(f'{name_formated} {ratio_padding}{ratio_str} passed: {check_char}')
            if n_failed > 0:
                for _, row in failed_df.iterrows():
                    logger.info(f'  [FAILED] {row["reporter"]}::{row["test-name"]}() [expected: \"{row["expected-value"]}\"; actual: {row["actual-value"]}]')


class TestSuite:
    def __init__(self, **suite_opts):
        self._no_run = suite_opts.get('no_run', False)
        self._quiet_tests = suite_opts.get('quiet_tests', False)
        self.stdout_opts = subprocess.DEVNULL if self._quiet_tests else None
        
        self._selected_test_cases = []

    @property
    def no_run(self):
        return self._no_run
    
    @property
    def ran_tests(self):
        return self._selected_test_cases
    
    @property
    def n_tests(self):
        return len(self._selected_test_cases)
    
    def execute_tests(self, test_cases, cmd_type='run'):
        ran_tests = {'test_name': [], 'test_results': []}
        self._selected_test_cases = [test for test in test_cases if test.enabled and test.can_execute(cmd_type)]
        n_tests = len(self._selected_test_cases)
        for test_num, test_case in enumerate(self._selected_test_cases):
            cmd = test_case.get_command(cmd_type, aslist=True)
            current_dir = os.getcwd()
            try:
                logger.info(self.__get_test_msg(test_num, test_case, cmd_type))
                logger.debug(f'  command: {cmd}')
                os.chdir(test_case.working_dir)
                if self.no_run:
                    # For --no-run debugging option do not actually call the subprocess.
                    process = '<NA>'
                else:
                    process = subprocess.call(cmd, stdout=self.stdout_opts)
                    ran_tests['test_name'].append(test_case.name)
                    ran_tests['test_results'].append(process)
               
                logger.info(f'{self.__get_test_msg(test_num, test_case, cmd_type)} completed with return code {process}.')
                
            finally:
                os.chdir(current_dir)

        n_tests_ran = len(ran_tests['test_name'])
        n_tests_passed = sum([1 for r in ran_tests['test_results'] if r == 0])
        n_tests_failed = sum([1 for r in ran_tests['test_results'] if r == 1])
        n_tests_other = sum([1 for r in ran_tests['test_results'] if r not in [0, 1]])
            
        if n_tests_ran == 0:
            logger.info(f'Could not execute "{cmd_type}" command. No tests found!')
        else:
            logger.info(f'Ran {n_tests_ran} tests ({n_tests_passed} passed, {n_tests_failed} failed, {n_tests_other} other)!')
            if n_tests_failed:
                failed_tests = ', '.join([name for name, results in zip(ran_tests['test_name'], ran_tests['test_results']) if results == 1])
                logger.info(f'Failed tests: {failed_tests}')

    def __get_test_msg(self, test_num, test_case, cmd_type):
        max_msg_len = max([len(t.name) for t in self._selected_test_cases]) + 3
        cur_msg_len = len(test_case.name)
        trailing_dots = '.'*(max_msg_len - cur_msg_len)

        max_num_len = len(f'{self.n_tests}/{self.n_tests}')
        cur_num_len = len(f'{test_num+1}/{self.n_tests}')
        padding = ' '*(max_num_len-cur_num_len)

        return f'({padding}{test_num+1}/{self.n_tests}) Executing {cmd_type} for "{test_case.name}"{trailing_dots}'
    
    def display_tests(self, test_cases, show_by):
        if show_by == 'names':
            for test_case in test_cases:
                print(test_case.name)
        
        elif show_by == 'keywords':
            keywords = set()
            for test_case in test_cases:
                keywords |= set(test_case.keywords)

            keywords = list(keywords)
            keywords.sort()
            for kw in keywords:
                print(kw)
        
        elif show_by == 'keyword-counts':
            kw_counts = {}
            kw_tests = {}
            for test_case in test_cases:
                for keyword in set(test_case.keywords):
                    kw_counts[keyword] = kw_counts.get(keyword, 0) + 1
                    if keyword not in kw_tests:
                        kw_tests[keyword] = []
                    kw_tests[keyword].append(test_case.name)

            ordered_kws = sorted(list(kw_counts.keys()))
            padding = max([len(kw) for kw in ordered_kws])
            for kw in ordered_kws:
                print(f'{kw: >{padding}}: {kw_counts[kw]} ({", ".join(kw_tests[kw])})')


class EnvVariables:
    var_pattern = r'\$\{[A-Za-z_\-]*\}|\$[A-Za-z_\-]*'
    
    def __init__(self) -> None:
        self._env_vars = {}    

    @property
    def variables(self):
        return self._env_vars

    @variables.setter
    def env_vars(self, new_dict):
        self._env_vars = new_dict 

    def push(self, *var_dicts):
        updated_dict = copy.deepcopy(self.env_vars)
        for var_dict in var_dicts:
            if 'env-variables' in var_dict:
                var_dict = var_dict['env-variables']

            updated_evs = EnvVariables()
            updated_dict.update(var_dict)
        
        updated_evs.env_vars = EnvVariables.resolve_dict(updated_dict)
        return updated_evs

    @staticmethod
    def resolve_dict(env_dict):
        completed_env_vars = {}
        prev_env_dict = copy.deepcopy(env_dict)
        updated_env_dict = copy.deepcopy(prev_env_dict)
        n_vars_prev = len(prev_env_dict)+1
        n_vars_curr = len(prev_env_dict)
        while prev_env_dict and n_vars_curr < n_vars_prev:
            for var_name, var_val in prev_env_dict.items():
                if isinstance(var_val, str):
                    subvars = re.findall(EnvVariables.var_pattern, var_val)
                    if len(subvars) == 0:
                        completed_env_vars[var_name] = var_val
                        del updated_env_dict[var_name]
                    else:
                        var_val_parsed = copy.copy(var_val)
                        for subvar_name in subvars:
                            tmp_str = subvar_name.replace('$', '').replace('{', '').replace('}', '')
                            if tmp_str in completed_env_vars:
                                var_val_parsed = var_val_parsed.replace(subvar_name, str(completed_env_vars[tmp_str]))

                        updated_env_dict[var_name] = var_val_parsed
                else:
                    completed_env_vars[var_name] = var_val
                    del updated_env_dict[var_name]

            n_vars_prev = n_vars_curr
            n_vars_curr = len(updated_env_dict)
            prev_env_dict = copy.deepcopy(updated_env_dict)

        if prev_env_dict:
            for k, v in prev_env_dict.items():
                logger.warn(f'environmental variable "{k}" could not be resolved.')
                completed_env_vars[k] = v

        return completed_env_vars

    def resolve(self, expression):
        if expression is None or len(expression) == 0:
            return expression

        elif isinstance(expression, str):
            ret_str = expression
            for subvar in re.findall(EnvVariables.var_pattern, expression):
                subvar_val = self[subvar]
                ret_str = ret_str.replace(subvar, subvar_val)
            return ret_str

        elif isinstance(expression, (list, tuple)):
            return [self.resolve(e) for e in expression]
        
        elif isinstance(expression, dict):
            return {k: self.resolve(v) for k, v in expression.items}

    def __getitem__(self, variable):
        var_key = variable.replace('$', '').replace('{', '').replace('}', '')
        if var_key in self.env_vars:
            return self.env_vars[var_key]
        else:
            raise KeyError(f'Variable "var_key" could not be found or resolved.')

    def get(self, variable, default=None):
        try:
            return self[variable]
        except KeyError as ke:
            return default

    def __repr__(self) -> str:
        rep_str = 'EnvVariable:'
        if not self.variables:
            rep_str += '\n   <no environmental variables set>'
        else:
            ordered_vars = sorted(list(self._env_vars.keys()))
            padding = max([len(v) for v in ordered_vars])
            for v in ordered_vars:
                rep_str += '\n' + f'   {v: >{padding}} = {self._env_vars[v]}'

        return rep_str

    @classmethod
    def generate_from_args(cls, args):
        if args is None or len(vars(args)) == 0:
            cls()

        env_vars = {}
        if args.no_uuid:
            env_vars['uuid'] = ''
        elif args.uuid is not None and len(args.uuid) > 0:
            env_vars['uuid'] = args.uuid
        else:
            env_vars['uuid'] = str(uuid.uuid4().hex)
 
        env_vars['force'] = args.force
        
        env_vars['date'] = datetime.today().strftime("%Y%m%d")

        env_vars['python'] = sys.executable

        env_vars['ncores'] = args.ncores
        env_vars['memory'] = args.memory
        
        use_mpirun = args.use_mpi or args.ncores > 1 and not args.use_slurm
        use_conda = args.run_with_conda and args.env_name is not None
        if args.use_slurm:
            slurm_opts = f'--task {args.ncores} ' if args.ncores else ' '
            slurm_opts += f'--memory {args.memory}' if args.memory else ' '
            slurm_opts += f'--conda-env {args.env_name}' if args.env_name else ' '
            slurm_opts += f'--job-name {args.slurm_job_name}' if args.slurm_job_name else ' '
            slurm_opts = slurm_opts.strip()
            env_vars['exec-bmtk'] = f'slurm_bmtk.sh {slurm_opts}'
            env_vars['exec-bionet'] = f'slurm_bionet.sh {slurm_opts}'
            env_vars['exec-filternet'] = f'slurm_bmtk.sh {slurm_opts}'
            env_vars['exec-pointnet'] = f'slurm_pointnet.sh {slurm_opts}'
        elif use_mpirun:
            env_vars['exec-bmtk'] = f'mpirun -np {args.ncores} {env_vars["python"]}'
            env_vars['exec-bionet'] = f'mpirun -np {args.ncores} nrniv -mpi -python'
            env_vars['exec-filternet'] = f'mpirun -np {args.ncores} {env_vars["python"]}'
            env_vars['exec-pointnet'] = f'mpirun -np {args.ncores} {env_vars["python"]}'
        else:
            env_vars['exec-bmtk'] = env_vars['python'] # 'python'
            env_vars['exec-bionet'] = 'nrniv -python' if args.use_nrniv else env_vars['python'] # 'python' 
            env_vars['exec-filternet'] = env_vars['python'] # 'python'
            env_vars['exec-pointnet'] = env_vars['python'] # 'python'

        if args.save_results:
            env_vars['results-output'] = args.save_results
        elif args.command[0] in ['check']:
            env_vars['results-output'] = (Path.cwd() / Path(f'.results.integration_tests.examples.csv')).as_posix()
        else:
            env_vars['results-output'] = ''

        env_vars['append-saves'] = args.append_saves
        if env_vars['results-output'] and not env_vars['append-saves'] and Path(env_vars['results-output']).exists():
            os.remove(env_vars['results-output'])

        ev = cls()
        ev.env_vars = env_vars
        return ev
