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
            print('Failed to connect to LabJack (%s): %s.'%(self.params['devid'], e))

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

    def _write_array(self, registers, values):
        ljm.eWriteNames(self.handle, len(registers), registers, values)

    def stop(self):
        ''' Stop streaming if currently running '''
        try:
            ljm.eStreamStop(self.handle)
        except:
            pass

if __name__ == '__main__':
    lj = LabJack(devid='470018954')
