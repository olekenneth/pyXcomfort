"""
Support for Xcomfort lights and wall switches.

For more details about this platform, please refer to the documentation at
https://github.com/olekenneth/pyXcomfort
"""
import voluptuous as vol
from homeassistant.const import (
    CONF_DEVICE, CONF_SWITCHES, CONF_NAME, CONF_TIMEOUT, CONF_DEVICES)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import load_platform
from xcomfort.xcomfort import Xcomfort

DOMAIN = 'xcomfort'
DATA_XCOMFORT = 'xcomfort'
CONF_SERIAL = 'serial'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_DEVICE, default='/dev/ttyUSB0'): cv.string,
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [
            {
                vol.Required(CONF_SERIAL): cv.positive_int,
                vol.Required(CONF_NAME): cv.string,
            }
        ]),
        vol.Optional(CONF_TIMEOUT, default=240): cv.positive_int,
        vol.Optional(CONF_SWITCHES): vol.All(cv.ensure_list, [
            {
                vol.Required(CONF_SERIAL): cv.positive_int,
                vol.Required(CONF_NAME): cv.string,
            }
        ])
    })
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Your controller/hub specific code."""
    conf = config[DOMAIN]
    xcomfort = Xcomfort(devicePath=conf.get(CONF_DEVICE))
    xcomfort.lights = conf.get(CONF_DEVICES)
    xcomfort.switches = conf.get(CONF_SWITCHES)
    hass.data[DATA_XCOMFORT] = xcomfort

    load_platform(hass, 'light', DOMAIN)
    load_platform(hass, 'binary_sensor', DOMAIN, {CONF_TIMEOUT:
                                                  conf.get(CONF_TIMEOUT)})

    return True
