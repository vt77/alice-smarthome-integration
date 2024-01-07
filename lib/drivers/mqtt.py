import logging
from typing import Union, List
from .base import ActionDriver, DriversErrorException

logger = logging.getLogger(__name__)


class DriverMqtt(ActionDriver):
    name = "mqtt"

    class SenderParameters:
        payload: Union[str, List[str]] = None

        def __init__(self, params: dict):
            if isinstance(params["payload"], list):
                self.on_off = True
                self.payload = params["payload"]

            if isinstance(params["payload"], str):
                self.on_off = False
                self.payload = str(params["payload"])

            assert self.payload, "payload missing or wrong type (str|list)"

        def __iter__(self):
            yield "payload", self.payload

    def __init__(
        self,
        action: str,
        params: dict,
    ):
        """Creates MQTT action driver

        Args:
            action (str): Action string [rfsend,irsend]
            params (dict): action parameters
        """
        self.action = action
        self.action_params: DriverMqtt.SenderParameters = self.build_action_params(
            action, params
        )
        self.state = None

    def build_action_params(self, action: str, params: dict) -> SenderParameters:
        """Validates and parses action parameters

        Args:
            action (str): action string ['rfsend','irsend']
            params (dict): parameters

        Raises:
            DriversErrorException: On parameters error

        Returns:
            (SenderParameters) parsed parameters

        """
        if action == "rfsend":
            self.freq = params.get("freq")
            assert self.freq, "Missing freq parameter"
            self.topic = f"rf/{self.freq}"
            return DriverMqtt.SenderParameters(params)

        if action == "irsend":
            self.proto = params.get("proto")
            assert self.proto, "Missing proto parameter"
            self.topic = f"ir/{self.proto}"
            return DriverMqtt.SenderParameters(params)

        raise DriversErrorException(f"Unknown action {action}")

    def action(self,device_id:str,action:str,param:str,value) -> dict:
        """Take action on device
        Args:
            device_id (str): device_id to take action
            action (str): Ex: on_off, color
            param (str): action params Ex: 'on'
            value (Any) : action param value Ex: False
        Returns:
            dict: Capability with action_result field
        """
        action_result = {
            "status": "DONE"
         }

        action_result = {
            "status": "ERROR",
            "error_code": "INVALID_ACTION",
            "error_message": "action not supportred"
        }
