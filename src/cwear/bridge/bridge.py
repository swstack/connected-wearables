"""Bridge the input from Human API into Device Cloud streams"""

from dc import DeviceCloud
from humanapi import HumanAPI
import logging

logger = logging.getLogger('bridge')


class HumanApiDeviceCloudBridge(object):
    def __init__(self):
        self._dc = DeviceCloud("connectedwearables", "Cwear12$")
        self._hapi = HumanAPI()

    def start(self):
        logger.info('Bridge Started.')
