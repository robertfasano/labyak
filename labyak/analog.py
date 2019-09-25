class Analog():
    def __init__(self, labjack):
        self.labjack = labjack

    def AIn(self, channel):
        ''' Read a channel and return the voltage. '''
        return self.labjack._query('AIN{}'.format(channel))

    def AOut(self, channel, value):
        ''' Output an analog voltage.

            Args:
                channel (int): number of the target DAC channel.
                value (float): Voltage in volts.
        '''
        self.labjack._command('%s%i'%('DAC', channel), value)

    def TDAC(self, channel, value):
        ''' Output an analog voltage.

            Args:
                channel (int): number of the target TDAC channel.
                value (float): Voltage in volts.
                TDAC (bool): If False, use a DAC channel (0-5 V); if True, use a TDAC channel with the LJTick-DAC accessory (+/-10 V).
        '''
        self.labjack._command("TDAC%i"%channel, value)
