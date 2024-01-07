import logging

logger  = logging.getLogger(__name__)

class Capability:
    """Base class for capability"""

    name:str = ""
    retrievable: bool = False
    reportable: bool = False
    state:dict = None
    action_result = None

    def __init__(self, retrievable=True, reportable=False):
        self.retrievable = retrievable
        self.reportable = reportable

    def get_full_name(self):
        return "devices.capabilities." + self.name

    def get_params(self):
        return {}

    def to_dict(self):
        data = {}
        if self.retrievable:
            data["retrievable"] = True
        if self.reportable:
            data["reportable"] = True
        return data


class CapabilityOnOff(Capability):
    name = "on_off"

    def __init__(self, split=False, **kwargs):
        self.split = split
        super().__init__(**kwargs)


    def get_params(self):
        # true — за включение и выключение отвечают разные команды;
        # false — за включение и выключение отвечает одна команда. Является значением по умолчанию.
        return {"split": self.split}

    def to_dict(self):
        data = super().to_dict()
        if self.split:
            data["split"] = True
        return data

    def set_state(self,value):
        return {
            'instance' : 'on',
            'value' : value  # False if off
        }


class CapabilityColorSettings(Capability):
    name = "color_setting"


class CapabilityColorRange(Capability):
    name = "range"

class CapabilityMode(Capability):
    name = "mode"

class CapabilityToggle(Capability):
    name = "toggle"
    def get_params(self):
        return {"instance": "backlight"}

def get_capability_by_name(name, **kwargs):
    logger.debug("Locate capability : %s",name)
    for cls in Capability.__subclasses__():
        if cls.name == name:
            return cls(**kwargs)
