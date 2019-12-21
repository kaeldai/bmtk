# Copyright 2017. Allen Institute. All rights reserved
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import os
import pandas as pd
import h5py
import numpy as np

from ..utils import range_itr, get_attribute_h5, lazy_property
from .node import Node, NodeSet
from .edge import Edge, EdgeSet
from .group import NodeGroup, EdgeGroup
from .types_table import TypesTable
from .column_property import ColumnProperty
from . import network_props
from . import model_props
from . import node_ids_table








class Population(object):
    def __init__(self, pop_name, pop_group, types_table):
        self._pop_name = pop_name
        self._pop_group = pop_group
        #self._types_table = types_table
        self._nrows = 0

        # For storing individual groups
        #self._group_map = {}  # grp-id --> h5py.Group object
        #self._find_groups()
        self._group_cache = {}  # grp-id --> soneta.io.Group() object

        # Refrences to most of the population's primary dataset

        self._network_props = network_props.load(types_table, population_name=pop_name, parent=pop_group,
                                                 ctype=self.ctype)

        # self._model_props = model_props.load(pop_group, node_ids=self.ctype)
        #self._group_id_ds = pop_group[self.group_id_column]
        #self._group_index_ds = pop_group[self.group_index_column]

        #self._group_indicies = {}  # grp-id --> list of rows indicies
        #self._group_indicies_cache_built = False

    @property
    def name(self):
        """name of current population"""
        return self._pop_name

    @property
    def ctype(self):
        raise NotImplementedError()

    @property
    def group_ids(self):
        """List of all group_ids belonging to population"""
        return self.model_ids

    @property
    def model_ids(self):
        return self._model_props.ids

    @property
    def groups(self):
        """Returns a list of sonata.Group objects"""
        return self._model_props.groups

    @property
    def models(self):
        return self._model_props

    @property
    def types_table(self):
        return self._network_props
        # return self._types_table

    @property
    def type_ids(self):
        return self._network_props.ids
        # return np.array(self._type_id_ds)

    @property
    def group_id_ds(self):
        return self._group_id_ds

    @property
    def group_index_ds(self):
        return self._group_index_ds

    @property
    def group_id_column(self):
        raise NotImplementedError

    @property
    def group_index_column(self):
        raise NotImplementedError

    def to_dataframe(self):
        """Convert Population to dataframe"""
        raise NotImplementedError

    def get_group(self, group_id):
        return self._model_props.get_group(group_id)

    def group_indicies(self, group_id, build_cache=False):
        """Returns a list of all the population row index that maps onto the given group.

        Used for iterating or searching within a Group

        :param group_id: id of a given group
        :param build_cache: Will cache indicies for all groups. Will be faster if making multiple calls but requires
         more memory (default False)
        :return: A (possibly empty) list of row indicies (non-contiguous, but unique)
        """
        if self._group_indicies_cache_built:
            return self._group_indicies.get(group_id, [])

        else:
            tmp_index = pd.DataFrame()
            # TODO: Need to check the memory overhead, especially for edges. See if an iterative search is just as fast
            tmp_index['grp_id'] = pd.Series(self._group_id_ds.values, dtype=self._group_id_ds.dtype)
            tmp_index['row_indx'] = pd.Series(range_itr(self._nrows), dtype=np.uint32)
            if build_cache:
                # save all indicies as arrays
                self._group_indicies = {grp_id: np.array(subset['row_indx'])
                                        for grp_id, subset in tmp_index.groupby(by='grp_id')}
                self._group_indicies_cache_built = True
                return self._group_indicies.get(group_id, [])
            else:
                # TODO: Manually del tmp_index to clear out the memory?
                tmp_index = tmp_index[tmp_index['grp_id'] == group_id]
                return np.array(tmp_index['row_indx'])

    def igroup_ids(self, row_indicies):
        return self._group_id_ds[list(row_indicies)]

    def igroup_indicies(self, row_indicies):
        return self._group_index_ds[list(row_indicies)]

    # def _find_groups(self):
    #     """Create a map between group-id and h5py.Group reference"""
    #     for grp_key, grp_h5 in self._pop_group.items():
    #         if grp_key.isdigit():
    #             grp_id = int(grp_key)
    #             self._group_map[grp_id] = grp_h5
    #         else:
    #             # TODO: Should we put a warning if an unrecognized group exists?
    #             pass

    def _build_group(self, group_id, group_h5):
        raise NotImplementedError

    def __len__(self):
        return self._nrows

