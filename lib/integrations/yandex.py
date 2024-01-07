from __future__ import annotations

import logging
import json
from devices import Device
from devices.actions import QueryResult, ActionResult
from .capabilities import get_capability_by_name
from .property import get_property_by_name
from .resolve import ActionRequest,QueryRequest
from .deviceinfo import DeviceInfo

logger = logging.getLogger(__name__)

class YandexResponse:
    """Convert general responce to Yandex API format serilizable json
    """
    def __init__(self,request_id, devices, nickname=None):
        self.request_id = request_id
        self.devices = devices
        self.nickname = nickname

    def __iter__(self):
        yield "request_id", self.request_id
        yield "payload", self.payload

    @property
    def payload(self):
        payload = {'devices':[dict(e) for e in self.devices]}
        if self.nickname: 
            payload['user_id'] = self.nickname
        return payload

class YandexError:
    """Handle errors in Yandex format """
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message

    def __iter__(self):
        yield "error_code",self.error_code
        yield "error_message",self.error_message


class YandexRequest:
    """Parse and handle yandex format request
    """

    def __init__(self,data):
        self.data = data

    @property
    def devices(self):
        return self.data['devices']


    @staticmethod
    def build_query_request(data:dict,request:list=None):
        """Builds StatableValue query request 

        Args:
            data (dict): StatableValue db data
            request (dict): requested values

        Returns:
            StatableValueRequest: request data
        """

        query_requests = data
        for name,r in query_requests:
            query_requests[r]['resolve'] = QueryRequest(name)

    @staticmethod
    def build_action_request(data:dict,request:list) -> dict:
        """ Converts yandex capability to action 

        Args:
            data (dict) : device capabilities
            capability (list): capabilities in yandex format

        Returns:
            list: capabilities data in database format
        """

        ret = {}
        for capability in request: 
            capability_name = capability['type'][21:]
            if capability_name in data:
               ret[capability_name] = data[capability_name]
               ret[capability_name]['resolve'] = ActionRequest(capability_name,capability['state'])

        return ret



class StatableValue:
    # Type of value - float/event for property or capability
    ptype = None
    # Value instance name in state (Ex: humidity  or 'on' for on_off ) 
    instance = None
    # instance value after query (Ex, true)
    value = None 
    # if action processd
    action_result = None

    # Value should be resolved/action done
    resolve = None

    def get_state(self):
        if not self.instance:
            return None
        state = {'instance':self.instance}
        # Value only exists when query function requested
        if self.value is not None:
            state['value'] = self.value
        if self.action_result is not None:
            state['action_result'] = self.action_result
        return state

    def set_result(self,result):
        logger.info("Set result %s",result)
        self.instance = result.param
        if isinstance(result,ActionResult):
            self.action_result = dict(result)
        if isinstance(result,QueryResult):
            self.value = result.value


class DeviceCapability(StatableValue):
    CAPIBILITIES = {
        # Устройство имеет светящиеся элементы
        # Фразы:
        #  Алиса, включи свет.
        #  Алиса, выключи свет.
        #  Алиса, прибавь яркость света.
        #  Алиса, сделай свет теплее.
        "devices.types.light": [
            "devices.capabilities.on_off",
            "devices.capabilities.color_setting",
            "devices.capabilities.range",
            "devices.capabilities.toggle",
        ],
        # Socket can be changed to light
        "devices.types.socket": [
            "devices.capabilities.on_off",
            "devices.capabilities.toggle",
        ],
        # Выключатель
        # Алиса, включи переключатель.
        # Алиса, включи выключатель.
        "devices.types.switch": [
            "devices.capabilities.on_off",
            "devices.capabilities.toggle",
        ],
        # Сенсор
        "devices.types.sensor": [],
    }

    capability = None

    def __init__(self, capability, resolve=None, **kwargs):
        self.capability = get_capability_by_name(capability, **kwargs)
        assert self.capability, "capability not found %s" % capability
        self.resolve = resolve
        
    def validate(self,device_type:str):
        """ Valiidate capability supported by device_type """
        if str(self.capability) not in self.CAPIBILITIES[device_type]:
            return False
        return True

    def __iter__(self):
        yield "type", 'devices.capabilities.' + str(self.capability.name)
        
        # State of capability after query driver / action
        # Ex of state : "state": { "instance": "on","value": true}
        # Ex2 of action : "state": {"instance": "on", "action_result": {"status": "DONE"}} 
        if state := self.get_state():
            yield 'state',dict(state)
        else:
            # otherwise send descriptor
            if not self.capability.retrievable:        
                yield "retrievable", self.capability.retrievable
            if  self.capability.reportable:
                yield "reportable", self.capability.reportable
            yield "parameters", dict(self.capability.get_params())

    def __str__(self):
        return json.dumps({self.capability.name: self.capability.to_dict()})

    @property
    def name(self):
        return self.capability.name

