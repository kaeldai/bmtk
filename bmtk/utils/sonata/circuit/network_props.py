import os
import numpy as np
import pandas as pd
import h5py
import six

from .column_property import ColumnProperty
from ..utils import range_itr, lazy_property



class NetworkProps(object):
    def __init__(self, props_df):
        self._props_df = props_df
        self._columns = ColumnProperty.from_csv(props_df)
        self._index_ds = None

        self._props_dict = self._props_df.to_dict(orient='index')

    @property
    def type_ids(self):
        return np.array(self._props_dict.keys())

    @property
    def ids(self):
        return self.type_ids

    @property
    def columns(self):
        return self._columns

    def add_index(self, index_ds):
        self._index_ds = index_ds

    @lazy_property
    def index(self):
        return self._index_ds

    @lazy_property
    def reverse_index(self):
        return pd.Series(range_itr(len(self.index)), index=self.index.values, dtype=self.index.dtype)

    def get_props(self, row):
        return self[self.index[row]]

    def get_ids(self, rows):
        return self.index[rows][()]

    def to_dataframe(self):
        return self._props_df

    def get_rows(self, type_id):
        return self.reverse_index.loc[type_id].values

    def __getitem__(self, type_id):
        return self._props_dict[type_id]


class EmptyTable(NetworkProps):
    def __init__(self):
        super(EmptyTable, self).__init__(pd.DataFrame({'node_type_id': [-1]}).set_index('node_type_id'))
        #print(self.type_ids)
        #print(list(self._props_dict.keys()))
        #exit()

    def get_props(self, row):
        return {}

    def get_ids(self, rows):
        return np.full(len(rows), -1)


def load(types_table, population_name=None, parent=None, ctype='nodes'):
    if types_table is None:
        return EmptyTable()

    if isinstance(types_table, six.string_types):
        types_table = pd.read_csv(types_table, sep=' ')

    if isinstance(types_table, NetworkProps):
        return types_table

    elif isinstance(types_table, pd.DataFrame):
        if population_name is not None and 'population' in types_table:
            types_table = types_table[types_table['population'] == population_name]

        netprops = NetworkProps(types_table)
        if parent is not None:
            if ctype == 'nodes':
                netprops.add_index(parent['node_type_id'])
            elif ctype == 'edges':
                netprops.add_index(parent['edge_type_id'])
        return netprops

    elif isinstance(types_table, h5py.Group):
        raise NotImplementedError()
