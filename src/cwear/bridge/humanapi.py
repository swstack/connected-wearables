from connection import HttpConnection
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger('hapi')

APP_KEY = '0f3692b3d7fa24279e5ea2eebe31b2e7866392bd'
CLIENT_ID = '683ef654510ba8d03579f5717a90657cb21d7ebd'
CLIENT_SECRET = '2cca9bf0e4a5d1d6a4df68314a40f4b3daf9c276'


class HumanAPI(object):
    def __init__(self, base_url="https://api.humanapi.co/v1"):
        self._conn = HttpConnection(HTTPBasicAuth(APP_KEY), base_url)
        logger.info('Human API Started.')
