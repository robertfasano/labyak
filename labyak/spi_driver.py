''' Digital communications module featuring SPI capabilities. '''
from labjack import ljm
import numpy as np
from labyak import LabJack

class SPIDriver(LabJack):
    def __init__(self, device='ANY', connection='ANY', devid='ANY'):
        super().__init__(device=device, connection=connection, devid=devid)
        self.initialize()

    def initialize(self, mode = 3, CLK=0, CS=1,MOSI=2, MISO=3):
        ''' Initializes the SPI bus using several FIO ports.

            Args:
                CS (int): the FIO channel to use as chip select
                CLK (int): the FIO channel to use as the clock
                MISO (int): the FIO channel to use for input
                MOSI (int): the FIO channel to use for output
        '''
        self._write_dict({
            "SPI_CS_DIONUM": CS,
            "SPI_CLK_DIONUM": CLK,
            "SPI_MISO_DIONUM": MISO,
            "SPI_MOSI_DIONUM": MOSI,
            "SPI_MODE": mode,                 # Selecting Mode CPHA=1 (bit 0), CPOL=1 (bit 1)
            "SPI_SPEED_THROTTLE": 0,     # Valid speed throttle values are 1 to 65536 where 0 = 65536 ~ 800 kHz
            "SPI_OPTIONS": 0              # Enabling active low clock select pin
        })

    def write_string(self, cmd):
        ''' Separates the bitstring cmd into a series of bytes and sends them through the SPI. '''
        lst = []
        r = 0
        for i in [0, 8, 16]:
            lst.append(int(cmd[i:8+i],2))
        r = self.write_bytes(lst)

    def write_bytes(self, data):
        ''' Writes a list of commands via SPI.

            Args:
                data (list): a list of bytes to send through MOSI.
        '''
        numBytes = len(data)
        self._command("SPI_NUM_BYTES", numBytes)

        # Write the bytes
        ljm.eWriteNameByteArray(self.handle, "SPI_DATA_TX", len(data), data)
        self._command("SPI_GO", 1)  # Do the SPI communications
