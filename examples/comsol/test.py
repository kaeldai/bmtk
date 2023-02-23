import pandas as pd 
import numpy as np

comsol_file = "C:\\Users\\nilsv\\bmtk\\examples\\bio_components\\stimulations\\COMSOL.txt"

dt = 0.01
header = pd.read_csv(comsol_file, sep="\s{3,}", header=None, skiprows=8, nrows=1, engine='python').to_numpy()[0]
header[0] = header[0][2:]
for i,col in enumerate(header):
    if col[0] == "V":
        header[i] = float(col[10:])
timepoints = np.array(header[3:], dtype=float)

print(np.arange(timepoints[0], timepoints[-1]+dt, dt))

df = pd.read_csv(comsol_file, sep="\s+", header=None, skiprows=9, names=header)

tsteps = np.arange(timepoints[0], timepoints[-1]+dt, dt)

arr = np.zeros((df.shape[0],len(tsteps)))

NN = np.random.randint(0,100,100)

for i in range(df.shape[0]):
    arr[i,:] = np.interp(tsteps, timepoints, df.iloc[i,3:])

print(arr[NN,1])
print(df.shape[0])