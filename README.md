# pyXcomfort
[![Tests](https://github.com/olekenneth/pyXcomfort/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/olekenneth/pyXcomfort/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/olekenneth/pyXcomfort/badge.svg?branch=master)](https://coveralls.io/github/olekenneth/pyXcomfort?branch=master)
[![Known Vulnerabilities](https://snyk.io/test/github/olekenneth/pyXcomfort/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/olekenneth/pyXcomfort?targetFile=requirements.txt)

This is an **unofficial** Python library for controlling Moeller Eaton Xcomfort lights.
It requires the Xcomfort CRSZ-00/01 RS-232 programming interface. 

This repository is not associated with Moeller Eaton, Home Assistant or other [integrations](/integrations).

If you are running [Home Assistant Supervisor](https://www.home-assistant.io/hassio/) you can use the [XComfort HA Addon](https://github.com/olekenneth/hassio-addons)

## How to use

```bash
git clone git@github.com:olekenneth/pyXcomfort.git xcomfort
```

### Callback when a specific light changes
```python
from xcomfort.xcomfort import Xcomfort

xcomfort = Xcomfort(devicePath='/dev/ttyUSB0')
xcomfort.lights = [{ serial: 2118491, name: 'Plafond' }, ... ]

def lightChangeCallback(light):
  print(light.name + ' changed state to ' + str(light.state))

light = xcomfort.lights[0]
light.onChange(lightChangeCallback)
light.state = False   # turn off the light
light.brightness = 25 # turn light on and set brightness to 25%
```

### Callback when one of the lights change
```python
xcomfort.onLight(lightChangeCallback)
```

## Contribute

Please contribute.

## License

GPLv3 see [LICENSE](LICENSE)
