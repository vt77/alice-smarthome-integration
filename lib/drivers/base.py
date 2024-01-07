
from devices.actions import ActionResult, DeviceAction

class DriversErrorException(Exception):
    """Base of drivers exception"""


class DeviceDriver:
    """Action driver"""
    name = ""

    @property
    def params(self):
        return {}

    @property
    def properties(self):
        return None

    @property
    def capabilities(self):
        return None

    def action(self,action:str,param:str,value=None,data=None) -> ActionResult:
        """Take action for device

        Args:
            action (str): Action
            param (str): device param
            value (_type_, optional): param value. Defaults to None.
            data (_type_, optional): command data. Defaults to None.

        Returns:
            ActionResult: action result
        """

        return ActionResult(ActionResult.STATUS_DONE)

    def load_state(self,device_id:str):
        """ Load state for device from DB """
        states = settings['backend'].get_device_state()


    def __str__(self):
        return self.name


class ActionProcessor:

    def __init__(self,driver:str):
        self.driver = DriverFactory.get(driver)

    def on_prepare(self):
        return self

    def on_error(self):
        return self

    def on_success(self):
        return self

    def process(self,action:DeviceAction):
        return self.driver.action(**action_params)

