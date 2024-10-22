#####################################
Running Network Simulations with BMTK
#####################################

In this section we will show how to use BMTK and SONATA to run simulation(s) on a brain network model. 

Unlike other neural simulation tools which will create and simulate a network in one script, BMTK workflow design is to
to split up these two parts of the process. So before we can run a simulation we must first procure a network model 
(typically store using `SONATA circuit format`_). We can either download an existing model, or alternatively use a tool
like the BMTK Network Builder to create one from scratch.

Once we have our network to run simulations on, we typically need to complete the following steps:

1. **Setup the enviornment**. For most networks, this entails downloading or creating any auxiliary files required for 
   network instantiation (morphology files, cell parameters, mod files, etc) and inputs (spikes, electrodes).

2. **Setup the SONATA configuration file(s)**. We use a json based SONATA configuration file to instruct BMTK how to 
   instiante a network (including location of circuits and any auxiliary files), run-time parameters, and what stimuli
   to use as input and what variables to record for our output. We can create a SONATA config file from scratch, or 
   download and edit an existing one using any prefered text-editor.

3. **Run the simulation(s)**. The majority of BMTK simulation can be fully defined in the SONATA config (although for 
   advanced users BMTK allows extensive customization using Python). Thus we just need to execute an pre-generated 
   python script with the above SONATA config file and let our simulation finish.
   
Once the simulation has completed it will automatically generate and save the results as specified in the SONATA 
configuration file. Although BMTK can run network models of different levels-of-resolutions, this is abstracted from 
the user will use the appropiate underlying simulator library, eg. **Simulation Engine**, depending on the cell models.
So no matter if the network is ran using NEURON, NEST, DiPDE, or any other engine; the expected inputs and outputs 
are the same format

.. figure:: _static/images/bmtk-workflow-v2-simulation-highlighted.png
    :scale: 60%


The rest of this guide will go through each of the above steps in detail. To help make the concepts for concrete we will
also be referencing the **example** network simulation found here. This is a biophysically detailed network containing a
400 cells with feedforward synaptic stimuli.


1. Setting up the Environment
=============================

First step is to download and/or create neccesary files required to instiate network and execute the simulation. At 
miniumum we require the SONATA circuit file(s), simulation configuration, and a BMTK run script. But depending on the 
model and simulation we may also need the following:

* template files used to build the cell or synapse models (*Hoc Templates*, *NeuroML*, *NESTML*)
* cell and synaptic dynamics attribute values,
* cell morphologies (*SWC*, *Neuralucdia*),
* simulation input and stimuli (*spike-trains*, *current wave-form*, *movie and auditory files*),
* NEURON .mod files.

We can put these files wherever we want as long as they are accessable during simulation execution. Although best 
practices is to put them inside a single directory with the following structure.

.. figure:: _static/images/bmtk_sim_env.2024.png
    :scale: 40%


BMTK includes the `create_environment <SIMSETUP>`_ tool that can help new users generate an environmental directory from scratch.
Another option we recommend, especially if running simulations on an already existing model, is to download an existing
simulation environment and make changes as necessary.



