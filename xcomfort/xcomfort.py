from enum import Enum
import threading
import time
from xcomfort.crc import Crc
from xcomfort.convert import Convert
from xcomfort.devices import *
from xcomfort.debounce import debounce
from collections import OrderedDict

class Xcomfort():
    messages = []
    startUpMessages = [
        '5a040ba5',
        '5a051a00a5',
        '5a09470800000006a5',
        '5a0444a5',
        '5a0442a5',
        '5a0422a5',
        '5a053301a5',
        '5a051a01a5',
        '5a0634ffffa5',
        '5a0431a55a0436a5'
    ]

    @property
    def lights(self):
        return self.devices[Light]

    @lights.setter
    def lights(self, lightsConfig):
        for lightConfig in lightsConfig:
            light = Light(self)
            if type(lightConfig) == dict or type(lightConfig) == OrderedDict:
                serial = lightConfig['serial']
                name = lightConfig['name'] or 'lamp-' + str(serial)
            elif type(lightConfig) == int:
                serial = lightConfig
                name = 'lamp-' + str(serial)
            light._name = name
            light._serial = serial
            light._serialAsBytes = Convert.intToBytes(serial, byteorder='little', length=4)
            self._appendDevice(light)
            light.requestState()

    @property
    def sensors(self):
        return self.devices[Sensor]

    @property
    def switches(self):
        return self.devices[Switch]

    @switches.setter
    def switches(self, switchesConfig):
        for switchConfig in switchesConfig:
            switch = Switch(self)
            if type(switchConfig) == dict or type(switchConfig) == OrderedDict:
                serial = switchConfig['serial']
                name = switchConfig['name'] or 'switch-' + str(serial)
            elif type(switchConfig) == int:
                serial = switchConfig
                name = 'switch-' + str(serial)
            switch._name = name
            switch._serial = serial
            switch._serialAsBytes = Convert.intToBytes(serial, byteorder='little', length=4)
            self._appendDevice(switch)

    def setState(self, serial, state):
        if type(state) != bool:
            raise TypeError('State should be True/False')
        command = b'\x50' if state == True else b'\x51'
        self.sendCommand(serial, command)

    def setBrightness(self, serial, brightness):
        if (brightness > 1):
            command = Convert.intToBytes(brightness, length=1)
            self.sendDimCommand(serial, command)
        else:
            self.setState(serial, False)

    def requestState(self, serial):
        self.sendCommand(serial, b'\x70')

    @debounce(3)
    def requestStateForAllLights(self):
        for light in self.devices[Light]:
            self.requestState(light._serialAsBytes)

    def find(self, device):
        deviceType = type(device)
        return next((d for d in self.devices[deviceType] if d._serial == device._serial), None)

    def _appendDevice(self, device):
        deviceType = type(device)
        result = self.find(device)
        if not result:
            self.devices[deviceType].append(device)

    def _runCallbacks(self, device):
        deviceType = type(device)
        for callback in self._callbacks[deviceType]:
            callback(device)

    def onLight(self, callback):
        self._callbacks[Light].append(callback)

    def onSwitch(self, callback):
        self._callbacks[Switch].append(callback)

    def onSensor(self, callback):
        self._callbacks[Sensor].append(callback)

    def __init__(self, serialPort = None, devicePath = None):
        self.devices = {
            Light: [],
            Sensor: [],
            Switch: []
        }
        self._callbacks = {
            Light: [],
            Sensor: [],
            Switch: []
        }

        if devicePath and not serialPort:
            import serial
            serialPort = serial.Serial(devicePath, 115200)

        if serialPort:
            self.serialPort = serialPort

            for message in self.startUpMessages:
                self.messages.append(bytearray(bytes.fromhex(message)))

            self.readerShutdown = False
            self.readerThread = threading.Thread(target=self.read, name='rx')
            self.readerThread.daemon = True
            self.readerThread.start()

            self.writerShutdown = False
            self.writerThread = threading.Thread(target=self.write, name='tx')
            self.writerThread.daemon = True
            self.writerThread.start()

    def write(self):
        while not self.writerShutdown:
            time.sleep(.01)
            if len(self.messages) > 0:
                message = self.messages.pop(0)
                if (message):
                    self.serialPort.write(message)
                    time.sleep(0.5)

    def read(self):
        bytes = bytearray()
        try:
            while not self.readerShutdown:
                time.sleep(.01)
                byte = self.serialPort.read(self.serialPort.in_waiting or 1)
                if byte:
                    bytes += byte
                    if byte[-1:] == b'\xa5':
                        self.parse(bytes)
                        bytes = bytearray()
        except Exception as e:
            print('Exception happen in read thread', e)

    def parseType(self, data):
        parsedType = None
        length = data[1:2]
        if length == b'\x1b': # switch
            parsedType = Switch(self)
        elif length == b'\x20': # temp. sensor
            parsedType = Sensor(self)
            parsedType._deviceType = 'temperature'
        elif length == b'\x17' or length == b'\x24': # light on/off
            parsedType = Light(self)
        elif length == b'\x19': # light dim
            parsedType = Light(self)
        return parsedType

    def parseSerial(self, byteArray, device):
        deviceType = type(device)

        if deviceType == Switch:
            bytes = byteArray[10:14]
        elif deviceType == Sensor:
            bytes = byteArray[15:19]
        elif deviceType == Light:
            bytes = byteArray[10:14]

        serial = Convert.bytesToInt(bytes, byteorder='big')
        device._serialAsBytes = bytes
        device._serial = serial

        return serial

    def parse(self, data):
        device = self.parseType(data)
        if not device:
            return
        serial = self.parseSerial(data, device)
        result = self.find(device)
        if result:
            device = result
        else:
            self._appendDevice(device)

        deviceType = type(device)
        if deviceType == Switch:
            self.parseSwitch(data, device)
        elif deviceType == Light:
            self.parseLight(data, device)
        elif deviceType == Sensor and device._deviceType == 'temperature':
            self.parseSensor(data, device)

        self._runCallbacks(device)

    def parseSensor(self, data, device):
        value = Convert.bytesToDecimal(data[21:22])
        state = Convert.bytesToInt(data[24:25]) == 255
        device._state = state
        device._value = value
        device._runCallbacks()

        return device

    def parseSwitch(self, data, device):
        state = data[3:4] != bytearray(b'\x51')
        button = int.from_bytes(data[9:10], byteorder='big')
        button += 1

        device._state = state
        device._buttons = max(device._buttons, button)
        device._runCallbacks()

        self.requestStateForAllLights()

        return device

    def parseLight(self, data, device):
        stateValue = Convert.bytesToInt(data[22:23])
        state = True

        if (stateValue == 3):
            device._isDimable = False

        if stateValue < 3:
            state = False

        device._state = state
        device._brightness = stateValue
        device._runCallbacks()
        return device

    def sendDimCommand(self, serial, dim):
        data = bytearray()
        data += b'\x5a'
        data += b'\x19'
        data += b'\x1b'
        data += b'\x5a'
        data += b'\x00'
        data += b'\x15'
        data += b'\x12'
        data += b'\x82'
        data += b'\x07'
        data += b'\x00'
        data += b'\x80'
        data += b'\x00'
        data += b'\x00'
        data += b'\x00'
        data += b'\x00'
        data += serial
        data += b'\x01'
        data += b'\x00'
        data += dim
        data += b'\x00'
        data += b'\x00'
        data += b'\xa5'

        data = Crc.generate(data)

        self.messages.append(data)

        return data

    def sendCommand(self, serial, state):
        data = bytearray()
        data += b'\x5a'
        data += b'\x17'
        data += b'\x1b'
        data += state
        data += b'\x00'
        data += b'\x13'
        data += b'\x1e'
        data += b'\x82'
        data += b'\x07'
        data += b'\x00'
        data += b'\x80'
        data += b'\x00'
        data += b'\x00'
        data += b'\x00'
        data += b'\x00'
        data += serial
        data += b'\x00'
        data += b'\x00'
        data += b'\x00'
        data += b'\xa5'

        data = Crc.generate(data)

        self.messages.append(data)

        return data
