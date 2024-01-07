import sys
import unittest
import logging

# Project lib path
sys.path.append("./lib")

from integrations.yandex import YandexDeviceBuilder,YandexRequest
from drivers import DeviceDriver, register_driver
from devices import ActionResult

logger = logging.getLogger(__name__)


class MockDriver(DeviceDriver):
    name = 'mock'
    params = None

    def reset(self):
        self.params = None
    
    def action(self,**kwargs):
        logger.info("Process action %s",kwargs)
        self.params = kwargs
        return ActionResult('on',ActionResult.STATUS_DONE)

mock_driver = MockDriver()
register_driver(mock_driver)

class TestCapabilities(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    def test_capability_onoff(self):
        """Test capabilty on_off with reportable non-default and parameter"""

        capability = {'on_off':{'split':True,'reportable':True}}
        builder = (
                YandexDeviceBuilder('test-1234', 'devices.types.light')
                .with_name('Lamp1')
                .with_capabilities(capability)
        )
        device = dict(builder.build())

        self.assertEqual(device['id'],'test-1234')
        self.assertEqual(device['type'],'devices.types.light')
        self.assertEqual(device['capabilities'][0]['type'],'devices.capabilities.on_off')
        self.assertEqual(device['capabilities'][0]['parameters']['split'],True)
        self.assertEqual(device['capabilities'][0]['reportable'],True)


    def test_capability_onoff_with_state(self):
        """Test capabilty on_off with state (after query by driver)"""

        capability = {'on_off':{'split':True,'reportable':True}}
        builder = (
                YandexDeviceBuilder('test-1234', 'devices.types.light')
                .with_name('Lamp1')
                .with_capabilities(capability)
        )
        device = dict(builder.build())

        self.assertEqual(device['id'],'test-1234')
        self.assertEqual(device['type'],'devices.types.light')
        self.assertEqual(device['capabilities'][0]['type'],'devices.capabilities.on_off')
        self.assertEqual(device['capabilities'][0]['parameters']['split'],True)
        self.assertEqual(device['capabilities'][0]['reportable'],True)


    def test_capability_onoff_with_state_change(self):
        """Capability on_off with state change 
        """
        capability = {'on_off':{'split':True,'reportable':True}}
        action_request = [
              {
                 "type": "devices.capabilities.on_off",
                 "state": {
                   "instance": "on",
                   "value": False
                 }
              }
            ]

        builder = (
                YandexDeviceBuilder('test-1234', 'devices.types.light')
                .with_name('Lamp1')
                .with_capabilities(YandexRequest.build_action_request(capability,action_request))
                .with_custom_data({'driver':'mock','actions':{'on_off':{'data':'test_data'}}})
        )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
        d = builder.build()
        d.resolve()
        device = dict(d)
        print(device)

        #self.assertEqual(device['id'],'test-1234')
        #self.assertEqual(device['type'],'devices.types.light')
        #self.assertEqual(device['capabilities'][0]['type'],'devices.capabilities.on_off')
        #self.assertEqual(device['capabilities'][0]['parameters']['split'],True)
        #self.assertEqual(device['capabilities'][0]['reportable'],True)


class TestIntegrationYandex(unittest.TestCase):
                                                            
                                                            
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    def test_build_simple_device(self):
        builder = (
            YandexDeviceBuilder('test-1234', 'devices.types.light')
            .with_name('Lamp1')
            .with_room('Living room')
            .with_description('First lamp')
            .with_custom_data({"driver":"mqtt",'params':{"topic":"/rf/315"},"actions":{"on_off":{"data":"10965763,24"}}})
            .with_properties({})
            .with_capabilities({"devices.capabilities.on_off":{'split':True}})
            .with_device_info({"manufacturer":"vt77", "model":"rf315sw", "hw_version":"0.1", "sw_version":"0.1"})
        )
        device =  builder.build()
        print(dict(device))
        self.assertEqual(device.room,'Living room')