"""
class NodeIDs(object):
    @property
    def is_indexed(self):
        pass

    @property
    def node_ids(self):
        raise NotImplementedError()

    @property
    def gids(self):
        return self.node_ids

    def get_node_id(self, node_id):
        raise NotImplementedError()

    def loc(self, node_id):
        pass

    @staticmethod
    def load(sonata_obj):
        if 'node_id' in sonata_obj:
            return HDF5NodeIDs(node_ids_ds=sonata_obj['node_id'])

    def __len__(self):
        return len(self.node_ids)


class HDF5NodeIDs(NodeIDs):
    def __init__(self, node_ids_ds, column_name='node_id'):
        self._column_name = column_name
        self._node_ids_ds = node_ids_ds

    @property
    def column_name(self):
        return self.column_name

    @property
    def node_ids(self):
        return np.array(self._node_ids_ds)

    @lazy_property
    def row_lu(self):
        return pd.Series(range_itr(len(self)), index=self.node_ids, dtype=self.node_ids.dtype)

    def get_row(self, node_id):
        return self.row_lu.loc[node_id]

    def get_node_id(self, row_index):
        return self._node_ids_ds[row_index]

    def get_node_ids(self, rows):
        return self._node_ids_ds[rows]

    def get_gid(self, node_id):
        return node_id
"""

class NodePopulation(Population):
    def __init__(self, pop_name, pop_group, node_types_tables, metadata=None):
        super(NodePopulation, self).__init__(pop_name=pop_name, pop_group=pop_group, types_table=node_types_tables)
        self._metadata = metadata or {}
        self._node_ids_table = node_ids_table.load(population=pop_name, table=pop_group)
        self._nrows = len(self._node_ids_table)

        self._model_props = model_props.load(pop_group, node_ids=self._node_ids_table,
                                             network_props=self._network_props, ctype=self.ctype)

        self.__itr_index = 0  # for iterator

    #@property
    #def group_id_column(self):
    #    return 'node_group_id'

    #@property
    #def group_index_column(self):
    #    return 'node_group_index'

    @property
    def node_ids(self):
        return self._node_ids_table.node_ids

    @property
    def ctype(self):
        return 'nodes'

    @property
    def node_types_table(self):
        # return self._types_table
        return self._network_props

    def to_dataframe(self, group_ids=None):
        return self._model_props.to_dataframe(group_ids=group_ids)


    def get_row(self, row_num):
        node_id = self._node_ids_table.get_row(row_num)
        model_props = self._model_props.get_props(row_num)
        network_props = self._network_props.get_props(row_num)

        return Node(node_id, 100, network_props, None, model_props, None)

    def get_rows(self, row_indicies):
        """Returns a set of all nodes based on list of row indicies.

        Warning: currently due to the use of h5py, the list must be ordered and cannot contain duplicates.

        :param row_indicies: A list of row indicies
        :return: An iterable NodeSet of nodes in the specified indicies
        """
        # TODO: Check that row_indicies is unsigned and the max (which will be the last value) < n_rows
        # TODO: Check order and check for duplicates in list
        return NodeSet(row_indicies, self)

    def inode_ids(self, row_indicies):
        return self._node_ids_table.get_node_id(row_indicies)

    def inode_type_ids(self, rows):
        ## self._node_type_id_ds
        ## return self._type_id_ds[list(row_indicies)]
        return self._network_props.get_ids(rows)

    def get_node_id(self, node_id):
        row_indx = self._node_ids_table.get_row(node_id=node_id)
        return self.get_row(row_indx)

    def filter(self, **filter_props):
        for grp in self.groups:
            for node in grp.filter(**filter_props):
                yield node

    def _build_group(self, group_id, group_h5):
        return NodeGroup(group_id, group_h5, self)

    def __iter__(self):
        self.__itr_index = 0
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.__itr_index >= self._nrows:
            raise StopIteration

        nxt_node = self.get_row(self.__itr_index)
        self.__itr_index += 1
        return nxt_node

    def __getitem__(self, item):
        if isinstance(item, slice):
            # TODO: Check
            start = item.start if item.start is not None else 0
            stop = item.stop if item.stop is not None else self._nrows
            row_indicies = range_itr(start, stop, item.step)
            return NodeSet(row_indicies, self)

        elif isinstance(item, int):
            return self.get_row(item)

        elif isinstance(item, list):
            return NodeSet(item)
        else:
            print('Unable to get item using {}.'.format(type(item)))

    def __repr__(self):
        ret_str = '{\n'
        ret_str += '  population name: {}\n'.format(self.name)
        ret_str += '  num of nodes: {}\n'.format(len(self))
        ret_str += '  node_types_table: {}\n'.format(self.node_types_table)
        ret_str += '  class: {}\n'.format(self.__class__)
        for k, v in self._metadata.items():
            ret_str += '  {}: {}\n'.format(k, v)
        ret_str += '}'
        return ret_str


