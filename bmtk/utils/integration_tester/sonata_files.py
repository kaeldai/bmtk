import os
import copy
import json
import re
from pathlib import Path
import inspect

import numpy as np
import h5py
import pandas as pd
import __main__

from .recorder_utils import RunChecksReport

class RunCheckTrait:
    def run_checks(self, tests, reporter=None, caller=None):
        if reporter is None:
            try:
                reporter = inspect.stack()[1].function
            except Exception as e:
                reporter = None
        
        if caller is None:
            try:
                py_path = Path(inspect.stack()[1].filename)
                caller = f'{py_path.parent.name}/{py_path.name}'
            except Exception as e:
                caller = None

        test_results = RunChecksReport(reporter, caller)
        for test_dict in tests:
            test_dict = copy.copy(test_dict)
            check_fn_name = test_dict.pop('check')
            check_fn = getattr(self, check_fn_name)
            args = test_dict.get('args', [])
            kwargs = test_dict.get('kwargs', {})
            try:
                actual_val = check_fn(*args, **kwargs)
            except (AttributeError, Exception) as e:
                actual_val = '<NA>'

            # if actual_val == '<NA>':
            #     passed = False
            # elif isinstance(expected_val,(np.ndarray, tuple, list)):
            #     passed = np.allclose(expected_val, actual_val, rtol=1.0e-03)
            # elif isinstance(expected_val, str):
            #     passed = expected_val == actual_val
            # elif np.isscalar(expected_val):
            #     passed = np.isclose(expected_val, actual_val, rtol=1.0e-03)
            # elif isinstance(expected_val, bool):
            #     passed = expected_val == actual_val
            # else:
            #     raise ValueError(f'Cant do comparisions on {type(expected_val)}')

            if '==' in test_dict:
                test_dict['expected'] = test_dict.pop('==')

            if 'expected' in test_dict:
                expected_val = test_dict.pop('expected')
                passed = self.check_value_equals(expected_val, actual_val)
                expected_val = f'actual == {expected_val}'
            elif 'between' in test_dict:
                expected_val = test_dict.pop('between')
                passed = self.check_value_between(expected_range=expected_val, actual_val=actual_val)
                expected_val = f'{expected_val[0]} <= actual <= {expected_val[0]}'
            elif '<' in test_dict:
                expected_val = test_dict.pop('<')
                passed = self.check_lt(expected_val=expected_val, actual_val=actual_val)
            elif '<=' in test_dict:
                expected_val = test_dict.pop('<=')
                passed = self.check_lt(expected_val=expected_val, actual_val=actual_val)
            elif '>' in test_dict:
                expected_val = test_dict.pop('>')
                passed = self.check_gt(expected_val=expected_val, actual_val=actual_val)
            elif '>=' in test_dict:
                expected_val = test_dict.pop('>=')
                passed = self.check_gteq(expected_val=expected_val, actual_val=actual_val)
            else:
                raise RuntimeError('No operator to compare results againsts (opts: expected, between, <=, >=)')

            test_results.append(
                check_fn_name=check_fn_name,
                expected_val=expected_val,
                actual_val=actual_val,
                passed=passed,
                # reporter=reporter,
                # calling_script=calling_script
            )
            # test_results.append(passed)

            # if return_report:
            #     report['check_function'].append(check_fn_name)
            #     report['expected'].append(expected_val)
            #     report['actual'].append(actual_val)

        # if return_report:
        #     return test_results, pd.DataFrame(report)
        return test_results
    
    def check_value_equals(self, expected_val, actual_val):
            if actual_val == '<NA>':
                passed = False
            elif isinstance(expected_val,(np.ndarray, tuple, list)):
                passed = np.allclose(expected_val, actual_val, rtol=1.0e-03)
            elif isinstance(expected_val, str):
                passed = expected_val == actual_val
            elif np.isscalar(expected_val):
                passed = np.isclose(expected_val, actual_val, rtol=1.0e-03)
            elif isinstance(expected_val, bool):
                passed = expected_val == actual_val
            else:
                raise ValueError(f'Cant do comparisions on {type(expected_val)}')
            
            return passed

    def check_value_between(self, expected_range, actual_val):
        if len(expected_range) != 2:
            raise ValueError(f'between operator must be an list, tuple, or array of size two [min, max]')
        
        return expected_range[0] <= actual_val <= expected_range[1]

    def check_lt(self, expected_val, actual_val):
        return actual_val < expected_val 
    
    def check_lteq(self, expected_val, actual_val):
        return actual_val <= expected_val

    def check_gt(self, expected_val, actual_val):
        return actual_val > expected_val

    def check_gteq(self, expected_val, actual_val):
        return actual_val >= expected_val


