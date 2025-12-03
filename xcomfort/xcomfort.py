import random
import threading
import time
import uuid
from collections import OrderedDict
from xcomfort.crc import Crc
from xcomfort.convert import Convert
from xcomfort.devices import Light, Sensor, Switch
from xcomfort.debounce import debounce

class Xcomfort:
    messages = []
    startUpMessages = [
        "5a040ba5",
        "5a051a00a5",
        "5a09470800000006a5",
        "5a0444a5",
        "5a0442a5",
        "5a0422a5",
        "5a053301a5",
        "5a051a01a5",
        "5a0634ffffa5",
        "5a0431a55a0436a5",
    ]

    @property
    def lights(self):
        return self.devices[Light]

    @lights.setter
    def lights(self, lightsConfig):
        for lightConfig in lightsConfig:
            light = Light(self)
            if isinstance(lightConfig, (OrderedDict, dict)):
                serial = lightConfig["serial"]
                name = lightConfig["name"] or "lamp-" + str(serial)
            elif isinstance(lightConfig, int):
                serial = lightConfig
                name = "lamp-" + str(serial)
            else:
                name = "device " + str(uuid.uuid4().hex)
            light.name = name
            light.serial = serial
            self._appendDevice(light)
            light.requestState()
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
            if isinstance(switchConfig, (OrderedDict, dict)):
                serial = switchConfig["serial"]
                name = switchConfig["name"] or "switch-" + str(serial)
            elif isinstance(switchConfig, int):
                serial = switchConfig
                name = "switch-" + str(serial)
            else:
                name = "switch " + str(uuid.uuid4().hex)
            switch.name = name
            switch.serial = serial
            self._appendDevice(switch)

    def setState(self, serial, state):
        if not isinstance(state, bool):
            raise TypeError("State should be True/False")
        command = b"\x50" if state is True else b"\x51"
        self._sendCommand(serial, command)
        self._sendCommand(serial, command)
        self._sendCommand(serial, command)

    def setBrightness(self, serial, brightness):
        if brightness > 1:
            command = Convert.intToBytes(brightness, length=1)
            self._sendDimCommand(serial, command)
            self._sendDimCommand(serial, command)
            self._sendDimCommand(serial, command)
        else:
            self.setState(serial, False)

    def requestState(self, serial):
        self._sendCommand(serial, b"\x70")
        time.sleep(0.3)

    @debounce(3)
    def requestStateForAllLights(self):
        for light in self.devices[Light]:
            self.requestState(light.serialAsBytes)

    def find(self, device):
        deviceType = type(device)
        return next(
            (j for j in self.devices[deviceType] if j.serial == device.serial), None
        )

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

    def __init__(self, serialPort=None, devicePath=None):
        self.devices = {Light: [], Sensor: [], Switch: []}
        self._callbacks = {Light: [], Sensor: [], Switch: []}

        if devicePath and not serialPort:
            import serial

            serialPort = serial.Serial(
                port=devicePath,
                baudrate=115200,
                timeout=0.05,
                write_timeout=0.05,
                inter_byte_timeout=None
            )

        if serialPort:
            self.serialPort = serialPort

            for message in self.startUpMessages:
                self.messages.append(bytearray(bytes.fromhex(message)))

            self.readerShutdown = False
            self.readerThread = threading.Thread(target=self.read, name="rx")
            self.readerThread.daemon = True
            self.readerThread.start()

            self.writerShutdown = False
            self.writerThread = threading.Thread(target=self.write, name="tx")
            self.writerThread.daemon = True
            self.writerThread.start()

    def write(self):
        while not self.writerShutdown:
            time.sleep(0.01)
            if self.messages:
                message = self.messages.pop(0)
                if message:
                    self.serialPort.write(message)
                    self.serialPort.flush()
                    time.sleep(0.005)

    def read(self):
        readBytes = bytearray()
        try:
            while not self.readerShutdown:
                time.sleep(0.01)
                byte = self.serialPort.read(self.serialPort.in_waiting or 1)
                if byte:
                    readBytes += byte
                    if byte[-1:] == b"\xa5":
                        self.parse(readBytes)
                        readBytes = bytearray()
        except Exception as ex:
            print("Exception happen in read thread", ex)

    def parseType(self, data):
        parsedType = None
        length = data[1:2]
        if length == b"\x1b":  # switch
            parsedType = Switch(self)
        elif length == b"\x20":  # temp. sensor
            parsedType = Sensor(self)
            parsedType.deviceType = "temperature"
        elif length == b"\x17" or length == b"\x24":  # light on/off
            parsedType = Light(self)
        elif length == b"\x19":  # light dim
            parsedType = Light(self)
        return parsedType

    @staticmethod
    def parseSerial(byteArray, device):
        deviceType = type(device)

        if deviceType == Switch:
            serialAsBytes = byteArray[10:14]
        elif deviceType == Sensor:
            serialAsBytes = byteArray[15:19]
        elif deviceType == Light:
            serialAsBytes = byteArray[10:14]
        else:
            print("Unable to detect device type")
            return device

        serial = Convert.bytesToInt(serialAsBytes, byteorder="big")
        # device.serialAsBytes = serialAsBytes
        device.serial = serial

        return device

    def parse(self, data):
        device = self.parseType(data)
        if not device:
            return
        device = self.parseSerial(data, device)
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
        elif deviceType == Sensor and device.deviceType == "temperature":
            self.parseSensor(data, device)

        self._runCallbacks(device)

    @staticmethod
    def parseSensor(data, device):
        value = Convert.bytesToDecimal(data[21:22])
        state = Convert.bytesToInt(data[24:25]) == 255
        device.value = value
        device.state = state

        return device

    def parseSwitch(self, data, device):
        state = data[3:4] != bytearray(b"\x51")
        button = int.from_bytes(data[9:10], byteorder="big")
        button += 1

        device.buttons = max(device.buttons, button)
        device.state = state

        self.requestStateForAllLights()

        return device

    @staticmethod
    def parseLight(data, device):
        stateValue = Convert.bytesToInt(data[22:23])
        state = True

        if stateValue == 3:
            device.isDimable = False

        if stateValue < 3:
            state = False

        device.silentBrightness = stateValue
        device.silentState = state

        return device

    def _sendDimCommand(self, serial, dim):
        data = bytearray()
        data += b"\x5a"
        data += b"\x19"
        data += b"\x1b"
        data += b"\x5a"
        data += b"\x00"
        data += b"\x15"
        data += bytes([random.randint(0x10, 0x1F)]) # random seq
        data += b"\x82"
        data += b"\x07"
        data += b"\x00"
        data += b"\x80"
        data += b"\x00"
        data += b"\x00"
        data += b"\x00"
        data += b"\x00"
        data += serial
        data += b"\x01"
        data += b"\x00"
        data += dim
        data += b"\x00"
        data += b"\x00"
        data += b"\xa5"

        data = Crc.generate(data)

        self.messages.append(data)

        return data

    def _sendCommand(self, serial, state):
        data = bytearray()
        data += b"\x5a"
        data += b"\x17"
        data += b"\x1b"
        data += state
        data += b"\x00"
        data += b"\x13"
        data += bytes([random.randint(0x10, 0x1F)]) # random seq
        data += b"\x82"
        data += b"\x07"
        data += b"\x00"
        data += b"\x80"
        data += b"\x00"
        data += b"\x00"
        data += b"\x00"
        data += b"\x00"
        data += serial
        data += b"\x00"
        data += b"\x00"
        data += b"\x00"
        data += b"\xa5"

        data = Crc.generate(data)

        if state == b"\x70":
            self.messages.append(data)
        else:
            self.messages.insert(0, data)

        return data
