class Device():
    def __init__(self, xcomfort = None):
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

    def _runCallbacks(self):
        print(self._callbacks)
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

class Sensor(Device):
    def __init__(self, xcomfort = None):
        super().__init__(xcomfort)
        self._deviceType = ''
        self._value = 0

    @property
    def value(self):
        return self._value

class Switch(Device):
    def __init__(self, xcomfort = None):
        super().__init__(xcomfort)
        self._buttons = 0

    @property
    def buttons(self):
        return self._buttons

class Light(Device):
    def __init__(self, xcomfort = None):
        super().__init__(xcomfort)
        self._isDimable = True
        self._brightness = 0

    def requestState(self):
        if self._xcomfort:
            self._xcomfort.requestState(self._serialAsBytes)

    @property
    def isDimable(self):
        return self._isDimable

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self._runCallbacks()
        if self._xcomfort:
            self._xcomfort.setState(self._serialAsBytes, value)

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
        self._runCallbacks()

        if self._xcomfort:
            self._xcomfort.setBrightness(self._serialAsBytes, value)
