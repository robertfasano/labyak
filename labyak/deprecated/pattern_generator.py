''' Digital pattern generator based on the LabJack T7. Output on up to 8 TTL
    channels with periods as short as 80 us/12.5 kHz. Faster speeds (up to 100 kHz
    for a single channel) could be achieved by writing to specific DIO registers
    rather than the shared FIO_STATE register. '''
from labjack import ljm
import numpy as np
from labyak import LabJack

class PatternGenerator(LabJack):
    def __init__(self, device='ANY', connection='ANY', devid='ANY'):
        super().__init__(device=device, connection=connection, devid=devid)

    def array_to_bitmask(self, arr, channels):
        ''' Convert multidimensional array with one column for each channel to an array of bitmasks. '''
        y = np.zeros(len(arr))
        ## prepare inhibit string
        inhibit = ''
        for i in range(23):
            inhibit += str(int(23-i-1 not in channels))

        for i in range(len(arr)):
            states = arr[i,:]
            bitmask = 0
            for j in range(len(channels)):
                bitmask = bitmask | (int(states[j]) << channels[j])
            lower_bits = format(bitmask, '#010b')
            y[i] = int(inhibit[-8:]+lower_bits[2:], 2)
        return y

    def stream_out(self, data, scanRate, loop = 0):
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
        self._write_dict({"STREAM_OUT0_TARGET": 2500,
                          "STREAM_OUT0_BUFFER_SIZE": buffer_size,
                          "STREAM_OUT0_ENABLE": 1,
                          "STREAM_OUT0_LOOP_SIZE": loop*len(data),
                          "STREAM_OUT0_SET_LOOP": 1
                          })

        data_register = ['STREAM_OUT0_BUFFER_U16']*len(data)
        self._write_array(data_register, list(data))

        # self._write_dict({"STREAM_OUT0_LOOP_SIZE": loop*len(data),
        #                   "STREAM_OUT0_SET_LOOP": 1
        #                   })

        scanRate = ljm.eStreamStart(self.handle, 1, 1, [4800], scanRate)

    def prepare_stream(self, channels):
        self.stop()

        ''' Set stream parameters '''
        inhibit = ''
        for i in range(23):
            inhibit += str(int(23-i-1 not in channels))

        bitmask = 0
        for ch in channels:
            bitmask = bitmask | 1 << ch

        self._write_dict({'DIO_INHIBIT': inhibit,
                          'DIO_DIRECTION': bitmask,
                          'STREAM_SETTLING_US': 0,
                          'STREAM_RESOLUTION_INDEX': 0,
                          'STREAM_CLOCK_SOURCE': 0
                          })

    def optimize_stream(self, sequence, period, max_samples = 8191):
        ''' Converts a sequence to a stream. The LabJack has two limitations:
            a maximum stream rate of 100 kS/s and a maximum sample count of
            2^13-1. This method computes a cutoff period based on these two
            restrictions; above the cutoff, the speed will be lowered to accommodate
            longer sequences with equal numbers of samples, while below the cutoff,
            the number of samples will be lowered while the speed is kept at max.

            Args:
                sequence (dict)
                period (float): The total sequence duration.

            Returns:
                stream (array): A list of points which will be output at the calculated sampling rate.
                speed (float): Stream rate in samples/second.
        '''
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

        ''' Resample to array format '''
        stream = np.zeros((int(samples), len(sequence)))
        j=0
        for channel in sequence:
            for point in sequence[channel]:
                t = point[0]
                V = point[1]
                stream[int(t/period*samples)::, j] = V
            j += 1
        return stream, scanRate

    def run(self, sequence, period):
        print('Resampling to optimal scan rate')
        data, scanRate = self.optimize_stream(sequence, period)
        print('Converting to bitmask array')
        data = self.array_to_bitmask(data, list(sequence.keys()))
        print('Preparing stream')
        self.prepare_stream(list(sequence.keys()))
        print('Starting stream')
        self.stream_out(data, scanRate, loop=1)

if __name__ == '__main__':
    p = PatternGenerator(devid='470018954')
    period=1e-2
    # sequence = {0: [(0,0), (period/2,1)], 1: [(0,0), (period/2,1)]}
    sequence = {3: [(0,0), (period/2,1)]}

    p.run(sequence, period)
