''' Base LabJack class implementing device connection and communication. '''
from labjack import ljm
from labyak import Analog, Digital, Temperature, PWM, SPI, I2C, Stream, WaveformGenerator, PatternGenerator, ADCStream

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

        ## load submodules
        self.analog = Analog(self)
        self.digital = Digital(self)
        self.temperature = Temperature(self)
        self.pwm = PWM(self)
        self.spi = SPI(self)
        self.i2c = I2C(self)
        self.stream = Stream(self)
        self.waveform = WaveformGenerator(self)
        self.pattern = PatternGenerator(self)
        self.adc_stream = ADCStream(self)

    def _query(self, register):
        ''' Reads the specified register. '''
        return ljm.eReadName(self.handle, register)

    def _read_array(self, register, num_bytes):
        return ljm.eReadNameByteArray(self.handle, "I2C_DATA_RX", read_bytes)

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

if __name__ == '__main__':
    lj = LabJack(devid='470018953')
