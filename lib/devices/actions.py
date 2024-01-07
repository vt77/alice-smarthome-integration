class DeviceAction:
    """Handle requet to change device capability parameter"""

    name = None
    param = None
    value = None

    def __init__(self,data):
        self.data = data

    def __iter__(self):
        yield 'param',self.param
        yield 'value',self.value

    def request(self,param:str,value:str):
        """Create device change request for driver

        Args:
            param (str): parameter 
            value (str): new value

        Returns:
            dict: request params
        """

        return {
            'param': param,
            'value': value          
        }



class DeviceActionOnOff(DeviceAction):
    name = 'on_off'

    def __init__(self,data):
        if isinstance(data,list):
            switch_data  =  data[0:2]
        else: 
            switch_data = [data]
        super(DeviceActionOnOff, self).__init__(switch_data)


    def request(self,param:str,value):
        """Create on_off request

        Args:
            param (str): should be always 'on'
            value (bool): True/False 

        Returns:
            dict : action request
        """

        action_value = self.data[0]
        if len(self.data) == 2 and not value: 
            # Differnt on and off values, use second value for off command
            action_value = self.data[1]

        return {
            'param': self.name,
            'value': action_value
        }



class DeviceActionRange(DeviceAction):
    name = 'range'
    value = 0
    relative = False 

    def __init__(self,data):
        # data in format : [up_cmd,down_cmd,set_cmd]
        # Example : [0,0,123344] - Only set supported
        super(DeviceActionRange, self).__init__(data)

    def request(self,param:str,value:int,relative:bool=False):
        """Create range request

        Args:
            param (str): should be always 'range'
            value (int): value to set
            relative (bool): set realtive to current state

        Returns:
            dict : action request
        """

        return {
            'param': self.param,
            'value': self.data[0]
        }


def get_action_by_name(name, **kwargs):
    for cls in DeviceAction.__subclasses__():
        if cls.name == name:
            return cls(**kwargs)

class ActionResult():

    status: str = None
    error_code = None
    error_message = None

    STATUS_DONE = "DONE"
    STATUS_ERROR = "ERROR"

    param = None

    def __init__(self,param,status,error_code=None,error_message=None):
        self.param = param
        self.status = status
        self.error_code = error_code
        self.error_message = error_message

    def __iter__(self):
        yield 'status', self.status
        if self.error_code:
            yield 'error_code', self.error_code
        if self.error_code:
            yield 'error_message', self.error_message


    def __str__(self):
        return f"(ActionResult) Param : {self.param} Status : {self.status}"



class QueryResult():
    value = 1234