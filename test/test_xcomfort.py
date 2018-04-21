import unittest
from xcomfort.xcomfort import *


class TestXcomfort(unittest.TestCase):
    def setup_method(self, test_method):
        self.instance = Xcomfort()

    def teardown_method(self, test_method):
        self.instance = None

    def test_init(self):
        import serial
        self.assertRaises(serial.serialutil.SerialException, Xcomfort, None, '/dev/test')

    def test_sendDimCommand(self):
        serial = b'\xc5\xc4\x55\x00'
        state = b'\xF0'
        command = self.instance.sendDimCommand(serial, state)
        self.assertEqual(command, bytearray(b'\x5a\x19\x1b\x5a\x00\x15\x12\x82\x07\x00\x80\x00\x00\x00\x00\xc5\xc4U\x00\x01\x00\xf0\xbc\xd4\xa5'))

    def test_sendCommand(self):
        serial = b'\xc5\xc4\x55\x00'
        state = b'\x50'
        command = self.instance.sendCommand(serial, state)
        self.assertEqual(command, bytearray(b'\x5a\x17\x1b\x50\x00\x13\x1e\x82\x07\x00\x80\x00\x00\x00\x00\xc5\xc4U\x00\x00\xf8\x15\xa5'))

        serial = Convert.intToBytes(2125309, byteorder='little')
        state = b'\x50'
        command = self.instance.sendCommand(serial, state)
        self.assertEqual(Convert.bytesToHex(command, 'little'), '0x5a171b5000131e8207008000000000fd6d2000003279a5')

        serial = Convert.intToBytes(2168571, byteorder='little')
        state = b'\x50'
        command = self.instance.sendCommand(serial, state)
        self.assertEqual(Convert.bytesToHex(command, 'little'), '0x5a171b5000131e8207008000000000fb162100002682a5')

    def test_parseType(self):
        data = bytearray(b'Z \x03c\x00\x18\x18"\x04\x00\x14\xd0\x1f\x00\x00\xc5\xc4U\x00\x17\x00\xd5\x00\xff\xff\xf3\xa4\x89\xdb\x17\xfd\xa5')
        parsedType = self.instance.parseType(data)
        self.assertEqual(type(parsedType), Sensor)

        data = bytearray(b'\x5a\x1b\x03\x55\x00\x13\x17\x10\x04\x01\xfd\x6d\x20\x00\x00\x5b\x00\x00E\xbe\x00\xa5')
        parsedType = self.instance.parseType(data)
        self.assertEqual(type(parsedType), Switch)

    def test_parseSerial(self):
        data = bytearray(b'\x5a\x1b\x03\x55\x00\x13\x17\x10\x04\x01\xfd\x6d\x20\x00\x00\x5b\x00\x00E\xbe\x00\xa5')
        parsedType = self.instance.parseType(data)
        serial = self.instance.parseSerial(data, parsedType)
        self.assertEqual(2125309, serial)

    def test_parseSensor(self):
        data = bytearray(b'Z \x03c\x00\x18\x18"\x04\x00\x14\xd0\x1f\x00\x00\xc5\xc4U\x00\x17\x00\xd5\x00\xff\xff\xf3\xa4\x89\xdb\x17\xfd\xa5')
        s = Sensor()
        s._state = True
        s._value = 21.3
        s._serial = 5620933
        sensor = self.instance.parseSensor(data, s)
        self.assertEqual(s, sensor)

    def test_parseSwitch(self):
        data = bytearray(b'\x5a\x1b\x03\x55\x00\x13\x17\x10\x04\x01\xfd\x6d\x20\x00\x00\x5b\x00\x00E\xbe\x00\xa5')
        s = Switch()
        switch = self.instance.parseSwitch(data, s)
        s._state = True
        s._buttons = 1
        s._serial = 2125309
        self.assertEqual(s, switch)

    def test_parseLight(self):
        lightData = bytearray(b'\x5a\x24\x03\x70\x00\x1c\x1b\xa0\x3f\x00\x66\x62\x24\x00\x00\x80\x00\x00\x00\xf0\x00\x11\x03\x00\x2d\x24\x6a\x00\x42\x02\x4a\x61\x39\x62\xfd\xa5')
        l = Light()
        light = self.instance.parseLight(lightData, l)
        l._state = True
        l._serial = 2384486
        l._isDimable = True
        self.assertEqual(l, light)

    def test_appendDevice(self):
        s = Sensor()
        s._value = 19.9
        s._deviceType = 'temperature'
        s._serial = 2384486
        self.instance._appendDevice(s)

        self.assertEqual(len(self.instance.devices[Sensor]), 1)

    def test_find(self):
        l = Light()
        l._isDimable = True
        l._serial = 2384487
        l.state = True
        l.brightness = 50

        self.instance._appendDevice(l)
        foundLight = self.instance.find(l)

        self.assertEqual(True, foundLight.state)
        self.assertEqual(True, foundLight.isDimable)
        self.assertEqual(l._serial, foundLight._serial)

    def test_callbacks(self):
        switchData = bytearray(b'\x5a\x1b\x03\x55\x00\x13\x17\x10\x04\x01\xfd\x6d\x20\x00\x00\x5b\x00\x00E\xbe\x00\xa5')
        lightData = bytearray(b'\x5a\x24\x03\x70\x00\x1c\x1b\xa0\x3f\x00\x66\x62\x24\x00\x00\x80\x00\x00\x00\xf0\x00\x11\x00\x00\x2d\x24\x6a\x00\x42\x02\x4a\x61\x39\x62\xfd\xa5')

        def switchCallback(switch):
            self.assertEqual(2125309, switch._serial)

        def lightCallback(light):
            self.assertEqual(2384486, light._serial)
            self.assertEqual(False, light.state)

        def firstLightChangeCallback(light):
            self.assertEqual(2384481, light._serial)

        def secondLightChangeCallback(light):
            self.assertEqual(2384482, light._serial)

        self.instance.onSwitch(switchCallback)
        self.instance.onLight(lightCallback)
        self.instance.parse(switchData)
        self.instance.parse(lightData)

        light = Light()
        light._serial = 2384481
        light._state = False
        light.onChange(firstLightChangeCallback)
        light.state = True

        light = Light()
        light._serial = 2384482
        light._state = False
        light.onChange(secondLightChangeCallback)
        light.state = True


    def test_setLights(self):
        self.instance.lights = [
            { 'name': 'Plafond', 'serial': 2384481 },
            { 'name': 'Pendel', 'serial': 2384482 }
        ]
        self.assertEqual(len(self.instance.lights), 2)
        self.assertEqual(type(self.instance.lights[0]), Light)

        self.instance.lights = [ 2384483, 2384484 ]
        self.assertEqual(len(self.instance.lights), 4)
        self.assertEqual(self.instance.lights[3].name, 'lamp-2384484')

    def test_bougusData(self):
        self.assertEqual(self.instance.parse(bytearray(b'\x5a\xff\x1b')), None)
