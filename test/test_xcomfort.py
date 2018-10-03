import unittest
from xcomfort.xcomfort import *

class SerialPortMock(unittest.TestCase):
    def write(self, message):
        self.assertEqual(type(message), bytearray)

    def read(self, length):
        self.assertEqual(length, 1)
        return bytearray(b'\x5a\x1b\x03\x55\x00\x13\x17\x10\x04\x01\xfd\x6d\x20\x00\x00\x5b\x00\x00E\xbe\x00\xa5')

    @property
    def in_waiting(self):
        return 1

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
        sensor = self.instance.parseSensor(data, Sensor())
        self.assertEqual(s.state, sensor.state)
        self.assertEqual(s._value, sensor._value)

    def test_parseSwitch(self):
        data = bytearray(b'\x5a\x1b\x03\x55\x00\x13\x17\x10\x04\x01\xfd\x6d\x20\x00\x00\x5b\x00\x00E\xbe\x00\xa5')
        switch = self.instance.parseSwitch(data, Switch())
        self.assertEqual(True, switch.state)
        self.instance.parse(data)
        switches = self.instance.switches
        self.assertEqual(len(switches), 1)

    def test_parseLight(self):
        lightData = bytearray(b'\x5a\x24\x03\x70\x00\x1c\x1b\xa0\x3f\x00\x66\x62\x24\x00\x00\x80\x00\x00\x00\xf0\x00\x11\x03\x00\x2d\x24\x6a\x00\x42\x02\x4a\x61\x39\x62\xfd\xa5')
        light = self.instance.parseLight(lightData, Light())
        self.assertEqual(False, light._isDimable)
        self.assertEqual(True, light.state)

    def test_appendDevice(self):
        s = Sensor()
        s._value = 19.9
        s._deviceType = 'temperature'
        s._serial = 2384486
        self.instance._appendDevice(s)

        self.assertEqual(len(self.instance.sensors), 1)

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
        sensorData = bytearray(b'Z \x03c\x00\x18\x18"\x04\x00\x14\xd0\x1f\x00\x00\xc5\xc4U\x00\x17\x00\xd5\x00\xff\xff\xf3\xa4\x89\xdb\x17\xfd\xa5')


        def switchCallback(switch):
            self.assertEqual(2125309, switch._serial)

        def sensorCallback(sensor):
            self.assertEqual(5620933, sensor._serial)
            self.assertEqual(21.3, sensor._value)

        def lightCallback(light):
            self.assertEqual(2384486, light._serial)
            self.assertEqual(False, light.state)

        def firstLightChangeCallback(light):
            self.assertEqual(2384481, light._serial)

        def secondLightChangeCallback(light):
            self.assertEqual(2384482, light._serial)

        self.instance.onSensor(sensorCallback)
        self.instance.onSwitch(switchCallback)
        self.instance.onLight(lightCallback)
        self.instance.parse(sensorData)
        self.instance.parse(switchData)
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

    def test_setSwitches(self):
        self.instance.switches = [
            { 'name': 'Living room', 'serial': 5109324 }
        ]
        self.assertEqual(len(self.instance.switches), 1)
        self.assertEqual(type(self.instance.switches[0]), Switch)

        self.instance.switches = [ 5109325 ]
        self.assertEqual(len(self.instance.switches), 2)
        self.assertEqual(self.instance.switches[1].name, 'switch-5109325')

    def test_bougusData(self):
        self.assertEqual(self.instance.parse(bytearray(b'\x5a\xff\x1b')), None)

    def test_setState(self):
        with self.assertRaises(TypeError):
            self.instance.setState(None, 'test')

        serial = bytearray()
        def sendCommandMock(serialAsByte, state):
            self.assertEqual(serialAsByte, serial)

        self.instance.sendCommand = sendCommandMock
        self.instance.setState(serial, True)
        self.instance.setState(serial, False)

    def test_setBrigtness(self):
        def sendDimCommandMock(serialAsByte, state):
            self.assertEqual(state, b'\xff')
        def setStateMock(serialAsByte, state):
            self.assertEqual(state, False)

        self.instance.setState = setStateMock
        self.instance.sendDimCommand = sendDimCommandMock
        self.instance.setBrightness(bytearray(), 255)
        self.instance.setBrightness(bytearray(), 0)

    def test_threads(self):
        serialPort = SerialPortMock()
        myInstance = Xcomfort(serialPort)
        myInstance.readerShutdown = True
        myInstance.writerShutdown = True

    def test_requestStateForAllLights(self):
        l = Light()
        self.instance._appendDevice(l)
        self.instance.requestStateForAllLights._original(self.instance)

    def test_read(self):
        serialPort = SerialPortMock()
        myInstance = Xcomfort(serialPort)
        def parseMock(bytes):
            myInstance.readerShutdown = True
            self.assertEqual(bytes, bytearray(b'\x5a\x1b\x03\x55\x00\x13\x17\x10\x04\x01\xfd\x6d\x20\x00\x00\x5b\x00\x00E\xbe\x00\xa5'))

        def parseMockException(bytes):
            raise Exception('This is an exception')

        myInstance.parse = parseMock
        myInstance.read()

        myInstance.readerShutdown = False
        myInstance.parse = parseMockException
        myInstance.read()
