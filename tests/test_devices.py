import sys
import logging

# Project lib path
sys.path.append("./lib")
# srvlet lib common
sys.path.append("..")

import unittest
from devices import Device, get_action_by_name
from drivers import DeviceDriver, register_driver
from devices.actions import DeviceAction


logger = logging.getLogger(__name__)


class MockDriver(DeviceDriver):
    name = 'mock'
    params = None

    def reset(self):
        self.params = None
    
    def action(self,**kwargs):
        logger.info("Process action %s",kwargs)
        self.params = kwargs

mock_driver = MockDriver()
register_driver(mock_driver)


class TestActions(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    def test_action_on_off(self):
        """Test action on_off"""
        action_data = {'data':['10965772,24','10965773,24']}
        action = get_action_by_name('on_off',**action_data)
        action_request = action.request('on',True)
        self.assertEqual(action_request['param'],'on_off')
        self.assertEqual(action_request['value'],'10965772,24')
        action_request = action.request('on',False)
        self.assertEqual(action_request['param'],'on_off')
        self.assertEqual(action_request['value'],'10965773,24')


    def test_action_on_off_toggle(self):
        """Test action on_off toggle"""
        action_data = {'data':'10965772,24'}
        action = get_action_by_name('on_off',**action_data)
        action_request = action.request('on',True)
        self.assertEqual(action_request['param'],'on_off')
        self.assertEqual(action_request['value'],'10965772,24')
        action_request = action.request('on',False)
        self.assertEqual(action_request['param'],'on_off')
        self.assertEqual(action_request['value'],'10965772,24')


    def test_action_range(self):
        """Test action range"""
        action_data = {'data':'10965772,24'}
        action = get_action_by_name('range',**action_data)
        action_request = action.request('up',1)
        self.assertEqual(action_request['param'],'up')
        self.assertEqual(action_request['value'],'10965772,24')
        action_request = action.request('on',False)
        self.assertEqual(action_request['param'],'on_off')
        self.assertEqual(action_request['value'],'10965772,24')





class TestDevices(unittest.TestCase):


    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    def test_load_device(self):
        """Test load device data """

        # Device custom_data from integration
        device_data = {"driver":"mock", 'params':{"topic":"/rf/315"},'actions': {"on_off":{"data":"10965772,24"}}}
        device = Device(**device_data)

        # Check device to datbase format translation
        device_dict_data = dict(device)

        self.assertEqual(str((device_dict_data['driver'])),'mock')
        self.assertEqual((device_dict_data['params']),device_data['params'])
        self.assertEqual((device_dict_data['actions']),device_data['actions'])


    def test_device_on(self):
        """Test actions device """
        # Device custom_data from integration
        device_data = {"driver":"mock", 'params':{"topic":"/rf/315"},'actions': {"on_off":"10965772,24"}}
        device: Device = Device(**device_data)
        mock_driver.reset()
        device.action('on_off','on',True)
        self.assertEqual(mock_driver.params['topic'],"/rf/315")
        self.assertEqual(mock_driver.params['data'],"10965772,24")

