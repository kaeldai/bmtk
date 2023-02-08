import os
import math
import pandas as pd
import numpy as np
import six
from neuron import h

from scipy.interpolate import NearestNDInterpolator as NNip
from bmtk.simulator.bionet.modules.sim_module import SimulatorMod
from bmtk.simulator.bionet.modules.xstim_waveforms import stimx_waveform_factory
from bmtk.simulator.bionet.utils import rotation_matrix
from bmtk.simulator.bionet.io_tools import io

class ComsolMod(SimulatorMod):
    """ 
    __init__: Comsol file is loaded as pandas dataframe
    and then used to set up nearest neighbour (NN) interpolation object to create interpolation map

    initialise: An interpolation map is defined per cell of every segment and stored in dictionary self._NN 
    The interpolation map maps (the center of) every segment to its NN. It is calculated once here and then used in every step. 

    step: An interpolation map is used to point each segment to its NN and find the corresponding voltage value in the comsol df.

    """
    def __init__(self, comsol_file, waveform=None, cells=None, set_nrn_mechanisms=True,
                 node_set=None):

        if waveform is not None:
            self._waveform = waveform  # TODO: Check if waveform is a file or dict and load it appropiately

        self._comsol_file = comsol_file
        self._comsol = pd.read_csv(comsol_file, sep="\s+", header=8, usecols=[0,1,2,3], names=['x','y','z','V'])
        self._NNip = NNip(self._comsol[['x','y','z']], np.arange(len(self._comsol['V'])))
        self._NN = {}

        self._set_nrn_mechanisms = set_nrn_mechanisms
        self._cells = cells
        self._local_gids = []
        self._fih = None

    # def __set_extracellular_mechanism(self):
    #     for gid in self._local_gids:

    def initialize(self, sim):
        if self._cells is None:
            # if specific gids not listed just get all biophysically detailed cells on this rank
            self._local_gids = sim.biophysical_gids
        else:
            # get subset of selected gids only on this rank
            self._local_gids = list(set(sim.local_gids) & set(self._all_gids))

        for gid in self._local_gids:
            # cell = sim.net.get_local_cell(gid)
            cell = sim.net.get_cell_gid(gid)
            cell.setup_xstim(self._set_nrn_mechanisms)
            r05 = cell.seg_coords.p05
            self._NN[gid] = self._NNip(r05.T)

        def set_pointers():
            for gid in self._local_gids:
                cell = sim.net.get_cell_gid(gid)
                # cell = sim.net.get_local_cell(gid)
                cell.set_ptr2e_extracellular()

        self._fih = sim.h.FInitializeHandler(0, set_pointers)

    def step(self, sim, tstep):
        for gid in self._local_gids:
            cell = sim.net.get_cell_gid(gid)
            NN = self._NN[gid]
            v_ext = self._comsol['V'].iloc[NN].to_numpy()
            cell.set_e_extracellular(h.Vector(v_ext))