# labyak
High-level wrappers around the [LJM Python](https://github.com/labjack/labjack-ljm-python) library for data acquisition and waveform or pattern generation with the [LabJack T7](https://labjack.com/products/t7). Labyak does not yet officially support the LabJack T4, but it should be mostly compatible.

To install with pip and git, run the following from the command line:

``` pip install git+http://github.com/robertfasano/labyak.git ```

## Tutorial
See the Jupyter notebook "Examples.ipynb" for a runnable version.

### Connecting to a device
```python 
  from labyak import LabJack
  labjack = LabJack(devid='470017907')
```
### Analog I/O
Generate 1 V on channel DAC0 and measure it on ADC0:
```python
  labjack.analog.AOut(0, 1)
  print(labjack.analog.AIn(0)
```
Generate -6 V with an LJTick-DAC on the FIO0-1 block and measure it with ADC1:
```python
  labjack.analog.TDAC(0, -6)
  print(labjack.analog.AIn(1)
```

### Digital I/O
Output a series of bits on FIO2 and read them on FIO3:
```python
  write_bits = [0, 1, 1, 0, 1]
  read_bits = []

  for bit in write_bits:
      labjack.digital.DOut(2, bit)
      read_bits.append(labjack.digital.DIn(3))

  print(read_bits)
```

### Temperature sensing
Measure a type J thermocouple using AIN2 and AIN3 for the positive and negative leads:
```python
  labjack.temperature.configure(pos_ch=2, neg_ch=3, kind='J')
  labjack.temperature.TIn(2)
```

### Waveform generation
Output a sine-wave from 0 to 5 V with 5 kHz frequency:
```python
  import numpy as np
  f = 5e3                                       # frequency of waveform
  t = np.linspace(0, 1/f, 3000)                 # time axis of waveform
  V = 2.5*(1+np.sin(2*np.pi*f*t))               # sine wave

  labjack.waveform.start(t, V, channels = [1])  # start generation
```

### Pattern generation
Generate a pattern on FIO3: high for 1 ms, low for 500 us, high for 2 ms, then low for 1 ms:
```python
  period=4.5e-3
  sequence = {3: [(0, 1),         # start high
                  (1e-3, 0),      # switch to low at 1 ms
                  (1.5e-3, 1),    # switch to high at 1.5 ms
                  (3.5e-3, 0)]}   # switch to low at 3.5 ms

  labjack.pattern.start(sequence, period)
```
