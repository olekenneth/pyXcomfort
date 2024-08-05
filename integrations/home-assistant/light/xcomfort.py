"""
Support for Xcomfort lights and wall switches.

For more details about this platform, please refer to the documentation at
https://github.com/olekenneth/pyXcomfort
"""

from homeassistant.components.light import ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light

XCOMFORT_SUPPORT_BRIGHTNESS = SUPPORT_BRIGHTNESS
DATA_XCOMFORT = "xcomfort"

TIMEOUT = 240


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Xcomfort Light platform."""
    xcomfort = hass.data[DATA_XCOMFORT]

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
    def unique_id(self):
        """Return a unique ID."""
        return str(self._light._serial)

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
