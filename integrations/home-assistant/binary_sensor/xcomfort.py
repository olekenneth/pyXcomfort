"""
Support for Xcomfort lights and wall switches.

For more details about this platform, please refer to the documentation at
https://github.com/olekenneth/pyXcomfort
"""

from threading import Timer
from homeassistant.const import CONF_SWITCHES, CONF_TIMEOUT
from homeassistant.components.binary_sensor import BinarySensorDevice

CONF_SERIAL = "serial"
DATA_XCOMFORT = "xcomfort"

TIMEOUT = 240


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Xcomfort Light platform."""

    print("hei", config)
    xcomfort = hass.data[DATA_XCOMFORT]

    add_devices(XcomfortSwitch(switch) for switch in xcomfort.switches)
    if discovery_info[CONF_TIMEOUT]:
        global TIMEOUT
        TIMEOUT = discovery_info[CONF_TIMEOUT]


class XcomfortSwitch(BinarySensorDevice):
    """Representation of a Xcomfort Wall switch as a binary sensor."""

    def __init__(self, switch):
        """Initialize a Xcomfort switch."""
        self._switch = switch
        self._switch.onChange(self.turnOn)
        self._state = False

    def turnOn(self, state):
        """Turn on state. And notify HASS."""
        self._state = True
        self.schedule_update_ha_state()
        t = Timer(TIMEOUT, self.turnOff)
        t.start()

    def turnOff(self):
        """Turn off state. And notify HASS."""
        self._state = False
        self.schedule_update_ha_state()

    @property
    def name(self):
        """Return the display name of this binary sensor."""
        return self._switch.name

    @property
    def is_on(self):
        """Return true if binary sensor is on."""
        return self._state

    @property
    def should_poll(self):
        """Tell Home Assistant not to poll this device."""
        return False
