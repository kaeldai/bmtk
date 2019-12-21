import tempfile
import itertools
import numpy as np
import pandas as pd
import h5py

from bmtk.utils.sonata.circuit.population import load_nodes


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def test_basic_h5():
    tmp_file, tmp_file_name = tempfile.mkstemp(suffix='.hdf5')
    with h5py.File(tmp_file_name, 'r+') as h5:
        h5.create_dataset('node_id', data=np.arange(1000))
        h5.create_dataset('node_group_id', data=[0]*500 + [1]*500)
        h5.create_dataset('node_group_index', data=list(itertools.chain(range(500), range(500))))
        h5.create_group('0')
        h5.create_group('1')

        population = load_nodes('test_pop', h5)
        assert(population.name == 'test_pop')
        assert(population.ctype == 'nodes')
        assert(np.all(population.node_ids == np.arange(1000)))
        assert(population.get_row(10).columns == {'node_id'})
        assert(population.get_row(10)['node_id'] == 10)

        # print(population.get_rows(range(50, 100, 10)))
        assert(population.get_row(50).columns == {'node_id'})
        assert(population.get_node_id(50)['node_id'] == 50)

        for i, n in enumerate(population):
            assert(n['node_id'] == i)

        assert(set(population.model_ids) == {0, 1})


def test_groups():
    tmp_file, tmp_file_name = tempfile.mkstemp(suffix='.hdf5')
    with h5py.File(tmp_file_name, 'r+') as h5:
        h5.create_dataset('node_id', data=np.arange(1000))
        h5.create_dataset('node_group_id', data=[0]*500 + [1]*500)
        h5.create_dataset('node_group_index', data=list(itertools.chain(range(500), range(500))))
        h5.create_dataset('node_type_id', data=list([0]*250 +[1]*250 + [0]*500))
        h5.create_dataset('0/nsyns', data=np.ones(500)*6)
        h5.create_dataset('1/nsyns', data=np.arange(0, 1000, 2))
        h5.create_dataset('1/delays', data=[0.2]*250 + [1.0]*250 + [0.5]*250)

        population = load_nodes('test_pop', h5, pd.DataFrame({'node_type_id': [0, 1], 'model_type': ['point', 'biophysical']}))
        print(population.get_row(0))
        assert(population.group_ids == [0, 1])
        grp1 = population.get_group(1)
        assert(set(grp1.columns) == {'nsyns', 'delays'})
        assert(len(grp1.get_data('delays')) == 500)
        assert(np.all(grp1.get_data('nsyns') == np.arange(0, 1000, 2)))
        assert(len(grp1.get_data('nsyns')) == 500)

        assert(grp1.to_dataframe().shape == (500, 6))
        assert(np.all(grp1.node_ids == np.arange(500, 1000)))

        assert(population.to_dataframe().shape == (1000, 6))
        assert(population.to_dataframe(0).shape == (500, 5))
        print(population.to_dataframe())

        #print(grp1.node_ids)

        #for grp in population.groups:
        #    print(grp.group_id)
        #    print(grp.columns)
        # print(population.to_dataframe())





# test_basic_h5()

