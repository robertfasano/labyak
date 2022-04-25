class PWM:
    def __init__(self, labjack):
        self.labjack = labjack

    def start(self, channel, frequency, duty_cycle):
        ''' Starts pulse width modulation on an FIO channel.

            Args:
                channel (int): FIO channel to use (0 or 2-5).
                frequency (float): desired frequency in Hz
                duty_cycle (float): duty cycle between 0 and 1.
        '''
        roll_value = 80e6 / frequency
        config = {
            "DIO_EF_CLOCK0_ENABLE": 0,
            "DIO_EF_CLOCK0_DIVISOR": 1,
            "DIO_EF_CLOCK0_ROLL_VALUE": roll_value,
        }
        self.labjack._write_dict(config)

        config = {
            "DIO_EF_CLOCK0_ENABLE": 1,
            "DIO%i_EF_ENABLE"%channel: 0,
            "DIO%i_EF_INDEX"%channel: 0,
            "DIO%i_EF_OPTIONS"%channel: 0,
            "DIO%i_EF_CONFIG_A"%channel: duty_cycle * roll_value,
        }
        self.labjack._write_dict(config)

        config = {
            "DIO%i_EF_ENABLE"%channel: 1
        }
        self.labjack._write_dict(config)

    def stop(self, channel):
        self._command("DIO%i_EF_ENABLE"%channel, 0)
