# -*- coding: utf-8 -*-
from labjack import ljm

class I2C:
    def __init__(self, labjack):
        self.labjack = labjack

    def initialize(self, sda=13, scl=12, speed=65516, options=2):
        ''' Set up I2C on a pair of FIO channels.
            Args:
                SCL, SDA (int): channel numbers of the FIO channels
                speed (int): throttle speed, inversely proportional to clock frequency
                options (int): bits implementing optional features:
                                bit 0: reset the I2C bus
                                bit 1: restart without stopping
                                bit 2: disable clock stretching
        '''
        self.labjack._write_dict({'I2C_SDA_DIONUM': sda,
                                  'I2C_SCL_DIONUM': scl,
                                  'I2C_SPEED_THROTTLE': speed,
                                  'I2C_OPTIONS': options})

    def read(self, addr, reg, read_bytes):
        # Set the TX bytes. We are sending 1 byte for the address.
        buffer = [reg]
        self.labjack._write_dict({'I2C_SLAVE_ADDRESS': addr,
                                  'I2C_NUM_BYTES_TX': len(buffer),
                                  'I2C_NUM_BYTES_RX': read_bytes,
                                  })
        self.labjack._write_array('I2C_DATA_TX', buffer)
        self.labjack._write('I2C_GO', 1)

        return self.labjack._read_array('I2C_DATA_RX', read_bytes)

    def write(self, addr, reg, data):
        buffer = [reg]
        buffer.extend(data)
        self.labjack._write_dict({'I2C_SLAVE_ADDRESS': addr,
                                  'I2C_NUM_BYTES_TX': len(buffer),
                                  'I2C_NUM_BYTES_RX': 0,
                                  })
        self.labjack._write_array('I2C_DATA_TX', buffer)
        self.labjack._write('I2C_GO', 1)

    def check(self, addr):
        ''' Query whether the target addr is an I2C channel '''
        self.labjack._write_dict({'I2C_SLAVE_ADDRESS': addr,
                                  'I2C_NUM_BYTES_TX': 0,
                                  'I2C_NUM_BYTES_RX': 0,
                                  })
        return self.labjack._query('I2C_ACKS') == 1