class CheckSONATATrait:
    MAGIC_ATTR = 'magic'
    MAGIC_VAL = 0x0A7A

    def check_magic(self, hdf5_file):
        """Check the magic attribute exists according to the sonata format"""
        hdf5_obj = self._load_h5(hdf5_file)
        if CheckSONATATrait.MAGIC_ATTR not in hdf5_obj.attrs:
            return False
            # raise Exception('File {} missing top-level \"{}\" attribute.'.format(hdf5_obj.filename, CheckSONATATrait.MAGIC_ATTR))
        elif np.uint32(self._get_attribute_h5(hdf5_obj, CheckSONATATrait.MAGIC_ATTR)) != CheckSONATATrait.MAGIC_VAL:
            # raise Exception('File {} has unexpected magic value (expected {})'.format(hdf5_obj.filename, CheckSONATATrait.MAGIC_VAL))
            return False

        return True 

    def _get_attribute_h5(self, h5obj, attribut_name, default=None):
        val = h5obj.attrs.get(attribut_name, default)
        if isinstance(val, bytes):
            # There is an but with h5py returning unicode/str based attributes as bytes
            val = val.decode()

        return val
    
    def _load_h5(self, h5file, mode='r'):
        # TODO: Allow for h5py.Group also
        if isinstance(h5file, h5py.File):
            return h5file

        return h5py.File(h5file, mode)
    
class ReportFile(CheckSONATATrait, RunCheckTrait):
    def __init__(self, report_path):
        self._report_path = report_path
        self._default_population = None
        self._pop_cache = {}
        try:
            self._report_h5 = h5py.File(report_path)
            self._valid_sonata = None
            self._valid_report = None
        except FileNotFoundError as fnfe:
            self._valid_sonata = False
            self._valid_report = False
            
    @property
    def valid_sonata(self):
        if self._valid_sonata is None:
            self._valid_sonata = self.check_magic(self._report_h5)

        return self._valid_sonata
    
    @valid_sonata.setter
    def valid_sonata(self, flag):
        self._valid_sonata = flag

    def is_valid_sonata(self):
        return self.valid_sonata

    @property
    def default_population(self):
        if self._default_population is None:
            default_pop = None
            for pop_name, h5_type in self._report_h5['report'].items():
                if isinstance(h5_type, h5py.Group):
                    if default_pop is not None:
                        raise ValueError('Report contains multiple populations, can not determine default.')
                    else:
                        default_pop = pop_name
            self._default_population = default_pop
        
        return self._default_population
    
    @default_population.setter
    def default_population(self, pop_name):
        self._default_population = pop_name

    def is_valid_report(self, population=None):
        population = population or self.default_population
        if self._valid_report is None:
            report_grp = self._report_h5['report'][population]
            
            data_ds = report_grp['data']
            mapping_grp = report_grp['mapping']
            time_ds = mapping_grp['time'][()]
            n_nodes = len(mapping_grp['node_ids'])
            n_elements = mapping_grp['index_pointer'][-1]           
            n_timesteps = len(np.arange(time_ds[0], time_ds[1], step=time_ds[2]) if len(time_ds) == 3 else len(time_ds))
            
            flag =  len(mapping_grp['index_pointer']) == n_nodes+1
            flag &= len(mapping_grp['element_pos']) == n_elements
            flag &= len(mapping_grp['element_ids']) == n_elements
            flag &= len(mapping_grp['index_pointer']) == n_nodes+1
            flag &= data_ds.shape[0] == n_timesteps
            flag &= data_ds.shape[1] == n_elements
            self._valid_report = flag

        return self._valid_report

    def recorded_node_ids(self, population=None):
        population = population or self.default_population
        return self._report_h5['report'][population]['mapping']['node_ids']
    
    def n_nodes(self, population=None):
        population = population or self.default_population
        return len(self.recorded_node_ids(population))

    def recorded_element_ids(self, population=None):
        population = population or self.default_population
        return self._report_h5['report'][population]['mapping']['element_ids']
    
    def n_elements(self, population=None):
        population = population or self.default_population
        return len(self.recorded_element_ids(population))

    def mean_trace(self, population=None):
        population = population or self.default_population
        data = self._report_h5['report'][population]['data'][()]
        return np.mean(data, axis=1)
    
    def mean_value(self, population=None):
        population = population or self.default_population
        return np.mean(self._report_h5['report'][population]['data'][()])
    
    def max_value(self, population=None):
        population = population or self.default_population
        return np.max(self._report_h5['report'][population]['data'])
    
    def min_value(self, population=None):
        population = population or self.default_population
        return np.min(self._report_h5['report'][population]['data'])

    def get_active_cells(self, threshold=0.0, population=None):
        population = population or self.default_population
        filtered_node_ids = []
        for node_ids_idx, node_id in enumerate(self._report_h5['report'][population]['mapping']['node_ids']):
            idx_beg = self._report_h5['report'][population]['mapping']['index_pointer'][node_ids_idx]
            idx_end = self._report_h5['report'][population]['mapping']['index_pointer'][node_ids_idx+1]
            max_value = self._report_h5['report'][population]['data'][:, idx_beg:idx_end].max()
            if max_value >= threshold:
                filtered_node_ids.append(node_id)
        return filtered_node_ids
    
    def n_active_cells(self, threshold=0.0, population=None):
        return len(self.get_active_cells(threshold=threshold, population=population))

    def get_inactive_cells(self, threshold=0.0, population=None):
        population = population or self.default_population
        filtered_node_ids = []
        for node_ids_idx, node_id in enumerate(self._report_h5['report'][population]['mapping']['node_ids']):
            idx_beg = self._report_h5['report'][population]['mapping']['index_pointer'][node_ids_idx]
            idx_end = self._report_h5['report'][population]['mapping']['index_pointer'][node_ids_idx+1]
            max_value = self._report_h5['report'][population]['data'][:, idx_beg:idx_end].max()
            if max_value < threshold:
                filtered_node_ids.append(node_id)
        return filtered_node_ids

    def n_inactive_cells(self, threshold=0.0, population=None):
        return len(self.get_inactive_cells(threshold=threshold, population=population))

    def is_empty(self, population=None):
        population = population or self.default_population
        data_ds = self._report_h5['report'][population]['data']
        for row in range(data_ds.shape[0]):
            if np.any(data_ds[row, :]):
                return False

        return True

    def __getitem__(self, population_name):
        report = ReportFile(self._report_path)
        report.valid_sonata = self.valid_sonata
        report.default_population = population_name
        return report

