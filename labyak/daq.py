from labjack import ljm
import numpy as np
from labyak import LabJack

class LabDAQ(LabJack):
    def __init__(self, device='ANY', connection='ANY', devid='ANY'):
        super().__init__(device=device, connection=connection, devid=devid)

    ''' Analog I/O '''
    def AIn(self, channel):
        ''' Read a channel and return the voltage. '''
        return self._query('AIN{}'.format(channel))

    def AOut(self, channel, value, TDAC=False):
        ''' Output an analog voltage.

            Args:
                channel (int): number of the target DAC channel.
                value (float): Voltage in volts.
                TDAC (bool): If False, use a DAC channel (0-5 V); if True, use a TDAC channel with the LJTick-DAC accessory (+/-10 V).
        '''
        if not TDAC:
            self._command('%s%i'%('DAC', channel), value)
        else:
            self._command("TDAC%i"%channel, value)

    ''' Digital I/O '''
    def DIn(self, channel):
        return self._query('DIO{}'.format(channel))

    def DOut(self, channel, state):
        ''' Output a digital signal.

            Args:
                channel (str): a digital channel on the LabJack, e.g. 'FIO4'.
                state (int): 1 or 0
        '''
        if type(channel) is int:
            channel = 'DIO%i'%channel
        self._command(channel, state)

    def DIO_STATE(self, channels, states):
        ''' Set multiple digital channels simultaneously. '''
        # prepare inhibit array
        inhibit = ''
        for i in range(23):
            if 23-i-1 in channels:
                inhibit += '0'
            else:
                inhibit += '1'
        inhibit = int(inhibit, 2)
        self._command('DIO_INHIBIT', inhibit)

        # set direction
        bitmask = 0
        for ch in channels:
            bitmask = bitmask | 1 << ch
        self._command('DIO_DIRECTION', bitmask)

        # prepare state array
        bitmask = 0
        for i in range(len(channels)):
            bitmask = bitmask | (states[i] << channels[i])
        self._command('DIO_STATE', bitmask)

if __name__ == '__main__':
    daq = LabDAQ(devid='470018954')
