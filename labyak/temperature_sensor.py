from labyak import LabJack
import numpy as np

class TemperatureSensor(LabJack):
    def __init__(self, device='ANY', connection='ANY', devid='ANY', averages=10, channels=[0, 2, 4, 6], arange=0.05, type='J'):
        super().__init__(device=device, connection=connection, devid=devid)
        self.averages = averages

        self.type = {'J': 21, 'K': 22}[type]
        for ch in channels:
            self._write_dict({f'AIN{ch}_EF_INDEX': self.type,
                              f'AIN{ch}_EF_CONFIG_B': 60052,
                              f'AIN{ch}_EF_CONFIG_D': 1,
                              f'AIN{ch}_EF_CONFIG_E': 0,
                              f'AIN{ch}_NEGATIVE_CH': ch+1,
                              f'AIN{ch}_RANGE': arange
                            })

    def TIn(self, ch, return_error=False):
        vals = []
        for i in range(self.averages):
            vals = np.append(vals, self._query(f'AIN{ch}_EF_READ_A'))
        if return_error:
            return np.mean(vals) - 273.15, np.std(vals) / np.sqrt(len(vals))
        else:
            return np.mean(vals) - 273.15

if __name__ == '__main__':
    daq = TemperatureSensor(devid='470018954', averages=30)
