"""Bridge the input from Human API into Device Cloud streams"""
import json

from dc import DeviceCloud, DataPoint
from cwear.db.model import DatabaseManager
from humanapi import HumanAPI
import logging

logger = logging.getLogger('bridge')


# Description of each of the batches that we handle and the keys for each
# that we should process and use.  For all, we handle the "document" case
# but beyond that we handle by key.
BATCHES = {
    "activities": {
        "keys": {
            "type": "string",
            "startTime": {
                "type": "string",
                "units": "ISO8601"
            },
            "endTime": {
                "type": "string",
                "units": "ISO8601"
            },
            "duration": {
                "type": "integer",
                "units": "seconds",
            },
            "distance": {
                "type": "integer",
                "unit": "meters",
            },
            "steps": "integer",
            "calories": "integer",
            "timeZone": "string",
            "sourceData": "string",
            "timeSeries": "string",  # object
            "updatedAt": {
                "type": "string",
                "units": "ISO8601"
            },
        }
    }
}


class HumanAPIStreamWriter(object):
    def __init__(self):
        self._writes = []

    def write(self, user_id, endpoint, path, **kwargs):
        fullpath = "/human/{}/{}/{}".format(user_id, endpoint, path)
        self._writes.append(DataPoint(fullpath, **kwargs))

    def get_writes(self):
        return self._writes

    def get_writes_by_path(self):
        writes_by_path = {}
        for write in self._writes:
            writes_by_path.setdefault(write.path, []).append(write)
        return writes_by_path


class HumanApiDeviceCloudBridge(object):
    def __init__(self):
        self._db_manager = DatabaseManager()
        self._dc = DeviceCloud("connectedwearables", "Cwear12$")
        self._hapi = HumanAPI(self._db_manager)

    def update(self):
        """Update the bridge"""

        stream_writer = HumanAPIStreamWriter()

        for endpoint in BATCHES:
            data = self._hapi.get_batch(endpoint)

            try:
                self.process_batch_for_endpoint(endpoint, data, stream_writer)
            except ValueError, e:
                logger.warn(e.message)
            else:
                for path, writes in stream_writer.get_writes_by_path().items():
                    self._dc.batch_stream_write(path, writes)

    def process_batch_for_endpoint(self, endpoint, batch, stream_writer):
        endpoint_spec = BATCHES.get(endpoint)
        for event in batch:
            datum_id = event.get("id")
            user_id = event.get("userId")
            created_at = event.get("createdAt")  # TODO: parse ISO8601 dt

            # write out full "document" to datastreams
            stream_writer.write(
                user_id, endpoint, "document", description=datum_id,
                unit="json", timestamp=created_at, data=json.dumps(event)
            )

            for key, key_spec in endpoint_spec.get("keys").items():
                key_tp = None
                key_unit = "unknown"
                value = event.get(key, None)
                if isinstance(key_spec, dict):
                    key_tp = key_spec.get("type")
                    key_unit = key_spec.get("unit", key_unit)
                elif isinstance(key_spec, basestring):
                    key_tp = key_spec
                else:
                    raise ValueError("Bad key_spec for endpoint %s" % endpoint)

                if value is None:  # not included, skip it
                    continue
                else:
                    stream_writer.write(
                        user_id, endpoint, key,
                        data_type=key_tp,
                        unit=key_unit,
                        data=value,
                        timestamp=created_at,
                        description=datum_id
                    )
