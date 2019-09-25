class Temperature:
    def __init__(self, labjack):
        self.labjack = labjack

    def configure(self, pos_ch, neg_ch, kind, arange=0.05):
        ''' Enables temperature sensing on a given channel pair for kind = 'J' or
            kind = 'K' thermocouples.  '''
        kind = {'J': 21, 'K': 22}[kind]
        self.labjack._command(f'AIN{pos_ch}_EF_INDEX', kind)
        self.labjack._write_dict({f'AIN{pos_ch}_EF_INDEX': kind,
                                  f'AIN{pos_ch}_EF_CONFIG_B': 60052,
                                  f'AIN{pos_ch}_EF_CONFIG_D': 1,
                                  f'AIN{pos_ch}_EF_CONFIG_E': 0,
                                  f'AIN{pos_ch}_NEGATIVE_CH': neg_ch,
                                  f'AIN{pos_ch}_RANGE': arange
                                  })

    def TIn(self, ch):
        ''' Returns the temperature of a given channel in degC. '''
        return self.labjack._query(f'AIN{ch}_EF_READ_A') - 273.15
