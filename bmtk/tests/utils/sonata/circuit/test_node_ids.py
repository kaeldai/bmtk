import pytest
import tempfile
import h5py
import pandas as pd
import numpy as np

from bmtk.utils.sonata.circuit import node_ids_table


def test_contig_df():
    # Test with input on pandas dataframe
    node_ids_index = node_ids_table.load(pd.DataFrame({'node_id': range(1000)}), population='test')
    assert(node_ids_table.column_name == 'node_id')
    assert(np.all(node_ids_index.node_ids == np.arange(1000)))
    assert(node_ids_index.get_row(node_id=102) == 102)
    assert(node_ids_index.get_node_id(row=103) == 103)
    assert(np.all(node_ids_index.get_node_ids(rows=[101, 102, 103]) == [101, 102, 103]))
    assert(np.all(node_ids_index.get_node_ids(rows=np.arange(500, 445, -1)) == range(500, 445, -1)))
    assert(np.all(node_ids_index.get_node_ids(rows=[0, 999, 44]) == [0, 999, 44]))


def test_contig_h5():
    # Standard use-case where nodes are contigously ordered from 0 to N.
    tmp_file, tmp_file_name = tempfile.mkstemp(suffix='.hdf5')
    with h5py.File(tmp_file_name, 'r+') as h5:
        h5.create_dataset('node_id', data=np.arange(1000))
        node_ids_index = node_ids_table.load(h5, population='test')
        assert(np.all(node_ids_index.node_ids == np.arange(1000)))
        assert(node_ids_index.get_row(node_id=102) == 102)
        assert(node_ids_index.get_node_id(row=103) == 103)
        assert(np.all(node_ids_index.get_node_ids(rows=[101, 102, 103]) == [101, 102, 103]))
        assert(np.all(node_ids_index.get_node_ids(rows=np.arange(500, 445, -1)) == range(500, 445, -1)))
        assert(np.all(node_ids_index.get_node_ids(rows=[0, 999, 44]) == [0, 999, 44]))


def test_implicit_nodes_h5():
    # Sonata use case where the 'node_id' column is missing, assumes a contig ordered set from 0 to N
    tmp_file, tmp_file_name = tempfile.mkstemp(suffix='.hdf5')
    with h5py.File(tmp_file_name, 'r+') as h5:
        h5.create_dataset('node_group_index', data=np.zeros(1000))
        node_ids_index = node_ids_table.load(h5, population='test')
        assert(np.all(node_ids_index.node_ids == np.arange(1000)))
        assert(node_ids_index.get_row(node_id=102) == 102)
        assert(np.all(node_ids_index.get_rows(node_ids=[50, 20, 30]) == [50, 20, 30]))
        assert(node_ids_index.get_node_id(row=103) == 103)
        assert(np.all(node_ids_index.get_node_ids(rows=[101, 102, 103]) == [101, 102, 103]))
        assert(np.all(node_ids_index.get_node_ids(rows=np.arange(500, 445, -1)) == range(500, 445, -1)))
        assert(np.all(node_ids_index.get_node_ids(rows=[0, 999, 44]) == [0, 999, 44]))


def test_randomize_h5():
    # Make sure it can handle out-of-ordered node sets
    node_ids_orig = np.arange(100)
    np.random.shuffle(node_ids_orig)

    tmp_file, tmp_file_name = tempfile.mkstemp(suffix='.hdf5')
    with h5py.File(tmp_file_name, 'r+') as h5:
        h5.create_dataset('node_id', data=node_ids_orig)
        node_ids_index = node_ids_table.load(h5, population='test')

        assert(np.all(node_ids_index.node_ids == node_ids_orig))
        assert(node_ids_index.get_row(node_id=55) == np.where(node_ids_orig == 55)[0][0])
        indx = node_ids_index.get_rows(node_ids=[10, 20, 15])
        assert(np.all(node_ids_orig[indx] == [10, 20, 15]))
        assert(node_ids_index.get_node_id(row=1) == node_ids_orig[1])
        assert(np.all(node_ids_index.get_node_ids(rows=[5, 15, 10]) == node_ids_orig[[5, 15, 10]]))


def test_missing_h5():
    tmp_file, tmp_file_name = tempfile.mkstemp(suffix='.hdf5')
    node_ids_orig = list(range(10, 15)) + list(range(30, 40))
    with h5py.File(tmp_file_name, 'r+') as h5:
        h5.create_dataset('node_id', data=node_ids_orig)
        node_ids_index = node_ids_table.load(h5, population='test')
        assert(np.all(node_ids_index.node_ids == node_ids_orig))
        assert(np.all(node_ids_index.get_node_ids(rows=[3, 4, 5, 6]) == [13, 14, 30, 31]))
        assert(np.all(node_ids_index.get_rows(node_ids=[31, 30, 14, 13]) == [6, 5, 4, 3]))


if __name__ == '__main__':
    test_missing_h5()
    # test_implicit_nodes_h5()