import tempfile
import itertools
import numpy as np
import h5py
import pandas as pd

class ReadNodes:
    """
    def setup(self):
        #tmp_h5, tmp_h5_name = tempfile.mkstemp(suffix='.h5')
        #self.nodes_h5 = tmp_h5_name

        tmp_csv, tmp_csv_name = tempfile.mkstemp(suffix='.csv')
        pd.DataFrame({'node_type_id': [0, 1], 'model_type': ['point', 'biophysical']}).to_csv(tmp_csv_name, sep=' ')
    """
    timeout = 360.0

    def setup_cache(self):
        tmp_h5, tmp_h5_name = tempfile.mkstemp(suffix='.h5')
        #self.nodes_h5 = tmp_h5_name
        N = 500000
        N_0 = int(N/2)
        N_1 = N - N_0
        with h5py.File(tmp_h5_name, 'r+') as h5:
            h5.create_dataset('/nodes/v1/node_id', data=np.arange(N))
            h5.create_dataset('/nodes/v1/node_group_id', data=[0]*N_0 + [1]*N_1)
            h5.create_dataset('/nodes/v1/node_group_index', data=list(itertools.chain(range(N_0), range(N_1))))
            h5.create_dataset('/nodes/v1/node_type_id', data=list([0]*int(N_0/2) + [1]*(N_0 - int(N_0/2)) + [0]*N_1))
            h5.create_dataset('/nodes/v1/0/nsyns', data=np.ones(N_0)*6)
            h5.create_dataset('/nodes/v1/1/nsyns', data=np.arange(0, N_1*2, 2))
            h5.create_dataset('/nodes/v1/1/delay', data=[0.2]*int(N_1/2) + [1.0]*(N_1 - int(N_1/2))) # + [0.5]*250)

        tmp_csv, tmp_csv_name = tempfile.mkstemp(suffix='.csv')
        pd.DataFrame({'node_type_id': [0, 1], 'model_type': ['point', 'biophysical']}).to_csv(tmp_csv_name, sep=' ')

        return tmp_h5_name, tmp_csv_name
        #tmp_csv, tmp_csv_name = tempfile.mkstemp(suffix='.csv')
        #pd.DataFrame({'node_type_id': [0, 1], 'model_type': ['point', 'biophysical']}).to_csv(tmp_csv_name, sep=' ')


    def time_iterate_nodes(self, tmp_h5_name):
        from bmtk.utils.sonata.file import File
        sonata_file = File(data_files=tmp_h5_name[0],
                           data_type_files=tmp_h5_name[1]) # pd.DataFrame({'node_type_id': [0, 1], 'model_type': ['point', 'biophysical']}))

        l = [n for n in sonata_file.nodes['v1'][::10]]
        #for i, node in enumerate(sonata_file.nodes['v1'])[0::10]:
        #    assert(node.node_id == i)

    def peakmem_iter(self, tmp_h5_name):
        from bmtk.utils.sonata.file import File
        sonata_file = File(data_files=tmp_h5_name[0], data_type_files=tmp_h5_name[1])

        df = sonata_file.nodes['v1'].to_dataframe()
        # assert(df.shape == (1000, 5))
        #for i, node in enumerate(sonata_file.nodes['v1']):
        #    assert(node.node_id == i)
