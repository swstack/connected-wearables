"""Bridge the input from Human API into Device Cloud streams"""
import json
import os
import yaml

from dc import DeviceCloud, DataPoint
from cwear.db.model import DatabaseManager
from humanapi import HumanAPI
import logging

logger = logging.getLogger('bridge')

THIS_DIR = os.path.dirname(__file__)


class HumanAPIStreamWriter(object):
    def __init__(self):
        self._writes = []

    def write(self, user_id, endpoint, path, **kwargs):
        fullpath = "/human/{}/{}/{}".format(user_id, endpoint, path)
        self._writes.append(DataPoint(fullpath, **kwargs))

    def get_datapoints_written(self):
        return self._writes

    def get_datapoints_written_by_path(self):
        writes_by_path = {}
        for write in self._writes:
            writes_by_path.setdefault(write.path, []).append(write)
        return writes_by_path


class HumanApiDeviceCloudBridge(object):
    def __init__(self):
        self._db_manager = DatabaseManager()
        self._dc = DeviceCloud("connectedwearables", "Cwear12$")
        self._hapi = HumanAPI(self._db_manager)
        self._mapping_cache = None

    def get_humanapi_mapping_metadata(self):
        if self._mapping_cache is None:
            with open(os.path.join(THIS_DIR, "humanapi_mapping.yml"), "rb") as f:
                self._mapping_cache = yaml.load(f)
        return self._mapping_cache

    def update(self):
        """Update the bridge"""

        stream_writer = HumanAPIStreamWriter()

        for endpoint in self.get_humanapi_mapping_metadata().keys():
            data = self._hapi.get_batch(endpoint)

            try:
                self.process_batch_for_endpoint(endpoint, data, stream_writer)
            except ValueError, e:
                logger.warn(e.message)

        # after we have gathered data up for all endpoints, then batch writes out to
        # the device cloud
        datapoints_written = stream_writer.get_datapoints_written()
        if len(datapoints_written) > 0:
            self._dc.batch_stream_write(datapoints_written)

    def process_batch_for_endpoint(self, endpoint, batch, stream_writer):
        endpoint_spec = self.get_humanapi_mapping_metadata().get(endpoint)
        endpoint_timestamp_field = endpoint_spec.get("timestamp_field", "createdAt")
        for event in batch:
            datum_id = event.get("id")
            user_id = event.get("userId")
            timestamp = event.get(endpoint_timestamp_field)  # TODO: parse ISO8601 dt?

            # write out full "document" to datastreams
            stream_writer.write(
                user_id, endpoint, "document", description=datum_id,
                unit="json", timestamp=timestamp, data=json.dumps(event)
            )

            for key, key_spec in endpoint_spec.get("forward_fields").items():
                field_type = None
                field_unit = "unknown"
                field_value = event.get(key, None)
                location = None
                if isinstance(key_spec, dict):
                    field_type = key_spec.get("type")
                    field_unit = key_spec.get("unit", field_unit)
                    unit_field = key_spec.get("unit_field")
                    if unit_field:
                        field_unit = event.get(unit_field, "unknown")
                elif isinstance(key_spec, basestring):
                    field_type = key_spec
                else:
                    raise ValueError("Bad key_spec for endpoint %s" % endpoint)

                # handle special field types
                if field_type == "datetime":  # Device Cloud does not have a type for this
                    field_type = "string"
                    field_unit = "ISO8601"

                if field_type == "boolean":
                    field_type = "integer"
                    field_unit = "boolean"
                    field_value = 1 if field_value else 0

                if field_value is None:  # not included, skip it
                    continue
                else:
                    stream_writer.write(
                        user_id, endpoint, key,
                        data_type=field_type,
                        unit=field_unit,
                        data=field_value,
                        timestamp=timestamp,
                        description=datum_id,
                        location=location,
                    )
