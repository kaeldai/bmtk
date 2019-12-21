import numpy as np
import pandas as pd
from six.moves import range

from ..utils import lazy_property


class NodeIDsTable(object):
    def __init__(self, node_ids_ds, column_name='node_id'):
        self._column_name = column_name
        self._node_ids_ds = node_ids_ds

    @property
    def column_name(self):
        return self._column_name

    @lazy_property
    def node_ids(self):
        return np.array(self._node_ids_ds)

    @lazy_property
    def row_lu(self):
        # An index for looking up the row number from the list of node_ids.
        # This is not always necessary to call depending how pySonata is used by the user. Create index
        #  only once and only when it's called
        return pd.Series(range(len(self)), index=self.node_ids, dtype=self.node_ids.dtype)

    def get_row(self, node_id):
        # Given a node_id do a lookup in the master index/table where the node is located.
        return self.row_lu.loc[node_id]

    def get_rows(self, node_ids):
        # Takes a list of node_id's and returns a list of the row in the master index
        return np.array(self.row_lu.loc[node_ids])

    def get_node_id(self, row):
        return self._node_ids_ds[row]

    def get_node_ids(self, rows):
        return np.array(self.node_ids[rows])

    def __len__(self):
        return len(self.node_ids)


def load(table, population):
    if 'node_id' in table:
        node_ids_ds = table['node_id']

    elif 'node_group_index' in table:
        node_ids_ds = np.arange(0, len(table['node_group_index']))

    else:
        raise AttributeError('Could not get node_ids from population {}'.format(population))

    return NodeIDsTable(node_ids_ds=node_ids_ds)