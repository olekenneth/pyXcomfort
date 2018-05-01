"""
Support for Xcomfort lights.

For more details about this platform, please refer to the documentation at
https://github.com/olekenneth/pyXcomfort
"""
import logging
import sys

import voluptuous as vol

from homeassistant.const import (CONF_DEVICE, CONF_NAME, CONF_DEVICES)
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light, PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv

sys.path.insert(0, './pyXcomfort/')
from xcomfort.xcomfort import Xcomfort

_LOGGER = logging.getLogger(__name__)

XCOMFORT_SUPPORT_BRIGHTNESS = SUPPORT_BRIGHTNESS

CONF_SERIAL = 'serial'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_DEVICE, default='/dev/ttyUSB0'): cv.string,
    vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [
        {
            vol.Required(CONF_SERIAL): cv.positive_int,
            vol.Required(CONF_NAME): cv.string,
        }
    ])
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Xcomfort Light platform."""
    xcomfort = Xcomfort(devicePath=config[CONF_DEVICE])
    xcomfort.lights = config[CONF_DEVICES]
    add_devices(XcomfortLight(light) for light in xcomfort.lights)


class XcomfortLight(Light):
    """Representation of a Xcomfort Light."""

    def __init__(self, light):
        """Initialize a Xcomfort Light."""
        self._light = light
        self._light.onChange(self.myUpdate)
        self._state = self._light.state
        self._brightness = self._light.brightness

    def myUpdate(self, light):
        """Tell Home Assistant new state available."""
        self.schedule_update_ha_state()

    @property
    def name(self):
        """Return the display name of this light."""
        return self._light.name

    @property
    def brightness(self):
        """Brightness of the light (an integer in the range 0-100)."""
        return self._light.brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._light.state

    @property
    def supported_features(self):
        """Flag supported features."""
        return XCOMFORT_SUPPORT_BRIGHTNESS if self._light.isDimable else 0

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        if ATTR_BRIGHTNESS in kwargs:
            self._light.brightness = int(kwargs[ATTR_BRIGHTNESS])
        else:
            self._light.state = True

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.state = False

    @property
    def should_poll(self):
        """Tell Home Assistant not to poll this device."""
        return False
