

import logging
from drivers import DriverFactory
from .actions import DeviceAction, get_action_by_name


logger = logging.getLogger(__name__)

class Device:
    """Base class for integrations devices """ 
    params = None #general driver command params
    driver = None # Driver name
    actions = None  # Actions data for device

    def __init__(self, driver:str,params:dict=None,actions:dict=None):
        """Create device

        Args:
            driver (str): driver name ex: mqtt
            params (dict, optional): global params Ex : topic: /test/mqtt . Defaults to None.
            actions (dict, optional): List of actions . Ex: {on_off: 1234567 }. Defaults to None.
        """
        self.params = params
        self.driver = DriverFactory.get(driver)
        assert driver,f"Can't find driver for {driver}"
        self.actions = actions


    def action(self,action:str, param:str, value: str=None, action_params:dict=None):
        """Process action on device. See DeviceAction

        Args:
            action (str): action name ex: on_off
            param(str): param to change ex : on
            value (str) : value to set ex: False

        Returns:
            ActionResult: action result
        """

        action = get_action_by_name(action,**self.actions[action])
        logger.info("[DEVICE]Process action %s for param %s => %s",action.name,param,value)
        action_request = action.request(param,value)
        print(action_request)
        params = self.params or {}
        if action_params:
            params.update(action_params)
        return self.driver.action(**action_request, driver_params=params)


    def __iter__(self):
        yield 'driver', self.driver
        yield 'params', self.params
        yield 'actions', self.actions
