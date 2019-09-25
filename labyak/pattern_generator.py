''' Digital pattern generator based on the LabJack T7. Output on up to 8 TTL
    channels with periods as short as 80 us/12.5 kHz. Faster speeds (up to 100 kHz
    for a single channel) could be achieved by writing to specific DIO registers
    rather than the shared FIO_STATE register. '''
from labjack import ljm
import numpy as np

class PatternGenerator:
    def __init__(self, labjack):
        self.labjack = labjack

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
        if self.labjack.deviceType == ljm.constants.dtT7:
            max_speed = 100000
        elif self.labjack.deviceType == ljm.constants.dtT4:
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

    def start(self, sequence, period):
        data, scanRate = self.optimize_stream(sequence, period)
        data = self.labjack.digital.array_to_bitmask(data, list(sequence.keys()))
        self.labjack.stream.configure()
        self.labjack.stream.set_inhibit(list(sequence.keys()))
        self.labjack.stream.DOut(data, scanRate, loop=1)
