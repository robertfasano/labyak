from labjack import ljm
import numpy as np
from scipy.signal import resample
from labyak import LabJack

class WaveformGenerator(LabJack):
    ''' Digital pattern generator based on the LabJack T7 '''
    def __init__(self, device='ANY', connection='ANY', devid='ANY'):
        super().__init__(device=device, connection=connection, devid=devid)

    def stream_out(self, channels, data, scanRate, loop = 0):
        ''' Streams data at a given scan rate.

            Args:
                channels (list): Output channels to stream on, e.g. ['DAC0', 'DAC1']
                data (array): Data to stream out. For streaming on multiple channels, use column 0 for DAC0 and column 1 for DAC1.
                scanRate (float): desired output rate in scans/s
                loop (int): number of values from the end of the buffer to loop after finishing stream
        '''

        self.stop()
        n = np.ceil(np.log10(2*(1+len(data)))/np.log10(2))
        buffer_size = 2**n

        for i in range(len(channels)):
            aNames =["STREAM_OUT%i_TARGET"%i,
                     "STREAM_OUT%i_BUFFER_SIZE"%i,
                     "STREAM_OUT%i_ENABLE"%i]
            ch = channels[i]
            target = 1000+2*ch
            aValues = [target, buffer_size, 1]
            self._write_array(aNames, aValues)
            target = ['STREAM_OUT%i_BUFFER_F32'%i] * len(data)
            self._write_array(target, list(data))
            aNames = ["STREAM_OUT%i_LOOP_SIZE"%i,
                           "STREAM_OUT%i_SET_LOOP"%i]
            aValues = [loop*len(data), 1]
            self._write_array(aNames, aValues)
            self.aScanList.append(4800+i)           # add stream-out register to scan list

        scanRate = ljm.eStreamStart(self.handle, 1, len(self.aScanList), self.aScanList, scanRate)

    def prepare_stream(self, channels):
        self.stop()

        ''' Set stream parameters '''
        self.aScanList = []
        aNames = ['STREAM_SETTLING_US', 'STREAM_RESOLUTION_INDEX', 'STREAM_CLOCK_SOURCE']
        aValues = [0, 0, 0]
        self._write_array(aNames, aValues)

        # for channel in channels:
        #     self.aScanList.extend(ljm.namesToAddresses(1, [channel])[0])

    def prepare_stream_trigger(self, trigger):
        if trigger is None:
            self._command("STREAM_TRIGGER_INDEX", 0) # disable triggered stream
            aNames = ['STREAM_TRIGGER_INDEX']
            aValues = [0]
        else:
            channel = 'DIO%i'%trigger
            aNames = ["%s_EF_ENABLE"%channel, "%s_EF_INDEX"%channel,
                      "%s_EF_OPTIONS"%channel, "%s_EF_VALUE_A"%channel,
                      "%s_EF_ENABLE"%channel, 'STREAM_TRIGGER_INDEX']
            aValues = [0, 3, 0, 2, 1, 2000+trigger]
            ljm.writeLibraryConfigS('LJM_STREAM_RECEIVE_TIMEOUT_MS',0)  #disable timeout
        self._write_array(aNames, aValues)

    def optimize_stream(self, array, period, max_samples = None):
        buffer_size = 2**14
        if max_samples is None:
            max_samples = int(buffer_size/2)-1

        ''' Compute optimum scan rate and number of samples '''
        if self.deviceType == ljm.constants.dtT7:
            max_speed = 100000
        elif self.deviceType == ljm.constants.dtT4:
            max_speed = 40000

        cutoff = max_samples / max_speed
        if period >= cutoff:
            samples = max_samples
            scanRate = int(samples/period)
        else:
            scanRate = max_speed
            samples = int(period*scanRate)

        stream = resample(array, samples)
        return stream, scanRate

    def start(self, t, V, channels = ['DAC0']):
        print('Resampling to optimal scan rate')
        data, scanRate = self.optimize_stream(V, np.max(t))
        print('Preparing stream')
        self.prepare_stream(channels)
        self.prepare_stream_trigger(None)

        print('Starting stream')
        self.stream_out([int(x[-1]) for x in channels], data, scanRate, loop=1)

if __name__ == '__main__':
    p = WaveformGenerator(devid='470018954')
    f = 5e3
    t = np.linspace(0, 1/f, 300)
    V = 2.5*(1+np.sin(2*np.pi*f*t))
    p.start(t, V)
