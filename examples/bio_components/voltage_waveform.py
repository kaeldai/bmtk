import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

class CreateVoltageWaveform:
    '''
    Class to create a voltage waveform and write it to a csv file for the bionet xstim simulation.
    Running "CreateVoltageWaveform()" in run_bionet.py will run __init__()
    '''

    def __init__(self, current_amplitude=10, timestep=10, writing=True, plotting=False):
        '''
        This is the main function you run when you call CreateVoltageWaveform() from another file.
        All necessary functions for creating the waveform, sampling it, and writing it to a .csv-file are called down here,
        so no other function calls are needed in the other file.
        :param current_amplitude: amplitude of the current in uA. By default 10uA.
        :param timestep: sampling timestep of the simulation. By default 10us. If e.g. set at 100us, time variables such as the pulsewidth change from 200 (us) to 2.
        :param writing: determines whether you write the waveform values to the csv file. By default it is set to True.
        :param plotting: determines whether you also plot the waveform shape. By default it is set to False, so the waveform
        is not plotted each time you run the simulation.
        '''
        self.current_amplitude = current_amplitude
        self.timestep = timestep
        # Stimulation parameters (can be changed but these are the real ones used in the experiments)
        self.period = int(5000/timestep) # 200 Hz stimulation frequency = every 5 ms = 4600us after previous pulse
        self.pulsewidth = int(200/timestep)

        # Create arrays for the timing
        self.time = np.linspace(0, self.period-1, self.period, dtype=int)
        self.amplitude = np.zeros(self.period)
        print(self.time)
        # Create a pulse train
        for t in self.time:
            C = 200E-10 # 200nF
            R = 10E3   # 10kohm
            V0 = R * self.current_amplitude * 1E-6 #   V
            if t < self.pulsewidth:
                self.amplitude[t] = -V0*(1-np.exp(-t*self.timestep*1E-6/(R*C))) - V0
            elif t < 2*self.pulsewidth:
                self.amplitude[t] = V0*(1-np.exp(-(t-self.pulsewidth)*self.timestep*1E-6/(R*C))) + V0
            else: 
                self.amplitude[t] = (-V0*(1-np.exp(-(t-2*self.pulsewidth)*self.timestep*1E-6/(R*C))) + V0)*np.exp(-(t-2*self.pulsewidth)*self.timestep*1E-6/(R*C))

        # If writing is set to true (default), write_to_csv() will be called
        # print(self.time)
        if writing == True:
            self.write_to_csv()

        # If plotting is set to true, plot_waveform() function will be called	
        if plotting == True:
            self.plot_waveform()

        return

    def make_function(self,t):
        '''
        Describe the relationship between voltage amplitude and time.
        '''
        # TO DO: change the underlying function to the correct voltage function
        #v = self.current_amplitude*t
        # parameters:
        C = 200E-10 # 200nF
        R = 10E3   # 10kohm
        V0 = R * self.current_amplitude * 1E-6 #   V
        # v = V0(1-exp(-t/RC))
        v = np.array([])
        for time in t:
            v = np.append(v, V0*(1-np.exp(-time*self.timestep*1E-6/(R*C))) + V0) # (Vc+Vr)
            # v = np.append(v, V0*(1-np.exp(-time*1E-6/(R*C)))*1E3)   # mV
            # v = np.append(v, V0*(1-np.exp(-time*1E-6/(R*C))))   # V
            # v = np.append(v, V0)
        np.append
             
        # Make sure that the first and last values are 0, otherwise there might be problems with full waveform later
        v[0] = 0
        v[-1] = 0
        # print(v)
        return v

    def sample_waveform(self,phase='anodic'):
        '''
        Give the discrete list self.time to the function to receive the corresponding amplitude values.
        '''
        if phase=='cathodic':
            return -1*self.make_function(self.time)
        else:
            return self.make_function(self.time)

    def write_to_csv(self):
        '''
        Take the self.time and self.time amplitude lists and write them to the correct csv-file.
        '''

        # TO DO: change path and name
        # path = './' # 'path/to/csv/file'
        #name = 'waveform_custom.csv'

        path = ('../bio_components/stimulations')
        name = 'waveform.csv'

        # Write the time and amplitude lists to the csv-file
        df = pd.DataFrame({'time': self.time, 'amplitude': self.amplitude})
        df.to_csv(os.path.join(path,name), sep='\t', index=False)
        return

    def plot_waveform(self):
        plt.plot(np.array([self.time, self.time+max(self.time)]).flatten(), np.array([self.amplitude,self.amplitude]).flatten())
        plt.title("xpto")
        # plt.xlim([0, 2*self.pulsewidth]) # Optional, to focus on 1 pulse only
        plt.show()
        return

if __name__ == '__main__':
    '''
    If you run the file voltage_waveform.py instead of calling if from another file, this part will run.
    Can be used to optimize the waveform without each time writing values to the csv-file and calling the simulation.
    '''
    waveform = CreateVoltageWaveform(timestep=25, current_amplitude=64, writing=True, plotting=True)
