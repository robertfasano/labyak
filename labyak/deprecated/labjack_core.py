''' Base LabJack class implementing device connection and communication. '''
from labjack import ljm

class LabJack():
    def __init__(self, device='ANY', connection='ANY', devid='ANY'):
        try:
            self.handle = ljm.openS(device,
                                    connection,
                                    devid)
            info = ljm.getHandleInfo(self.handle)

            self.deviceType = info[0]
            assert self.deviceType in [ljm.constants.dtT7, ljm.constants.dtT4]

            print('Connected to LabJack (%i).'%(info[2]))
        except Exception as e:
            print('Failed to connect to LabJack (%s): %s.'%(devid, e))

    def _query(self, register):
        ''' Reads the specified register. '''
        return ljm.eReadName(self.handle, register)

    def _command(self, register, value):
        ''' Writes a value to a specified register.

            Args:
                register (str): a Modbus register on the LabJack.
                value: the value to write to the register.
                '''
        ljm.eWriteName(self.handle, register, value)

    def _write(**kwargs):
        ''' Updates registers according to the passed keyword arguments. For
            example, to set DAC0 to 1 and DAC1 to 0 we would call
                self._write(DAC0=1, DAC1=0)
        '''
        self._write_array(list(kwargs.keys()), list(kwargs.values()))
        
    def _write_array(self, registers, values):
        ljm.eWriteNames(self.handle, len(registers), registers, values)

    def _write_dict(self, d):
        ''' Writes values to registers according to the passed dictionary. '''
        self._write_array(list(d.keys()), list(d.values()))

    def stop(self):
        ''' Stop streaming if currently running '''
        try:
            ljm.eStreamStop(self.handle)
        except:
            pass

    def PWM(self, channel, frequency, duty_cycle):
        ''' Starts pulse width modulation on an FIO channel.

            Args:
                channel (int): FIO channel to use (0 or 2-5).
                frequency (float): desired frequency in Hz
                duty_cycle (float): duty cycle between 0 and 100.
        '''
        try:
            roll_value = self.clock / frequency

            config = {
                "DIO_EF_CLOCK0_ENABLE": 0,
                "DIO_EF_CLOCK0_DIVISOR": 1,
                "DIO_EF_CLOCK0_ROLL_VALUE": roll_value,
                "DIO_EF_CLOCK0_ENABLE": 1,
                "DIO%i_EF_ENABLE"%channel: 0,
                "DIO%i_EF_INDEX"%channel: 0,
                "DIO%i_EF_OPTIONS"%channel: 0,
                "DIO%i_EF_CONFIG_A"%channel: duty_cycle * roll_value / 100,
                "DIO%i_EF_ENABLE"%channel: 1
            }
            self._write_dict(config)

        except Exception as e:
            print(e)

    def PWM_stop(self, channel):
        self._command("DIO%i_EF_ENABLE"%channel, 0)

if __name__ == '__main__':
    lj = LabJack(devid='470018953')