.. card::

  **example** network
  ^^^^^^^^^^^^^^^^^^^

  When creating the `BioNet example`_ we used the `build_network.py` python script to build and save the network model 
  into the **network/** sub-directory (see `BMTK Builder Guide`_ for more information on that process). With the network
  built we then used the following command to generate baseline strucutre plus `config.simulation.json` configuration and
  the `run_bionet.py` script used to execute the simulation:

  .. code:: bash

      $ python -m bmtk.utils.create_environment        \
                      --config-file config.iclamp.json  \
                      --overwrite                       \
                      --network-dir network             \
                      --output-dir output_iclamp        \
                      --tstop 3000.0                    \
                      --dt 0.1                          \
                      --report-vars v                   \
                      --iclamp 0.150,500,2000           \
                      --compile-mechanisms              \
                      bionet .
              
  This script will create the **components/** directory to place any auxiliary files for network instiation, but unless
  explicity defined, the corresponding subfolders will be empty. In particular out model's various cell-types require
  SWC morphology and dynamics parameters files that can be downloaded from the Allen Cell Types Database, renamed and 
  placed into their corresponding folders.

  .. figure:: _static/images/ctdb_screenshot.ephys_page.highlighted.png
    :scale: 40%

  For simulation input our network will be stimulated by feed-forwar pre-generated spike-trains that will save into 
  the **inputs/** folder using the `create_inputs.py` script

  .. code:: bash

    $ python create_inputs.py




2. Setting up Sonata Config file(s)
===================================

The primary interface thorugh which most users will run a simulation is through the **SONATA confiugration** file(s). 
Each simulation will have its own json config file that can be opened and modified by any text editor, allowing users
to readily adjust simulation, network, input, and output of any given simulation without any required coding or having
to learn the API for a specific simulator.

The config file is segmented into sections for the various aspects of running a full simulation. We will go into depth
of each section below.



"run"
^^^^^
The "run" section of the configuration file gives us run-time parameters for the simulation. At minimum this includes 
the **tstop** parameter that determines the time step (in ms) when the simulation will stop. Other options, including
**tstart** (time at start of simulation, ms) and **dt** (time step interval, ms), may or may not be optional or even
used depending on the simulation.


.. dropdown:: "run" simulation attributes

   .. list-table::
      :header-rows: 1

      * - name
        - description
        - required
      * - tstart
        - Start time of simulation in ms (default 0.0)
        - False
      * - tstop
        - Stop time of simulation (default 0.0)
        - True
      * - dt
        - The time step of a simulation; ms
        - True
      * - dL
        - For networks with morphological models, is a global parameter used to indicate to the simulator the maximum length 
          of each compartmental segment, in microns. If "dL" parameter is explicitly defined for a specific cell or cell-type,
          then BMTK will default to the more grainular option.
        - False
      * - spike_threshold
        - For networks using conductance based model, is a global paramter to indicate the threshold in mV at which a cell undergoes
          an action potential. Will not apply to integrate-and-fire type models. Value will be overwritten for any cell or cell-type
          that explicity defines "spike_threshold" parameter in network attribute.
        - False
      * - nsteps_block
        - Used by certain input/report modules to indicate time processing of timestep in blocks of every n time-steps. In particular
          for recording of spike-trains, membrane variables, or extraceullar potential; tells the simulation when to flush data 
          out of memory and onto the disk. 
        - False

.. card::
  
  The "run" section for our example simulation contains the following:
  
  .. code:: json
      
      "run": {
        "tstop": 3000.0,
        "dt": 0.1,
        "dL": 20.0,
        "spike_threshold": -15,
        "nsteps_block": 5000
      },

  This will tell our simulation to run for 3,000 ms (3 seconds) with 0.1 ms timesteps, block process all the data every
  5000 steps (eg. 500 ms). The "dL" makes sure that for morphologically detailed cells each branch segment is no more 
  than 20 microns in lenght. And to record a spike when a cell reaches threshold of -15.0 mV.

  


"inputs"
^^^^^^^^

The "inputs" section of the SONATA config file is used to specify stimlus to apply to the network. It will contain one or more independent stimuli blocks
of the format 

.. code:: json 

    {
        "<BLOCK_NAME>": {
            "input_type": "<STIMULI_TYPE>",
            "module": "<STIMULI_FORMAT>",
            "node_set": "<NODES_SUBSET>",
            "param1": "<VAL1>",
            "param2": "<VAL2>",
            "paramN": "value"

        }
    }

* The **<BLOCK_NAME>** is the name of the stimuli block, users can choose whatever name they want to identify a specific stimuli.
* **input_type** specifies the nature of the stimlulation, eg. if cell activity is being generated by synaptic events, current clamps, etc. The available options will depend of the resolution of the model and the type of cell models used. The options will depend on the input_type
* **module** is used to indicate the format of the stimuli. For example in trying to stimulate network with virtual spiking activity file, the individual spike times may be stored in a SONATA spikes file, a NWB file, a CSV, etc.
* **node_set** is a dictionary or reference used to select which cells to apply current stimuli to.
* Most stimuli will have one or more **parameters** options, depending on the input_type + module.


.. dropdown:: Available "input_type" stimuli

    .. list-table::
        :widths: 25 25 50 20
        :header-rows: 1

        * - input_type
          - module
          - description
          - available
        * - current_clamp
          - | IClamp
            | csv
            | nwb 
            | allen
          - Directly injects current into one or more cells in the network. Shape of stimulus may be a simple block, or user may specify more advanced current form using a csv, nwb, or hdf5 file.
          - BioNet, PointNet
        * - spikes
          - | sonata
            | csv
            | ecephys_probe 
            | function
          - Reads a table of spike train events into one or more virtual cells in the network.
          - BioNet, PointNet
        * - voltage_clamp
          - SEClamp
          - Applys a voltage clamping block onto one or more cells.
          - BioNet
        * - extracellular
          - | xstim
            | comsol
          - Provides an extracellular potential to alter the membrane comptanence of a selected set of cells in the network. Can replicate extracellular stimulation coming from an electrode (xstim) or field can pre-generated (comsol). 
          - BioNet
        * - replay
          - replay
          - Allows users "replay" the recurrent activity of a previous recorded simulation with a selected subset of cells and/or connections. Useful for when looking at summative properties of contributions in large networks. 
          - BioNet, PointNet
        * - syn_activity
          - | syn_activity
            | function
            | list
          - Provides spontaneous firing of a select subset of recurrently connected synapses. Users may pre-specify firing times or let bmtk generate them randomly.  
          - BioNet
        * - movie
          - movie
          - Plays a movie (eg a numpy matrix file) onto the receptive field of a grid of neurons to mimic LGN reaction.
          - FilterNet
        * - movie
          - | grating
            | full_field_flash
            | spontaneous
            | looming
          - Automatically generate a movie of one of a number of well-known experimental stimuli and use it to play onto the receptive field of a set of neurons.
          - FilterNet


"components"
^^^^^^^^^^^^

The "components" section is used to indicate the paths to various auxiliary files required for instantiating our simulation; like morphology 
swc files, NEURON mod files, NESTML or NeuroML cell models. BMTK will use these paths to find neccesary files required to instantiate the network
for simulation.

the different directories are defined using the format

.. code:: json 

    "components": {
        "<COMPONENT_TYPE>": "/path/to/components/dir/"
    }



.. dropdown:: Recognized "components" directories

    .. list-table::
        :widths: 25 75
        :header-rows: 1

        * - name
          - description
        * - biophysical_neuron_models_dir
          - Directory containing files for instantiation of biophysically detailed models. Typically containing json cell model files downloaded 
            from the Allen Cell-Types Database.
        * - point_neuron_models_dir
          - Directory containing files for instantiation of point-neuron models. Typically json parameter files, or with PointNet may be model
            files downloaded from the Allen Cell-Types Database to instantiate optimized "glif" models.
        * - filters_dir
          - Directory containing parameters files for instiating models used by `FilterNet <LINK REQ>`_
        * - morphologies_dir
          - Directory containing any morphological reconstruction files (ex. swc, neuralucdia).
        * - synpatic_models_dir
          - Directory containing files for specific synaptic parameters.
        * - mechanisms_dir
          - Directory containing any morphological reconstruction files (ex. swc, neuralucdia)
        * - templates_dir
          - Contains NEURON Hoc template files or NeuroML cell or synapse models.


"output" and "reports"
^^^^^^^^^^^^^^^^^^^^^^

The "outputs" section is where we define basic information about where and how to we will save any simulation results. Most importantly is the
**output_dir** attribute that defines default location of any files generated during the simulation. We also define the **spikes_file** attribute
which is the file name (relative to the **output_dir** path) where BMTK will save any non-virtual spikes generated during the simulation in a 
SONATA hdf5 formated file.

.. dropdown:: "output" attributes

    .. list-table::
        :widths: 25 50 25
        :header-rows: 1

        * - name
          - description
          - default value
        * - output_dir
          - Path of output folder where simulation results and temp files will be saved in. BMTK will create the folder if it does not already
            exists. If value is not an absolute path, then will assume to be relative to location where BMTK simulation is being executed (eg `os.getcwd()`)
          - `.`
        * - overwrite_output_dir
          - If set to True then BMTK will overwrite any previous output files stored in **output_dir**. If set to False and files exists before run time then
            BMTK may throw an error and exit simulation.
          - True
        * - log_file
          - Name of file where any BMTK messages will be written to. If the file name has a relative path then file will be saved underneath **output_dir**. 
            If value is set to `false` or `none` then no log file will be created during simulation.
          - `none`
        * - log_level
          - Level of logging information that will be included during simulation (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
          - `DEBUG`
        * - log_format
          - The format string for how BMTK will save loggnig messages. It uses the `LogRecord attributes <https://docs.python.org/3/library/logging.html#logrecord-attributes>`_ options
            set by python's logging module.
          - `%(asctime)s [%(levelname)s] %(message)s`
        * - log_to_console
          - If `true` then will also log output to default **standard ouput (stdout)**, if `false` then will disable **stdout** logging. Note: if both **log_to_console** and
            **log_file** are set to `false` then BMTK will not log any simulation messages (simulation will still run and produce results).
          - `true`
        * - quiet_simulator
          - Can be set `true` to turn off any extermporaneous messages generated by the underlying simulator (NEURON, NEST, DiPDE)
          - `false`.
        * - spikes_file
          - location of hdf5 file where spikes will be saved. If location is a relative path file will be saved under the **output_dir** directory. If set to `none` then no
            SONATA spikes file will be created during simulation.
          - `none`
        * - spikes_file_csv
          - Location of space separated csv file where spikes will be saved. If location is a relative path file will be saved under the **output_dir** directory. If set to `none` 
            then no csv spikes file will be created during simulation.
          - `none`


By default BMTK will save non-virtual spike-trains of the simulation. BMTK is also capable of saving many other cell, synapse, and even network wide parameters
and attributes during a simulation, like membrane potential, Calcium concentration, or local field potentials. To instruct BMTK to record a extra parameter we 
must add one or more blocks to the "reports" subsection to config, which will have the following format:

.. code:: json 

    {
        "<BLOCK_NAME>": {
            "module": "<REPORT_TYPE>",
            "input_type": "<REPORT_VAR>",
            "cells": "<NODES_SUBSET>",
            "file_name": "<FILE_NAME>",
            "param1": "<VAL1>",
            "param2": "<VAL1>"

        }
    }

The **<BLOCK_NAME>** is a user-given identifier for a different report, each different block assumed to be independent of each other.

* **module** is used to indicate the report type and nature.
* **variable_name** indicates the specific variable in the simulation being recorded.
* **cells** is a node-set to indicate which cells are being targeted in recording.
* **file_name** is an *optional* path for where module will save output. If path is relative then it will assume to be saved under the **output_dir** 
  path specified in "output" block. If not specified, then BMTK will attempt to infer the correct path (usually under **ouput_dir/<BLOCK_NAME>.h5**

Different modules may also have different required/optional parameters. The following is a list of BMTK supported "report" modules:


.. dropdown:: Available "report" modules

    .. list-table::
        :widths: 25 50 20
        :header-rows: 1

        * - module
          - description
          - available
        * - membrane_report
          - Used to record a contingous time trace of a cell ion or parameter, like membrane voltage or calcium concentration
          - BioNet, PointNet
        * - syn_report
          - Used to record a contingous time trace of variables for the synapses of a given set of cells
          - BioNet, PointNet
        * - syn_weight
          - Record of synaptic weight changes for a given set of cells. 
          - BioNet, PointNet
        * - extracellular
          - Used to record a contingous time trace of variables for the synapses of a given set of cells
          - BioNet


"networks"
^^^^^^^^^^

The "networks" section contains path to any SONATA network files, cells and connections, used during our simulation. By default it is divided into two 
subsection, one containing any nodes (cells) files used during the simulation, and the other containing and edges (synapses) files used, with the following
format:

.. code:: json 

    "networks": {
        "nodes": [
            {
                "nodes_file": "</path/to/nodes.h5>",
                "node_types_file": "</path/to/node_types.h5>"
            }
        ],
        "edges": [
            {
                "edges_file": "</path/to/edges.h5>",
                "edge_types_file": "</path/to/edge_types.h5>"
            }
        ]
    }

BMTK will go through each nodes.h5 and edges.h5 file and import all nodes and edges population found, respectively (If a file contains both nodes and edges populations
then said file must be added to the "nodes" list and the "edges" list to include the total network.



Executing the Simulation
========================




******************
Simulation Engines
******************



**************
Further Guides
**************



Starting Guides and Tutorials
=============================


.. grid:: 1 1 4 4
    :gutter: 1

    .. grid-item-card::  Simple Single Cell Biophysical Simulations will BioNet
        :link: builder_guide 
        :img-bottom: _static/images/ch2_simple_edge_swc_c_micron_scale__source_swc_red_target_swc_red.png

        *BioNet* 


    .. grid-item-card:: Complex Multi-cell, Cross Model Simulations
        :link: simulators_guide.rst
        :img-bottom: _static/images/l4-morpho-lifs-soma-tach.png

        *BioNet* 

       
    .. grid-item-card:: Large-scale simulation with Point-neuron LIF cells
        :link: analzer
        :img-bottom: _static/images/pointnet_figure.png

        *PointNet*

    .. grid-item-card:: Population-based firing rate model simulations
        :link: analzer
        :img-bottom: _static/images/dipde_figure.png

        *PopNet*


    .. grid-item-card:: Generating feedforward stimuli from Images and Movies
        :link: analzer
        :img-bottom: _static/images/lnp_model.jpg

        *FilterNet*

    .. grid-item-card:: Generating feedforward stimuli from Sound files
        :link: analzer
        :img-bottom: _static/images/spectrogram.jpeg

        *Auditory FilterNet*


Simulation Engines Key Concepts
===============================

.. grid:: 1 1 4 4
    :gutter: 1

    .. grid-item-card::  BioNet: Core Conecpts
        :link: builder_guide 


    .. grid-item-card::  BioNet: Core Conecpts
        :link: builder_guide 


    .. grid-item-card::  FilterNet: Core Conecpts
        :link: builder_guide 


Simulation Stimuli and Inputs
=============================

.. grid:: 1 1 4 4
    :gutter: 1

    .. grid-item-card::  Generating Custom spike inputs for simulation stimulus
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card::  Loading Spikes from NWB 2.0 Files into BMTK simulations
        :link: builder_guide 
        
        *Something here*


    .. grid-item-card::  Using Allen Cell-Types database trials in a simulation
        :link: builder_guide 

        *Something here*


    .. grid-item-card::  Custom generated spike trains
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Advanced Options for Current clamp wave-forms in BioNet and PointNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Replaying recurrent activity in BioNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Generating Spontaneous Synaptic Activity in BioNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Using Movies in FilterNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Autogenerated Movies in FilterNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Auditory Stimuli for FilterNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Auditory Stimuli for FilterNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Extracellular Stimulation of Networks in BioNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Importing Experimental Sweep data from the Allen Cell-Types Database
        :link: builder_guide 
        
        *Something here*



Simulation Variables and Reports
================================

.. grid:: 1 1 4 4
    :gutter: 1

    .. grid-item-card::  Recording Local Field Potentials and Current Source Densities in BioNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card::  Recording Synaptic weights and properties
        :link: builder_guide 
        
        *Something here*


    .. grid-item-card::  Membrane-Recording in BioNet
        :link: builder_guide 

        *Something here*


    .. grid-item-card::  Membrane-Recording in PointNet
        :link: builder_guide 
        
        *Something here*


Running and Computing
=====================

.. grid:: 1 1 4 4
    :gutter: 1

    .. grid-item-card::  Optimization Techniques in FilterNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card::  Help with installing and running BioNet and PointNet on HPC
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card::  Running BMTK on Neuroscience Gateway (NSG)
        :link: builder_guide 
        
        *Something here*


Custom and Imported Models
==========================

.. grid:: 1 1 4 4
    :gutter: 1

    .. grid-item-card::  Importing ModelDB and OpenSourceBrain cell models into BioNet simulations.
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card::  Building your own cell models in BioNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card::  Importing custom membrane mechanics into your models for BioNet
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card::  Dynamically modfying cell properties before and during simulation.
        :link: builder_guide 
        
        *Something here*

    .. grid-item-card:: Creating and importing custom models using NESTML for PointNet
        :link: builder_guide 
        
        *Something here*


Advanced Programming Options
============================

.. grid:: 1 1 4 4
    :gutter: 1

    .. grid-item-card:: Creating Customized Modules
        :link: builder_guide 
        
        *Something here*