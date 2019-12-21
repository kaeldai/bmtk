import pandas as pd
import numpy as np

from .column_property import ColumnProperty
from ..utils import lazy_property


class GroupIndex(object):
    def __init__(self, table, id_col, index_col):
        self.table = table
        self.id_col = id_col
        self.index_col = index_col

        self._group_ids_vals = table[id_col]
        self._group_index_vals = table[index_col]

    def get_group_id(self, row):
        return self._group_ids_vals[row]

    def get_index(self, row):
        return self._group_index_vals[row]

    def get_indices(self, group_id):
        return self.reverse_lu[self.reverse_lu['group_id'] == group_id]

    @lazy_property
    def reverse_lu(self, ):
        return pd.DataFrame({
            'group_id': np.array(self.table[self.id_col]),
            'group_index': self.table[self.index_col],
            'master_table_row': np.arange(0, len(np.array(self.table[self.id_col])))
        })


class GroupTableStruct(object):
    def __init__(self, group_id, group_table, parent):
        self.group_id = group_id
        self.parent = parent
        self.group_table = group_table
        self._nrows = len(group_table)

    @lazy_property
    def local_lu(self):
        return self.parent.group_index.get_indices(self.group_id)

    @lazy_property
    def group_indices(self):
        return self.local_lu['group_index']

    @lazy_property
    def master_rows(self):
        return self.local_lu['master_table_row']

    @lazy_property
    def columns(self):
        return ColumnProperty.from_h5(self.group_table)

    @property
    def node_ids(self):
        return self.parent.node_ids.get_rows(self.master_rows)

    def get_data(self, column):
        return np.array(self.group_table[column][self.group_indices])
        # return np.array(self.group_table[column][self.row_index])

    def to_dataframe(self):
        df = pd.DataFrame({c.name: self.get_data(c.name) for c in self.columns})
        df['group_id'] = self.group_id


        df['node_type_id'] = self.parent.network_props.get_ids(self.master_rows)
        df[self.parent.node_ids.column_name] = self.parent.node_ids.get_rows(self.master_rows)

        df = df.merge(self.parent.network_props.to_dataframe(), how='left', on='node_type_id')
        return df

    def __len__(self):
        return self._nrows

    def __getitem__(self, grp_index):
        group_props = {}
        for c in self.columns:
            group_props[c] = self.group_table[c.name][grp_index]
        return group_props

    def __contains__(self, column):
        return column in self.columns


class NodesModelProps(object):

    def __init__(self, group_table, grp_index, node_ids, network_props):
        self.node_ids = node_ids
        self.network_props = network_props
        self.group_index = grp_index
        self._group_table = group_table
        self._group_map = {}
        self._find_groups(group_table)

    @property
    def ids(self):
        return list(self._group_map.keys())

    def _find_groups(self, group_table):
        """Create a map between group-id and h5py.Group reference"""
        for grp_key, grp_h5 in group_table.items():
            if grp_key.isdigit():
                grp_id = int(grp_key)
                self._group_map[grp_id] = GroupTableStruct(grp_id, grp_h5, self)

    def get_props(self, row):
        grp_id = self.group_index.get_group_id(row)  # self._group_ids_ds[row]
        grp_index = self.group_index.get_index(row)  # self._group_index_ds[row]
        return self._group_map[grp_id][grp_index]

    @property
    def groups(self):
        return list(self._group_map.values())

    def get_group(self, group_id):
        return self._group_map[group_id]

    def to_dataframe(self, group_ids=None):
        group_ids = group_ids if group_ids is not None else list(self._group_map.keys())
        group_ids = [group_ids] if np.isscalar(group_ids) else group_ids

        if len(group_ids) == 0:
            return pd.DataFrame()

        else:
            ret_df = self._group_map[group_ids[0]].to_dataframe()
            for grp_id in group_ids[1:]:
                ret_df = ret_df.append(self._group_map[grp_id].to_dataframe(), sort=False)
            return ret_df


def load_nodes(group_table, node_ids, network_props):
    grp_index = GroupIndex(group_table, 'node_group_id', 'node_group_index')
    return NodesModelProps(group_table, grp_index, node_ids, network_props)


def load_edges(group_table):
    raise NotImplementedError()
    # return EdgesModelProps(group_table)


def load(group_table, node_ids, network_props, ctype='nodes'):
    if ctype == 'nodes':
        return load_nodes(group_table, node_ids, network_props)
    elif ctype == 'edges':
        return load_edges(group_table)
    else:
        raise AttributeError()
    #return ModelProps(group_table)