def load_nodes(name, nodes_table, network_props_table=None, version='0.1'):

    metadata = {}
    if isinstance(nodes_table, h5py.Group):
        metadata['format'] = 'HDF5'
        metadata['file'] = os.path.abspath(nodes_table.file.filename)
        metadata['location'] = nodes_table.name

    return NodePopulation(name, nodes_table, network_props_table, metadata)


class EdgesIndex(object):
    def __init__(self):
        pass

    def get_row(self, node_id):
        pass

    def get_node_id(self, row):
        pass

    def get_node_ids(self, rows):
        pass



class EdgePopulation(Population):
    class __IndexStruct(object):
        """Class sto store indicies subgroup"""
        # TODO: Use collections.namedtuple
        def __init__(self, lookup_table, edge_table):
            self.lookup_table = lookup_table
            self.edge_table = edge_table

    def __init__(self, pop_name, pop_group, edge_types_tables, metadata=None):
        super(EdgePopulation, self).__init__(pop_name=pop_name, pop_group=pop_group, types_table=edge_types_tables)

        # keep reference to source and target datasets
        self._source_node_id_ds = pop_group['source_node_id']
        self._target_node_id_ds = pop_group['target_node_id']

        self._nrows = len(self._source_node_id_ds)
        self._metadata = metadata or {}


        # TODO: Throw an error/warning if missing
        self._source_population = EdgePopulation.get_source_population(pop_group)
        self._target_population = EdgePopulation.get_target_population(pop_group)

        self.__itr_index = 0

        # TODO: use a function pointer for get_index so it doesn't have to run a conditional every time
        # TODO: add property and/or property so user can determine what indicies exists.
        self._targets_index = None
        self._has_target_index = False
        self._sources_index = None
        self._has_source_index = False
        self.build_indicies()

    # @property
    # def group_id_column(self):
    #     return 'edge_group_id'

    # @property
    # def group_index_column(self):
    #     return 'edge_group_index'

    @property
    def ctype(self):
        return 'edges'

    @property
    def source_population(self):
        return self._source_population

    @property
    def target_population(self):
        return self._target_population

    @staticmethod
    def get_source_population(pop_group_h5):
        return get_attribute_h5(pop_group_h5['source_node_id'], 'node_population', None)

    @staticmethod
    def get_target_population(pop_group_h5):
        return get_attribute_h5(pop_group_h5['target_node_id'], 'node_population', None)

    @property
    def edge_types_table(self):
        return self._types_table

    def to_dataframe(self):
        raise NotImplementedError()


    def build_indicies(self):
        if 'indicies' in self._pop_group:
            indicies_grp = self._pop_group['indicies']
            for index_name, index_grp in indicies_grp.items():
                # TODO: Let __IndexStruct build the indicies
                # Make sure subgroup has the correct datasets
                if not isinstance(index_grp, h5py.Group):
                    continue

                if 'node_id_to_range' not in index_grp:
                    # TODO: make this more general, i.e 'id_to_range' thus we can index on gids, edge_types, etc
                    # TODO: Check that there are two columns in dataset
                    raise Exception('index {} in {} edges is missing column {}.'.format(index_name, self.name,
                                                                                        'node_id_to_range'))
                if 'range_to_edge_id' not in index_grp:
                    raise Exception('index {} in {} edges is missing column {}.'.format(index_name, self.name,
                                                                                        'range_to_edge_id'))

                # Cache the index
                targets_lookup = index_grp['node_id_to_range']
                edges_range = index_grp['range_to_edge_id']
                index_obj = self.__IndexStruct(targets_lookup, edges_range)

                # Determine the type of index
                if index_name == 'source_to_target':
                    self._sources_index = index_obj
                    self._has_source_index = True
                elif index_name == 'target_to_source':
                    self._targets_index = index_obj
                    self._has_target_index = True
                else:
                    # TODO: Need to send this to a logger rather than stdout
                    print('Unrecognized index {}. Ignoring.'.format(index_name))

    def _build_group(self, group_id, group_h5):
        return EdgeGroup(group_id, group_h5, self)

    def group_indicies(self, group_id, build_cache=False, as_list=False):
        if as_list:
            return super(EdgePopulation, self).group_indicies(group_id, build_cache)

        # For nodes it's safe to just keep a list of all indicies that map onto a given group. For edges bc there are
        # many more rows (and typically a lot less groups), We want to build an index like for source/target ids
        if len(self._group_map) == 1:
            return len(self), [[0, len(self)]]

        grp_indicies = super(EdgePopulation, self).group_indicies(group_id, build_cache=False)
        if len(grp_indicies) == 0:
            # Return an index with no ranges
            return 0, []

        # cluster into ranges. Naively implement, there is probably a faster way to cluster an ordered array!
        range_beg = grp_indicies[0]
        ranges = []
        for i in range_itr(1, len(grp_indicies)):
            if (grp_indicies[i-1]+1) != grp_indicies[i]:
                ranges.append([range_beg, grp_indicies[i-1]+1])
                range_beg = grp_indicies[i]
        ranges.append([range_beg, grp_indicies[-1]+1])
        return len(grp_indicies), np.array(ranges, dtype=np.uint32)

    '''
    def _get_target_index(self):
        # TODO: Do only once
        if self._targets_index is not None:
            return self._targets_index

        if 'incidies' in self._pop_group:
            if 'target_to_source' in self._pop_group['incidies']:
                targets_lookup = self._pop_group['incidies']['target_to_source']['node_id_to_range']
                edges_range = self._pop_group['incidies']['target_to_source']['range_to_edge_id']
                self._targets_index = self.__IndexStruct(targets_lookup, edges_range)
                return self._targets_index

        # TODO: What to do if index doesn't exist?
        raise NotImplementedError
    '''

    def get_row(self, index):
        src_node = self._source_node_id_ds[index]
        trg_node = self._target_node_id_ds[index]
        edge_type_id = self._type_id_ds[index]
        edge_types_props = self.edge_types_table[edge_type_id]

        edge_group_id = self._group_id_ds[index]
        edge_group_index = self._group_index_ds[index]
        edge_group_props = self.get_group(edge_group_id)[edge_group_index]
        return Edge(trg_node_id=trg_node, src_node_id=src_node, source_pop=self.source_population,
                    target_pop=self.target_population, group_id = edge_group_id,
                    group_props=edge_group_props, edge_types_props=edge_types_props)

    def filter(self, **filter_props):
        selected_edge_types = set(self.edge_types_table.edge_type_ids)
        types_filter = False  # Do we need to filter results by edge_type_id
        if 'edge_type_id' in filter_props:
            # TODO: Make sure the edge_type_id is valid
            selected_edge_types = set([filter_props['edge_type_id']])
            del filter_props['edge_type_id']
            types_filter = True

        if 'group_id' in filter_props:
            grp_id = filter_props['group_id']
            grp_id = [grp_id] if np.isscalar(grp_id) else grp_id
            selected_groups = set(grp_id)
            del filter_props['group_id']
        else:
            selected_groups = set(self._group_map.keys())  # list of grp_id's that will be used

        group_prop_filter = {}  # list of actual query statements
        group_filter = False  # do we need to filter results by group_id

        # Go through filter key==value pairs, create filters for groups and edge_types
        for filter_key, filter_val in filter_props.items():
            # Find out what groups, if any, the column should search in.
            group_query = False  # If it's querying a group property don't look in edge_types
            types_query = False
            for grp_id, grp_h5 in self._group_map.items():
                if filter_key in grp_h5:
                    # TODO: Need to check the dtype's match
                    selected_groups &= set([grp_id])
                    group_prop_filter[filter_key] = filter_val
                    group_query = True
                    group_filter = True

            if (not group_query) and filter_key in self.edge_types_table.columns:
                # Presearch the edge types and get only those edge_type_ids which match key==val
                selected_edge_types &= set(self.edge_types_table.find(filter_key, filter_val))
                types_filter = True
                types_query = True

            if not (group_query or types_query):
                # Property key neither exists in a group or the edge_types_table
                raise Exception('Could not find property {}'.format(filter_key))

        # Iterate through all nodes, only returning those that match the filter
        for indx in range_itr(self._nrows):
            # Filter by edge_type_id
            if types_filter:
                # TODO: Invert the selected_edge_types, it will be faster to fail immeditely than search the entire list
                if self._type_id_ds[indx] not in selected_edge_types:
                    continue

            # Filter by group properties
            if group_filter:
                # TODO: Invert group search
                grp_id = self._group_id_ds[indx]
                if grp_id not in selected_groups:
                    continue

                grp_index = self._group_index_ds[indx]
                search_failed = True
                for prop_key, prop_val in group_prop_filter.items():
                    if prop_val != self._group_map[grp_id][prop_key][grp_index]:
                        break
                else:
                    search_failed = False

                if search_failed:
                    continue

            yield self.get_row(indx)

    def get_target(self, target_node_id):
        # TODO: Raise an exception, or call find() and log a warning that the index is not available
        # TODO: check validity of target_node_id (non-negative integer and smaller than index range)
        assert(self._has_target_index)
        return self._get_index(self._targets_index, target_node_id)

    def get_targets(self, target_node_ids):
        # TODO: verify input is iterable
        assert(self._has_target_index)
        trg_index = self._targets_index
        for trg_id in target_node_ids:
            for edge in self._get_index(trg_index, trg_id):
                yield edge

    def get_source(self, source_node_id):
        assert(self._has_source_index)
        return self._get_index(self._sources_index, source_node_id)

    def get_sources(self, source_node_ids):
        assert(self._has_target_index)
        trg_index = self._sources_index
        for src_id in source_node_ids:
            for edge in self._get_index(trg_index, src_id):
                yield edge

    def _get_index(self, index_struct, lookup_id):
        # TODO: Use a EdgeSet instead
        if lookup_id >= len(index_struct.lookup_table):
            # TODO: Store length in index
            raise StopIteration

        edges_table = index_struct.edge_table
        lookup_beg, lookup_end = index_struct.lookup_table[lookup_id]
        for i in range_itr(lookup_beg, lookup_end):
            edge_indx_beg, edge_indx_end = edges_table[i]
            for edge_indx in range_itr(edge_indx_beg, edge_indx_end):
                yield self.get_row(edge_indx)

    def __iter__(self):
        self.__itr_index = 0
        return self

    def __next__(self):
        if self.__itr_index >= self._nrows:
            raise StopIteration

        next_edge = self.get_row(self.__itr_index)
        self.__itr_index += 1
        return next_edge

    def next(self):
        return self.__next__()

    def __repr__(self):
        ret_str = '{\n'
        ret_str += '  population name: {}\n'.format(self.name)
        ret_str += '  source/target nodes: {} -> {}\n'.format(self.source_population, self.target_population)
        ret_str += '  num of edges: {}\n'.format(len(self))
        # ret_str += '  node_types_table: {}\n'.format(self.edge_types_table)
        ret_str += '  class: {}\n'.format(self.__class__)
        for k, v in self._metadata.items():
            ret_str += '  {}: {}\n'.format(k, v)
        ret_str += '}'
        return ret_str


def load_edges(name, edges_table, network_props_table=None, version='0.1'):
    metadata = {}
    if isinstance(edges_table, h5py.Group):
        metadata['format'] = 'HDF5'
        metadata['file'] = os.path.abspath(edges_table.file.filename)
        metadata['location'] = edges_table.name

    return EdgePopulation(name, edges_table, network_props_table, metadata)