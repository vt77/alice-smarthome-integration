"""
Property examples


        PROPERTIES = {
            'devices.types.socket' : {
                'devices.properties.float' : ['amperage','power','voltage']
            },
            'devices.types.switch' : {
                'devices.properties.float' : ['amperage','power','voltage']
            },
            'devices.types.sensor':{
                'devices.properties.event' : ['battery_level','button','gas','motion','open','smoke','vibration','water_leak'],
                'devices.properties.float' : ['battery_level','co2_level','humidity','illumination','pressure','temperature','tvoc','water_level']
            }
        }

        UNITS = {
            'humidity' : 'unit.percent'
        }


Yandex descriptor : 
Weather station : 
{
 "capabilities": [],
 "properties": [{
  "type": "devices.properties.float",
  "retrievable": true,
  "parameters": {
   "instance": "temperature",
   "unit": "unit.temperature.celsius"
  }
 }, {
  "type": "devices.properties.float",
  "retrievable": true,
  "parameters": {
   "instance": "humidity",
   "unit": "unit.percent"
  }
 }]
}


Yandex open/close sensor :

{
 "capabilities": [],
 "properties": [{
  "type": "devices.properties.event",
  "retrievable": true,
  "reportable": true,
  "parameters": {
   "instance": "open",
   "events": [{
     "value": "opened"
    },
    {
     "value": "closed"
    }
   ]
  }
 }]
}

"""


class Property:
    name = ""
    ptype = "float"
    retrievable = True
    reportable = False
    units = ""
    state = None

    def to_dict(self):
        data = {'type':self.ptype}
        if self.retrievable:
            data["retrievable"] = True
        if self.reportable:
            data["reportable"] = True
        return data

    @classmethod
    def with_params(cls,params):
        return cls(**params)

class PropertyAmperage(Property):
    name = "amperage"
    ptype = "float"
    units = "amper"


class PropertyPower(Property):
    name = "power"
    ptype = "float"
    units = "watt"


class PropertyVoltage(Property):
    name = "voltage"
    ptype = "float"
    units = "volt"

class PropertyTemperature(Property):
    name = "temperature"
    ptype = "float"
    units = "celsius"


def get_property_by_name(name):
    for cls in Property.__subclasses__():
        if cls.name == name:
            return cls
