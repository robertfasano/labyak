from labjack import ljm
import numpy as np

class Digital():
    ''' Handles digital subsystems of the LabJack T-series device family, covering
        digital in/out, simultaneous DIO_STATE updates, and streaming.
    '''
    def __init__(self, labjack):
        self.labjack = labjack

    def DIn(self, channel):
        return int(self.labjack._query('DIO{}'.format(channel)))

    def DOut(self, channel, state):
        ''' Output a digital signal.

            Args:
                channel (str): a digital channel on the LabJack, e.g. 'FIO4'.
                state (int): 1 or 0
        '''
        if type(channel) is int:
            channel = 'DIO%i'%channel
        self.labjack._command(channel, state)

    def DIO_STATE(self, channels, states):
        ''' Set multiple digital channels simultaneously. '''
        state = 0
        for i in range(len(channels)):
            state = state | (states[i] << channels[i])

        bitmask = self.bitmask(channels)
        self.labjack._write_dict({'DIO_INHIBIT': 0x7FFFFF-bitmask,
                                  'DIO_DIRECTION': bitmask,
                                  'DIO_STATE': state})

    @staticmethod
    def inhibit_string(channels):
        inhibit = ''
        for i in range(23):
            if 23-i-1 in channels:
                inhibit += '0'
            else:
                inhibit += '1'
        return inhibit

    @staticmethod
    def array_to_bitmask(arr, channels):
        ''' Convert multidimensional array with one column for each channel to an array of bitmasks. '''
        y = np.zeros(len(arr))

        inhibit = 0x7FFFFF-Digital.bitmask(channels)
        inhibit_string = Digital.inhibit_string(channels)
        for i in range(len(arr)):
            states = arr[i,:]
            bitmask = Digital.state(channels, states)
            lower_bits = format(bitmask, '#010b')
            y[i] = int(inhibit_string[-8:]+lower_bits[2:], 2)
        return y

    @staticmethod
    def bitmask(channels):
        bm = 0
        for ch in channels:
            bm |= 1 << ch
        return bm

    @staticmethod
    def state(channels, states):
        ''' Returns a bitmask representation of the passed channels and states. '''
        bitmask = 0
        for j in range(len(channels)):
            bitmask = bitmask | (int(states[j]) << channels[j])

        return bitmask
