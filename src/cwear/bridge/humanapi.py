from connection import HttpConnection, HttpException
from requests.auth import HTTPBasicAuth
from cwear.db.model import SyncState
import logging
import datetime
import json

logger = logging.getLogger('hapi')

APP_KEY = '0f3692b3d7fa24279e5ea2eebe31b2e7866392bd'
CLIENT_ID = '683ef654510ba8d03579f5717a90657cb21d7ebd'


class HumanAPI(object):
    """Component used for retrieving endpoint data from Human API"""

    def __init__(self, db_manager, app_key, client_id, base_url="https://api.humanapi.co/v1/apps"):
        self._db_manager = db_manager
        self._app_key = app_key
        self._client_id = client_id
        self._conn = HttpConnection(HTTPBasicAuth(self._app_key, ""), base_url)
        logger.info('Human API Started.')

    #---------------------------------------------------------------------------
    # Internal
    #---------------------------------------------------------------------------
    def _fmt_time(self, dt):
        """Return a UTC datetime string in the form YYYYMMDDhhmmssZ"""

        return dt.strftime("%Y%m%d%H%M%SZ")

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

    def get_batch(self, cwear_app, endpoint):
        """Get the data for a specific endpoint"""
        db_session = self._db_manager.get_db_session()

        endpoint_url = "/%s/users/%s" % (self._client_id, endpoint)

        hapi_account_id = cwear_app.related_hapiaccount.id
        last_sync = (db_session.query(SyncState)
                     .filter_by(endpoint=endpoint, hapiaccount_id=hapi_account_id)
                     .first())
        if last_sync:
            last_sync_time = self._fmt_time(last_sync.last_sync_time)
            endpoint_url += ("?updated_since=%s" % last_sync_time)

        try:
            response = self._conn.get(endpoint_url)
        except HttpException, e:
            logger.warn(e.message)
            return None
        else:
            utcnow = datetime.datetime.utcnow()

            if last_sync:
                last_sync.last_sync_time = utcnow
            else:
                new_sync = SyncState(
                    endpoint=endpoint,
                    hapi_account_id=hapi_account_id,
                    last_sync_time=utcnow)
                db_session.add(new_sync)

            db_session.commit()

        return json.loads(response.text)
