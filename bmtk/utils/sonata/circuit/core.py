import os
import h5py

from ..utils import check_magic, get_version
from .population import NodePopulation, EdgePopulation, load_nodes, load_edges

import logging
_logger = logging.getLogger(__name__)


class NodesRoot(object):
    """A struct for keeping track of the different node populations within a sonata file/directory"""
    def __init__(self):
        self._populations = {}

    def add(self, name, population):
        if name in self._populations:
            raise NameError('Node population with name {} already exists.'.format(name))
        else:
            self._populations[name] = population

    @property
    def population_names(self):
        return list(self._populations.keys())

    @property
    def populations(self):
        return list(self._populations.values())

    def __contains__(self, pop):
        pop_name = pop.name if isinstance(pop, NodePopulation) else pop
        return pop_name in self._populations.keys()

    def __getitem__(self, pop):
        pop_name = pop.name if isinstance(pop, NodePopulation) else pop
        return self._populations[pop_name]

    def __len__(self):
        return len(self._populations)

    def __iter__(self):
        return iter(self._populations.values())

    def __str__(self):
        ret_str = '/nodes\n'
        for p in self:
            ret_str += '{}'.format(str(p))
        return ret_str


class EdgesRoot(NodesRoot):
    def add(self, name, population):
        if name in self._populations:
            raise NameError('Edges population with name {} already exists.'.format(name))
        else:
            self._populations[name] = population

    def get_populations(self, name=None, source=None, target=None):
        """Find all populations with matching criteria, either using the population name (which will return a list
        of size 0 or 1) or based on the source/target population.

        To return a list of all populations just use populations() method

        :param name: (str) name of population
        :param source: (str or NodePopulation) returns edges with nodes coming from matching source-population
        :param target: (str or NodePopulation) returns edges with nodes coming from matching target-population
        :return: A (potential empty) list of EdgePopulation objects filter by criteria.
        """
        assert((name is not None) ^ (source is not None or target is not None))
        if name is not None:
            return [self[name]]

        else:
            selected_pops = self.population_names
            if source is not None:
                # filter out only edges with given source population
                source = source.name if isinstance(source, NodePopulation) else source
                selected_pops = [name for name in selected_pops
                                 if EdgePopulation.get_source_population(self._populations[name]) == source]
            if target is not None:
                # filter out by target population
                target = target.name if isinstance(target, NodePopulation) else target
                selected_pops = [name for name in selected_pops
                                 if EdgePopulation.get_target_population(self._populations[name]) == target]

            return [self[name] for name in selected_pops]

    def __str__(self):
        ret_str = '/edges\n'
        for p in self:
            ret_str += ' {}'.format(str(p))
        return ret_str


class CircuitRoot(object):
    def __init__(self):
        self.nodes = NodesRoot()
        self.edges = EdgesRoot()

    @property
    def has_nodes(self):
        return len(self.nodes) > 0

    @property
    def has_edges(self):
        return len(self.edges) > 0

    def __str__(self):
        ret_str = '/circuit\n'
        ret_str += str(self.nodes) + '\n'
        ret_str += str(self.edges) + '\n'
        return ret_str


def load_path(file_path, node_types_path=None, edge_types_path=None, require_magic=True, root='/'):
    h5_file = h5py.File(file_path, 'r')
    h5_root = h5_file[root]

    check_magic(h5_root, warning_only=not require_magic)
    sonata_version = get_version(h5_root)

    circuit_root = CircuitRoot()
    for pop_name, nodes_grp in h5_root.get('/nodes', {}).items():
        circuit_root.nodes.add(pop_name, load_nodes(name=pop_name, nodes_table=nodes_grp,
                                                    network_props_table=node_types_path, version=sonata_version))

    for pop_name, edges_grp in h5_root.get('/edges', {}).items():
        circuit_root.edges.add(pop_name, load_edges(pop_name, edges_table=edges_grp,
                                                    network_props_table=edge_types_path, version=sonata_version))

    return circuit_root


def load_directory():
    pass


def load_config():
    pass