class SpikesFile(RunCheckTrait):
    def __init__(self, file_path):
        self._file_path = file_path
        self._spikes_obj = None
        self._is_hdf5 = False
        self._is_csv = False
        self._pop_cache = {}
        self._spikes_df = None

        try:
            self._spikes_obj = pd.read_csv(file_path, sep=' ')
            self._is_csv = True           
        except Exception as e:
            pass

        if self._spikes_obj is None:
            try:
                self._spikes_obj = h5py.File(file_path, 'r')
                self._is_hdf5 = True
            except Exception as e:
                pass

    @property
    def spikes_df(self):
        return self._spikes_df
    
    @spikes_df.setter
    def spikes_df(self, spikes_df):
        self._spikes_df = spikes_df

    def _get_dataframe(self, population_name):
        if self._is_hdf5:
            pop_grp = self._spikes_obj['spikes'][population_name]
            return pd.DataFrame({
                'timestamps': pop_grp['timestamps'],
                'population': population_name,
                'node_ids': pop_grp['node_ids']
            })
        elif self._is_csv:
            return self._spikes_obj[self._spikes_obj['population'] == population_name]
        else:
            raise Exception('File in not an hdf5 or csv')        

    def node_ids(self, population_name=None):
        spikes_df = self.spikes_df if self._spikes_df is not None else self._get_dataframe(population_name)
        return spikes_df['node_ids'].unique()

    def n_nodes(self, population_name=None):
        return len(self.node_ids(population_name=population_name))

    def n_spikes(self, population_name=None):
        spikes_df = self.spikes_df if self._spikes_df is not None else self._get_dataframe(population_name)
        return len(spikes_df)
    
    def spikes_per_node(self, population_name=None):
        spikes_df = self.spikes_df if self._spikes_df is not None else self._get_dataframe(population_name)
        return spikes_df.groupby('node_ids')['timestamps'].agg('count').reset_index('node_ids').rename(columns={'timestamps': 'n_spikes'})

    def mean_spikes_per_node(self, population_name=None):
        spike_counts = self.spikes_per_node(population_name=population_name)
        return np.mean(spike_counts['n_spikes'].values)

    def min_timestamp(self, population_name=None):
        spikes_df = self.spikes_df if self._spikes_df is not None else self._get_dataframe(population_name)
        return spikes_df['timestamps'].min()
    
    def max_timestamp(self, population_name=None):
        spikes_df = self.spikes_df if self._spikes_df is not None else self._get_dataframe(population_name)
        return spikes_df['timestamps'].max()

    def mean_firing_rate(self, population_name=None, min_time=None, max_time=None):
        max_time = max_time if max_time is not None else self.max_timestamp(population_name=population_name)
        min_time = min_time if min_time is not None else self.min_timestamp(population_name=population_name)
        n_spikes = self.n_spikes()
        time_secs = (max_time - min_time)/1000.0
        return n_spikes / time_secs / self.n_nodes()

    def __getitem__(self, population_name):
        if population_name in self._pop_cache:
            return self._pop_cache[population_name]
        else:
            new_spikes_file = SpikesFile(self._file_path)
            new_spikes_file.spikes_df = self._get_dataframe(population_name=population_name)
            self._pop_cache[population_name] = new_spikes_file
            return new_spikes_file


