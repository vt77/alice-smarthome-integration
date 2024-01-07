import sys
import json

# Project lib path
sys.path.append("./lib")

import unittest
from drivers import DriverFactory

class TestDriverBase(unittest.TestCase):
    def get_driver_by_name(self):
        device = DriverFactory('mqtt').get({'test':'data'})
        self.assertIsNotNone(driver)
        # self.assertEqual(custom_data['driver'],'mqtt')


if __name__ == "__main__":
    unittest.main()


