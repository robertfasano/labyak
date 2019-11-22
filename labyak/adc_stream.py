from labjack import ljm
import numpy as np
import pandas as pd
import time
import datetime

class ADCStream:
    def __init__(self, labjack):
        self.labjack = labjack

    def start(self, channels, scanRate):
        self.scanRate = scanRate
        # self.effective_scan_rate = scanRate / len(channels)
        self.channels = channels
        self.labjack.stream.configure(settling_time=0, resolution_index=0, clock_source=0)
        self.labjack.stream.set_trigger(None)
        self.labjack.stream.AIn_start(channels, scanRate)

    def sample(self):
        return self.labjack.stream.AIn_read()

    def read(self):
        data = np.array(self.labjack.stream.AIn_read()[0])
        # tmax = len(data) / len(self.channels) / self.effective_scan_rate
        # t = time.time() + np.arange(0, tmax, 1/self.effective_scan_rate)
        now = datetime.datetime.utcnow()

        n = int(len(data) / len(self.channels))
        dt = 1 / self.scanRate
        times = []
        for i in range(n):
            times.append(now + datetime.timedelta(seconds=i*dt))
        data = pd.DataFrame(data.reshape(-1, len(self.channels)), columns=self.channels, index=times)
        return data[data != -9999.0]

if __name__ == '__main__':
    from labyak import LabJack
    lj = LabJack(devid='470018943')