class ECPFile(RunCheckTrait):
    def __init__(self, file_path):
        self._file_path = file_path
        self._ecp_grp = None

        try:
            self._ecp_h5 = h5py.File(file_path)
            self._valid_ecp_report = None
        except FileNotFoundError as fnfe:
            self._ecp_h5 = None
            self._valid_ecp_report = False
    
    @property
    def ecp_grp(self):
        if self._ecp_grp is None:
            self._ecp_grp = self._ecp_h5['ecp']
        
        return self._ecp_grp

    def is_valid(self):
        if self._valid_ecp_report is None:
            try:
                ecp_grp = self._ecp_h5['ecp']
                time_ds = ecp_grp['time']
                n_channels = len(ecp_grp['channel_id'])
                n_timesteps = len(np.arange(time_ds[0], time_ds[1], step=time_ds[2]))
                self._valid_ecp_report = ecp_grp['data'].shape == (n_timesteps, n_channels)
            except Exception as e:
                self._valid_ecp_report = False

        return self._valid_ecp_report
    
    def n_channels(self):
        return len(self.ecp_grp['channel_id'])
    
    def n_timesteps(self):
        time_ds = self.ecp_grp['time']
        return int(time_ds[1] - time_ds[0])/time_ds[2]
    
    def mean_value(self):
        return np.mean(self.ecp_grp['data'])
    
    def max_value(self):
        return np.max(self.ecp_grp['data'])
    
    def min_value(self):
        return np.min(self.ecp_grp['data'])
    
    def is_empty(self):
        return not np.any(self.ecp_grp['data'])


