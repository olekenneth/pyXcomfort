from xcomfort.convert import Convert

class Device():
    def __init__(self, xcomfort=None):
        self._state = False
        self._serial = 0
        self._serialAsBytes = bytearray()
        self._name = ''
        self._xcomfort = xcomfort
        self._callbacks = []

    def __repr__(self):
        return '<xcomfort.devices.{0} object serial {1}>'.format(
            self.__class__.__name__,
            self._serial)

    def runCallbacks(self):
        for callback in self._callbacks:
            callback(self)

    def onChange(self, callback):
        self._callbacks.append(callback)

    @property
    def state(self):
        return self._state

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, value):
        self._serial = value
        self._serialAsBytes = Convert.intToBytes(value, byteorder='little', length=4)

    @property
    def serialAsBytes(self):
        return self._serialAsBytes

class Sensor(Device):
    def __init__(self, xcomfort=None):
        super().__init__(xcomfort)
        self._deviceType = ''
        self._value = 0

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.runCallbacks()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def deviceType(self):
        return self._deviceType

    @deviceType.setter
    def deviceType(self, value):
        self._deviceType = value

class Switch(Device):
    def __init__(self, xcomfort=None):
        super().__init__(xcomfort)
        self._buttons = 0

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.runCallbacks()

    @property
    def buttons(self):
        return self._buttons

    @buttons.setter
    def buttons(self, value):
        self._buttons = value

class Light(Device):
    def __init__(self, xcomfort=None):
        super().__init__(xcomfort)
        self._isDimable = True
        self._brightness = 0

    def requestState(self):
        if self._xcomfort:
            self._xcomfort.requestState(self._serialAsBytes)

    @property
    def isDimable(self):
        return self._isDimable

    @isDimable.setter
    def isDimable(self, value):
        self._isDimable = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.runCallbacks()
        if self._xcomfort:
            self._xcomfort.setState(self._serialAsBytes, value)

    @property
    def silentState(self):
        return self._state

    @silentState.setter
    def silentState(self, value):
        self._state = value
        self.runCallbacks()

    @property
    def silentBrightness(self):
        return self._brightness

    @silentBrightness.setter
    def silentBrightness(self, value):
        self._brightness = value
        self.runCallbacks()

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if not self.isDimable:
            raise NotImplementedError('Cannot set brightness for a non dimable light')

        state = True if value > 0 else False
        self._state = state

        self._brightness = value
        self.runCallbacks()

        if self._xcomfort:
            self._xcomfort.setBrightness(self._serialAsBytes, value)