class DeviceProperty(StatableValue):
    PROPERTIES = {
        # Format : name : [[float][event]]
        "devices.types.socket": [["amperage", "power", "voltage"], []],
        "devices.types.switch": [["amperage", "power", "voltage"], []],
        "devices.types.sensor": [
            [
                "battery_level",
                "co2_level",
                "humidity",
                "illumination",
                "pressure",
                "temperature",
                "tvoc",
                "water_level",
            ],
            [
                "battery_level",
                "button",
                "gas",
                "motion",
                "open",
                "smoke",
                "vibration",
                "water_leak",
            ],
        ],
    }

    def __init__(self, name, resolve, params):
        prop_class  = get_property_by_name(name)
        assert prop_class, "Property class not found %s" % (name)
        self.prop = prop_class.with_params(params)
        self.resolve = resolve

    def __iter__(self):
        yield "type", "devices.properties." + str(self.prop.ptype)
        if self.prop.state:
            yield "state", self.prop.state
        else:
            yield "retrievable", self.prop.retrievable
            yield "reportable", self.prop.reportable
            yield "parameters", {"instance": self.prop.name, "unit": self.prop.units}

    def __str__(self):
        return json.dumps({self.prop.name: self.prop.ptype})

    @property
    def name(self):
        return self.prop.name

class YandexDevice(Device):
    """ Database and API device representation handler """

    device_id: str = None
    name: str = None
    description: str = None
    room: str = None
    device_type: str =  None
    capabilities: list = None
    properties: list = None
    device_info: DeviceInfo = None
    custom_data: dict = None
    device : Device = None

    def __init__(
        self,
        device_id: str,
        name: str,
        device_type: str,
        description: str = None,
        room: str = None,
        capabilities:list = None,
        properties: list = None,
        device_info: DeviceInfo = None, 
        custom_data: dict = None,
    ):
        self.device_id = str(device_id)
        self.name = name
        self.description = description
        self.room = room
        self.device_type = device_type
        self.capabilities = capabilities
        self.properties = properties
        self.device_info = device_info
        self.custom_data = custom_data
        if custom_data:
            self.device = Device(**custom_data)

    def __iter__(self):
        yield "id", self.device_id
        if self.name:
            yield "name", self.name
        if self.device_type:
            yield "type", self.device_type
        if self.description:
            yield "description", self.description
        if self.room:
            yield "room", self.room
        if self.capabilities:
            yield "capabilities", [dict(c) for c in self.capabilities]
        #if self.properties:
        #    yield "properties", [dict(p) for p in self.properties]
        if self.device_info:
            yield "device_info", dict(self.device_info)
        if self.custom_data:
            yield "custom_data", self.custom_data


    def resolve(self,params=None):
        """Resolves all unresolved properties/capabilities for device

        Args:
            params (dict, optional): driver parameters . Defaults to None.
        """

        def resolve_all(prop:list): 
            if prop:
                for p in prop:
                    if p.resolve:
                        logger.info("dev[%s]Resolve param %s",self.device_id,p.name)
                        p.set_result(self.device.action(**dict(p.resolve),action_params=params))

        resolve_all(self.capabilities)
        resolve_all(self.properties)


class YandexDeviceBuilder:
    capabilities: DeviceCapability = None
    properties: DeviceProperty = None
    device_info: DeviceInfo = None
    device_type: str = None
    custom_data: dict = None
    device_id: int = 0
    device_name: str = None
    room : str = None
    description: str = None

    def __init__(
        self,
        device_id: int,
        device_type: str=None,
    ):
        self.device_id = device_id
        self.device_type = device_type

    def with_room(self,room):
        self.room = room
        return self

    def with_name(self,name):
        self.device_name = name
        return self

    def with_description(self,description):
        self.description = description
        return self

    def with_custom_data(self, custom_data):
        self.custom_data = custom_data
        return self

    def with_capabilities(self, capabilities: dict):
        if capabilities:
            self.capabilities = [
                DeviceCapability(c, **p)
                for c, p in capabilities.items()
            ]
        return self

    def with_properties(self, properties: dict):
        if properties:
            self.properties = [
                DeviceProperty(p,**t)
                for p, t in properties.items()
            ]
        return self

    def with_device_info(self, device_info: dict):
        if isinstance(device_info, dict):
            self.device_info = DeviceInfo(**device_info)
        return self

    def build(self):
        return YandexDevice(
            self.device_id,
            self.device_name,
            self.device_type,
            self.description,
            self.room,
            self.capabilities,
            self.properties,
            self.device_info,
            self.custom_data,
        )