class ConfigJSON:
    def __init__(self, config_path, **args):
        # print(config_path)
        self._config_path = config_path
        self._variables = {
            'configdir': Path(config_path).parent.resolve().as_posix()
        }

        self._config_dict = json.load(open(config_path, 'r'))
        for arg_name, arg_val in args.items():
            self._add_variable(arg_name, arg_val)

        self.load_manifest(self._config_dict)
        
    def _get_variable(self, name):
        var_name = name.replace('$', '').replace('{', '').replace('}', '')
        return self._variables.get(var_name, None)
    
    def _add_variable(self, name, value):
        var_name = name.replace('$', '').replace('{', '').replace('}', '')
        self._variables[var_name] = value
                        

    def load_manifest(self, config_dict):
        if 'manifest' not in config_dict:
            return
        
        manifest_dict = copy.deepcopy(config_dict['manifest'])
        n_vars_remaining = len(manifest_dict.keys())
        while n_vars_remaining > 0:
            no_vals_resolved = True
            var_names = list(manifest_dict.keys())
            var_vals = list(manifest_dict.values())
            for var_name, var_val in zip(var_names, var_vals):
                subvars = re.findall(r'\$\{[A-Za-z_]*\}|\$[A-Za-z_]*', var_val)
                if len(subvars) == 0:
                    self._add_variable(var_name, var_val)
                    no_vals_resolved = False
                    del manifest_dict[var_name]
                else:
                    for subvar in subvars:
                        subvar_val = self._get_variable(subvar)
                        if subvar_val is not None:
                            manifest_dict[var_name] = manifest_dict[var_name].replace(subvar, subvar_val)
                            no_vals_resolved = False

            if no_vals_resolved:
                raise ValueError(f'unable to resolve manifest {manifest_dict}')
            
            n_vars_remaining = len(manifest_dict.keys())
            
    @property
    def output_dir(self):
        output_dir = self._config_dict['output']['output_dir']
        for subvar in re.findall(r'\$\{[A-Za-z_]*\}|\$[A-Za-z_]*', output_dir):
            subval = self._get_variable(subvar)
            output_dir = output_dir.replace(subvar, subval)
        return Path(output_dir)

    def get_spikes_file(self, ext=None):
        output_dict = self._config_dict['output']
        if ext and ext == 'h5' and 'spikes_file_h5' not in output_dict:
            spikes_file_arg = 'spikes_file'
        elif ext:
            spikes_file_arg = f'spikes_file_{ext}'
        else:
            spikes_file_arg = 'spikes_file'
            
        spikes_file_path = Path(self._config_dict['output'][spikes_file_arg])
        if Path(spikes_file_path).is_absolute():
            return spikes_file_path
        else:
            return self.output_dir / spikes_file_path
        
    def get_report_file(self, report_name):
        report_dict = self._config_dict['reports'][report_name]
        if 'file_name' in report_dict:
            file_path = Path(report_dict['file_name'])
            return file_path if Path(file_path).is_absolute() else self.output_dir / file_path
        else:
            return self.output_dir / Path(f'{report_name}.h5')


class NodesFile(CheckSONATATrait, RunCheckTrait):
    def __init__(self, h5_path, csv_path, default_population=None):
        self._h5_path = h5_path
        self._csv_path = csv_path
        self._default_popualation = default_population
        self._pop_cache = {}
        self._is_valid = None

        # self._nodes_h5 =
        self._nodes_h5_root = None
        self._nodes = None
        self._node_types = None

    @property
    def nodes(self):
        if self._nodes is None:
            self._nodes = self.hdf5_root['nodes'][self._default_popualation]
        
        return self._nodes

    @property
    def hdf5_root(self):
        if self._nodes_h5_root is None:
            self._nodes_h5_root = h5py.File(self._h5_path, 'r')
        
        return self._nodes_h5_root

    @property
    def node_types(self):
        if self._node_types is None:
            self._node_types = pd.read_csv(self._csv_path, sep=' ')
            if 'population' in self._node_types.columns:
                self._node_types = self.node_types[self._node_types['population'] == self._default_popualation]

        return self._node_types

    def is_valid(self):
        flag = self.check_magic(self.hdf5_root)
        flag &= 'node_id' in self.nodes
        flag &= 'node_type_id' in self.nodes and self.nodes['node_type_id'].shape == self.nodes['node_id'].shape
        flag &= 'node_group_id' in self.nodes and self.nodes['node_group_id'].shape == self.nodes['node_id'].shape
        flag &= 'node_group_index' in self.nodes and self.nodes['node_group_index'].shape == self.nodes['node_id'].shape

        # Check groups exists
        group_ids = np.unique(self.nodes['node_group_id'][()])
        flag &= all([str(group_id) in self.nodes for group_id in group_ids])

        # Check node-type properties
        node_type_ids = np.unique(self.nodes['node_type_id'][()])
        flag &= all([ntid in self.node_types['node_type_id'].values for ntid in node_type_ids])

        return flag

    def group_ids(self):
        return np.unique(self.nodes['node_group_id'][()]).astype(str)

    def n_nodes(self):
        return len(self.nodes['node_id'])

    def n_node_types(self):
        return len(np.unique(self.nodes['node_type_id'][()]))

    def n_groups(self):
        return len(self.group_ids())

    def csv_attributes(self, ignore_cols=['node_type_id', 'population']):
        nt_cols = [c for c in self.node_types.columns if c not in ignore_cols]
        return set(nt_cols)

    def hdf5_attributes(self):
        h5_cols = set()
        for group_id in self.group_ids():
            h5_cols |= set(self.nodes[group_id].keys())
        return h5_cols

    def hdf5_attributes_contains(self, attribute_name):
        return attribute_name in self.hdf5_attributes()

    def n_attributes(self):
        return len(self.csv_attributes() | self.hdf5_attributes())

    def __getitem__(self, population_name):
        if population_name in self._pop_cache:
            return self._pop_cache[population_name]
        else:
            nodes_file = NodesFile(
                self._h5_path, self._csv_path, 
                default_population=population_name
            )
            self._pop_cache[population_name] = nodes_file
            return nodes_file


