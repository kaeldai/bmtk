# Comsol

A small network of 200 multi-compartment biophysically detailed cells placed in a column with radius 200 $\mu m$ and height 400 $\mu m$. 
The network receives input in the form of a time-dependent potential distribution defined by a .txt file that is exported from COMSOL. 

Uses the BioNet simulator (requires NEURON)

## Running:

```
$ python run_bionet.py config_comsol.json
```
If successful, will create a *output* directory containing log, spike trains and recorded cell variables.

## The Network:
The network files have already been built and stored as SONATA files in the *network/* directory. The bmtk Builder
script used to create the network files is *build_network.py*. To adjust the parameters and/or topology of the network
change this file and run:
```
$ python build_network.py
```
This will overwrite the existing files in the network directory. Note that there is some randomness in how the network
is built, so expect (slightly) different simulation results everytime the network is rebuilt.

## Simulation Parameters
Parameters to run the simulation, including run-time, inputs, recorded variables, and networks are stored in config_comsol.json and config_network.json and can modified with a text editor.

The COMSOL file path can be specified in config_comsol.json

```json
  "inputs": {
    "Extracellular_Stim": {
      "input_type": "lfp",
      "node_set": "all",
      "module": "comsol",
      "comsol_file": "$STIM_DIR/COMSOL.txt"
    }
```
