import pandas as pd
import numpy as np
from bmtk.utils.sonata.circuit.population import NodePopulation
from bmtk.utils.sonata.circuit.types_table import NodeTypesTable


node_types_table_df = pd.DataFrame({
    'node_type_id': [100, 200],
    'attr1': [1, 10],
    'attr2': [20.0, 40.0],
    'attr3': ['bio', 'point']
})

class MockHDF5File(object):
    def __init__(self):
        self.df = pd.DataFrame({
            'node_id': np.arange(101),
            'node_type_id': [100]*51 + [200]*50,
            'node_group_id': 0,
            'node_group_index': np.arange(101)
        })

    def items(self):
        return [('0', pd.DataFrame({'x': np.linspace(5.0, 100.0, 101),
                                    'y': np.linspace(-50.0, 50.0, 101)}))]

    def __getitem__(self, item):
        return self.df[item]

    def __contains__(self, item):
        return item in self.df.columns



types_table = NodeTypesTable()
types_table.add_table(node_types_table_df)
nodes_h5 = MockHDF5File()
pop = NodePopulation('mypop', pop_group=nodes_h5, node_types_tables=node_types_table_df)

# print(pop.node_ids)
assert(np.all(pop.node_ids == np.arange(0, 101)))
# print(len(pop))
assert(len(pop) == 101)
assert(pop.name == 'mypop')
assert(pop.get_node_id(6).node_id == 6)
assert(pop.get_row(5).node_id == 5)
assert(len(pop[1::2]) == 50)
for n in pop[1::2]:
    assert(n.node_id % 2 == 1)

assert(pop.get_row(5)['attr3'] == 'bio')
pop.types_table[100]['attr3'] = 'my' + pop.types_table[100]['attr3'] + '.swc'
assert(pop.get_row(5)['attr3'] == 'mybio.swc')

assert(pop.get_rows([0, 5, 50, 100]).node_ids.tolist() == [0, 5, 50, 100])

assert(pop.get_node_id(99)['attr3'] == 'point')
assert(np.all(pop.inode_type_ids([0, 90, 95, 5]) == [100, 200, 200, 100]))

# print(pop.to_dataframe())

assert(np.all(pop.node_types_table.get_rows(100) == range(0, 51)))
assert(np.all(pop.node_types_table.get_rows(200) == range(51, 101)))

assert(pop.model_ids == [0])
print(pop.models.to_dataframe(group_id=0))


"""
# BioNet usecase: Check that "model_type" property exists in all groups
for grp in node_pop.groups:
    assert('model_type' in grp.all_columns)


# BioNet usecase: check if a population contains virtual_nodes (exclusivly or not)
model_types = set()
for grp in node_pop.groups:
    model_types.update(set(np.unique(grp.get_values('model_type'))))
print('virtual' in model_types)


# General usecase: modify 'morphology' column, preprending morphology_dir and appending swc
if 'morphology' in node_pop.types_table.columns:
    for nt_id in np.unique(node_pop.type_ids):
        node_type = node_pop.types_table[nt_id]
        if node_type['morphology'] is not None:
            node_type['morphology'] = os.path.join(morp_dir, node_type['morphology'] + '.swc')


# General usecase: similiar to above but loading the dynamic_params from types_table
"""

