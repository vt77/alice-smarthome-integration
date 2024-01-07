import json

class DeviceInfo:
    __slots__ = "manufacturer", "model", "hw_version", "sw_version"

    def __init__(self, manufacturer, model, hw_version, sw_version):
        self.manufacturer = manufacturer
        self.model = model
        self.hw_version = hw_version
        self.sw_version = sw_version

    def __iter__(self):
        for attr in self.__slots__:
            yield attr, self.__getattribute__(attr)

    def __str__(self):
        return json.dumps(dict(self))
