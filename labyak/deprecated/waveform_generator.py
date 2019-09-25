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
            self._write_dict({f'STREAM_OUT{i}_TARGET': 1000+2*channels[i],
                              f'STREAM_OUT{i}_BUFFER_SIZE': buffer_size,
                              f'STREAM_OUT{i}_ENABLE': 1
                            })

            target = ['STREAM_OUT%i_BUFFER_F32'%i] * len(data)
            self._write_array(target, list(data))

            self._write_dict({f'STREAM_OUT{i}_LOOP_SIZE': loop*len(data),
                              f'STREAM_OUT{i}_SET_LOOP': 1
                            })
            self.aScanList.append(4800+i)           # add stream-out register to scan list

        scanRate = ljm.eStreamStart(self.handle, 1, len(self.aScanList), self.aScanList, scanRate)

    def prepare_stream(self, channels):
        self.stop()

        ''' Set stream parameters '''
        self.aScanList = []
        self._write_dict({'STREAM_SETTLING_US': 0,
                          'STREAM_RESOLUTION_INDEX': 0,
                          'STREAM_CLOCK_SOURCE': 0
                        })

    def prepare_stream_trigger(self, ch):
        if ch is None:
            self._command("STREAM_TRIGGER_INDEX", 0) # disable triggered stream
        else:
            self._write_dict({f"DIO{ch}_EF_ENABLE": 0,
                              f"DIO{ch}_EF_INDEX": 3,
                              f"DIO{ch}_EF_OPTIONS": 0,
                              f"DIO{ch}_EF_VALUE_A": 2,
                              f"DIO{ch}_EF_ENABLE": 1,
                              "STREAM_TRIGGER_INDEX": 2000+ch
                              })
            ljm.writeLibraryConfigS('LJM_STREAM_RECEIVE_TIMEOUT_MS',0)  #disable timeout

    def optimize_stream(self, array, period, max_samples = 8191):
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
