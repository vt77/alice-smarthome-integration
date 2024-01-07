import logging
from .base import DeviceDriver, DriversErrorException

drivers_cache = {}

logger = logging.getLogger(__name__)

def get_driver_by_name(name: str):
    for cls in DeviceDriver.__subclasses__():
        if cls.name == name:
            return cls
    return None

def register_driver(driver: DeviceDriver):
        global drivers_cache
        logger.debug("Register driver %s",driver.name)
        drivers_cache[driver.name] = driver

class DriverFactory:

    @staticmethod
    def get(driver_name: str, params:dict = None) -> DeviceDriver:
        global drivers_cache
        logger.debug("Lookup driver %s",driver_name)
        if driver_name not in drivers_cache:
            raise DriversErrorException('DRIVER_NOT_FOUND')
        return drivers_cache.get(driver_name)
