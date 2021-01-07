from labjack import ljm
from scipy.signal import resample
import numpy as np

class Stream:
    def __init__(self, labjack):
        self.labjack = labjack

    def configure(self, settling_time=0, resolution_index=0, clock_source=0):
        self.stop()
        self.labjack._write_dict({'STREAM_SETTLING_US': settling_time,
                                  'STREAM_RESOLUTION_INDEX': resolution_index,
                                  'STREAM_CLOCK_SOURCE': clock_source
                        })

    def set_inhibit(self, channels):
        bitmask = self.labjack.digital.bitmask(channels)
        inhibit = 0x7FFFFF-bitmask

        self.labjack._write_dict({'DIO_INHIBIT': inhibit,
                                  'DIO_DIRECTION': bitmask
                                  })

    def stop(self):
        ''' Stop streaming if currently running '''
        try:
            ljm.eStreamStop(self.labjack.handle)
        except:
            pass

    def resample(self, array, period, max_samples = 8191):
        ''' Compute optimum scan rate and number of samples '''
        if self.labjack.deviceType == ljm.constants.dtT7:
            max_speed = 100000
        elif self.labjack.deviceType == ljm.constants.dtT4:
            max_speed = 40000

        cutoff = max_samples / max_speed
        if period >= cutoff:
            samples = max_samples
            scanRate = int(samples/period)
        else:
            scanRate = max_speed
            samples = int(period*scanRate)

        stream = resample(array, samples)
        return stream, scanRate

    def AIn_start(self, channels, scan_rate):
        self.stop()
        scan_list = ljm.namesToAddresses(len(channels), channels)[0]

        scans_per_read = int(scan_rate/2)
        ljm.eStreamStart(self.labjack.handle, scans_per_read, len(channels), scan_list, scan_rate)

    def AIn_read(self):
        return ljm.eStreamRead(self.labjack.handle)

    def AOut(self, channels, data, scanRate, loop=0):
        self._start([1000+2*ch for ch in channels], data, scanRate, loop=loop, dtype='F32')

    def DOut(self, data, scanRate, loop=0):
        self._start([2500], data, scanRate, loop=loop, dtype='U16')

    def _start(self, channels, data, scanRate, loop = 0, dtype='F32'):
        self.stop()
        n = np.ceil(np.log10(2*(1+len(data)))/np.log10(2))
        buffer_size = 2**n
        i = 0
        scan_list = []
        for ch in channels:
            self.labjack._write_dict({f'STREAM_OUT{i}_TARGET': ch,
                              f'STREAM_OUT{i}_BUFFER_SIZE': buffer_size,
                              f'STREAM_OUT{i}_ENABLE': 1
                            })

            target = ['STREAM_OUT%i_BUFFER_%s'%(i, dtype)] * len(data)
            self.labjack._write_array(target, list(data))

            self.labjack._write_dict({f'STREAM_OUT{i}_LOOP_SIZE': loop*len(data),
                              f'STREAM_OUT{i}_SET_LOOP': 1
                            })
            scan_list.append(4800+i)
            i += 1
        scanRate = ljm.eStreamStart(self.labjack.handle, 1, len(scan_list), scan_list, scanRate)

    def set_trigger(self, ch):
        if ch is None:
            self.labjack._command("STREAM_TRIGGER_INDEX", 0) # disable triggered stream
        else:
            self.labjack._command(f"DIO{ch}_EF_ENABLE", 0)
            self.labjack._write_dict({
                              f"DIO{ch}_EF_INDEX": 3,
                              f"DIO{ch}_EF_OPTIONS": 0,
                              f"DIO{ch}_EF_VALUE_A": 2,
                              f"DIO{ch}_EF_CONFIG_A": 2,
                              "STREAM_TRIGGER_INDEX": 2000+ch,
                              f"DIO{ch}_EF_ENABLE": 1
                              })
            ljm.writeLibraryConfigS('LJM_STREAM_RECEIVE_TIMEOUT_MS',0)  #disable timeout
