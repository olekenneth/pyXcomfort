import unittest
from xcomfort.devices import *

class XcomfortMock(unittest.TestCase):
    def setState(self, serial, value):
        self.assertEqual(value, True)
    def setBrightness(self, serial, value):
        self.assertEqual(value > 0, True)

class TestDevices(unittest.TestCase):
    def test_device(self):
        d = Device()
        self.assertEqual(d.state, False)
        self.assertEqual(str(d), '<xcomfort.devices.Device object serial 0>')

    def test_sensor(self):
        s = Sensor()
        self.assertEqual(s.value, 0)

    def test_switch(self):
        s = Switch()
        self.assertEqual(s.buttons, 0)

    def test_light(self):
        xcomfortMock = XcomfortMock()
        l = Light(xcomfortMock)
        l.state = True
        l.brightness = 50
        self.assertEqual(l.state, True)
        self.assertEqual(l.brightness, 50)

        l2 = Light()
        l._isDimable = False
        with self.assertRaises(NotImplementedError):
            l.brightness = 50

    def test_silentLight(self):
        l = Light()
        l.state = True
        l.brightness = 50
        self.assertEqual(l.silentState, True)
        self.assertEqual(l.silentBrightness, 50)
