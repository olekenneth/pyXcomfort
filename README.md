# pyXcomfort
[![Build Status](https://travis-ci.org/olekenneth/pyXcomfort.svg?branch=master)](https://travis-ci.org/olekenneth/pyXcomfort)
[![Coverage Status](https://coveralls.io/repos/github/olekenneth/pyXcomfort/badge.svg?branch=master)](https://coveralls.io/github/olekenneth/pyXcomfort?branch=master)

This is a Python library for controlling Moeller Eaton Xcomfort lights.
It require the RS-232 programming interface.

## How to use

```bash
pip install pyxcomfort
```

```python
from xcomfort.xcomfort import Xcomfort

def lightChangeCallback(light):
  print(light.name + ' changed state to ' + str(light.state))

xcomfort = Xcomfort(devicePath='/dev/ttyUSB0')
xcomfort.lights = [{ serial: 2118491, name: 'Plafond' }, ... ]

light = xcomfort.lights[0]
light.onChange(lightChangeCallback)
light.state = False   # turn off the light
light.brightness = 25 # turn light on and set brightness to 25%
```

## Contribute

Please contribute.

## License

GPLv3 see [LICENSE](LICENSE)