class EdgesFile(CheckSONATATrait, RunCheckTrait):
    def __init__(self, h5_path, csv_path, default_population=None):
        self._h5_path = h5_path
        self._csv_path = csv_path
        self._default_popualation = default_population
        self._pop_cache = {}
        self._is_valid = None

        # self._nodes_h5 =
        self._edges_h5_root = None
        self._edges = None
        self._edge_types = None

    @property
    def hdf5_root(self):
        if self._edges_h5_root is None:
            self._edges_h5_root = h5py.File(self._h5_path, 'r')
        
        return self._edges_h5_root

    @property
    def edges(self):
        if self._edges is None:
            self._edges = self.hdf5_root['edges'][self._default_popualation]
        
        return self._edges

    @property
    def edge_types(self):
        if self._edge_types is None:
            self._edge_types = pd.read_csv(self._csv_path, sep=' ')
            if 'population' in self._edge_types.columns:
                self._edge_types = self._edge_types[self._edge_types['population'] == self._default_popualation]

        return self._edge_types

    def is_valid(self):
        flag = self.check_magic(self.hdf5_root)
        flag &= 'target_node_id' in self.edges
        flag &= 'source_node_id' in self.edges and self.edges['source_node_id'].shape == self.edges['target_node_id'].shape
        flag &= 'edge_type_id' in self.edges and self.edges['edge_type_id'].shape == self.edges['target_node_id'].shape
        flag &= 'edge_group_id' in self.edges and self.edges['edge_group_id'].shape == self.edges['target_node_id'].shape
        flag &= 'edge_group_index' in self.edges and self.edges['edge_group_index'].shape == self.edges['target_node_id'].shape

        # Check groups exists
        group_ids = np.unique(self.edges['edge_group_id'][()])
        flag &= all([str(group_id) in self.edges for group_id in group_ids])

        # Check node-type properties
        edge_type_ids = np.unique(self.edges['edge_type_id'][()])
        flag &= all([etid in self.edge_types['edge_type_id'].values for etid in edge_type_ids])

        return flag
    
    def n_connections(self):
        return len(self.edges['source_node_id'])
    
    def mean_edges_per_pair(self):
        pairs_df = pd.DataFrame({
            'source_node_id': self.edges['source_node_id'],
            'target_node_id': self.edges['target_node_id'],
            'n_edges': 1
        })
        return pairs_df.groupby(['source_node_id', 'target_node_id']).agg('count')['n_edges'].mean()


    def group_ids(self):
        return set(np.unique(self.edges['edge_group_id']).astype(str))
    
    def n_edge_groups(self):
        return len(self.group_ids())
    
    def edge_type_ids(self):
        return set(np.unique(self.edges['edge_type_id']))
    
    def n_edge_type_ids(self):
        return len(self.edge_type_ids())

    def csv_attributes(self, ignore_cols=['edge_type_id', 'population']):
        et_cols = [c for c in self.edge_types.columns if c not in ignore_cols]
        return set(et_cols)

    def csv_attributes_contains(self, attribute_name):
        return attribute_name in self.csv_attributes(ignore_cols=[])

    def hdf5_attributes(self):
        h5_cols = set()
        for group_id in self.group_ids():
            h5_cols |= set(self.edges[group_id].keys())
        return h5_cols

    def hdf5_attributes_contains(self, attribute_name):
        return attribute_name in self.hdf5_attributes()

    def n_attributes(self):
        return len(self.csv_attributes() | self.hdf5_attributes())
    
    def source_node_population(self):
        return str(self.edges['source_node_id'].attrs['node_population'])

    def target_node_population(self):
        return str(self.edges['target_node_id'].attrs['node_population'])


    def __getitem__(self, population_name):
        if population_name in self._pop_cache:
            return self._pop_cache[population_name]
        else:
            edges_file = EdgesFile(
                self._h5_path, self._csv_path, 
                default_population=population_name
            )
            self._pop_cache[population_name] = edges_file
            return edges_file
