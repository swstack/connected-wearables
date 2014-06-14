from connection import HttpConnection, HttpException
from requests.auth import HTTPBasicAuth
import logging
import datetime
import json

logger = logging.getLogger('hapi')

APP_KEY = '0f3692b3d7fa24279e5ea2eebe31b2e7866392bd'
CLIENT_ID = '683ef654510ba8d03579f5717a90657cb21d7ebd'
CLIENT_SECRET = '2cca9bf0e4a5d1d6a4df68314a40f4b3daf9c276'


class HumanAPI(object):
    """Component used for retrieving endpoint data from Human API"""

    def __init__(self, base_url="https://api.humanapi.co/v1/apps"):
        self._conn = HttpConnection(HTTPBasicAuth(APP_KEY, ""), base_url)
        self._query_times = {}
        logger.info('Human API Started.')

    #---------------------------------------------------------------------------
    # Internal
    #---------------------------------------------------------------------------
    def _get_utc_time(self):
        """Return a UTC datetime string in the form YYYYMMDDhhmmssZ"""

        utcnow = datetime.datetime.utcnow()
        return utcnow.strftime("%Y%m%d%H%M%SZ")

    #---------------------------------------------------------------------------
    # Public
    #---------------------------------------------------------------------------
    def get_all(self):
        """Get all data for every endpoint"""

        return {
            'activities': self.get_batch('activities'),
            'heart_rates': self.get_batch('heart_rates'),
            'bmis': self.get_batch('bmis'),
            'body_fats': self.get_batch('body_fats'),
            'heights': self.get_batch('heights'),
            'weights': self.get_batch('weights'),
            'blood_glucoses': self.get_batch('blood_glucoses'),
            'blood_oxygens': self.get_batch('blood_oxygens'),
            'sleeps': self.get_batch('sleeps'),
            'blood_pressures': self.get_batch('blood_pressures'),
            'genetic_traits': self.get_batch('genetic_traits'),
            'locations': self.get_batch('locations')
        }

    def get_batch(self, endpoint):
        """Get the data for a specific endpoint"""

        endpoint_url = "/%s/users/%s" % (CLIENT_ID, endpoint)

        last_query = self._query_times.get(endpoint)
        if last_query:
            endpoint_url += ("?updated_since=%s" % last_query)

        try:
            response = self._conn.get(endpoint_url)
        except HttpException, e:
            logger.warn(e.message)
            return None
        else:
            self._query_times[endpoint] = self._get_utc_time()

        return json.loads(response.text)


if __name__ == "__main__":
    hapi = HumanAPI()
    hapi.get_batch('activities')
    hapi.get_batch('bmis')
    hapi.get_batch('activities')