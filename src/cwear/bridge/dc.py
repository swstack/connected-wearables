from xml.etree import ElementTree
from connection import HttpConnection
from requests.auth import HTTPBasicAuth
import logging

DATA_POINT_TEMPLATE = """\
<DataPoint>
   <data>{data}</data>
   <streamId>{stream}</streamId>
</DataPoint>
"""

DATA_STREAM_TEMPLATE = """\
<DataStream>
   <streamId>{id}</streamId>
   <dataType>{data_type}</dataType>
   <description>{description}</description>
   <dataTtl>{data_ttl}</dataTtl>
   <rollupTtl>{rollup_ttl}</rollupTtl>
</DataStream>
"""

ONE_DAY = 86400  # in seconds


logger = logging.getLogger('dc')


class StreamException(Exception):
    """Base class for stream related exceptions"""


class NoSuchStreamException(StreamException):
    """Failure to find a stream based on a given id"""


class DeviceCloud(object):
    def __init__(self, username, password, base_url="https://login.etherios.com"):
        self._conn = HttpConnection(HTTPBasicAuth(username, password), base_url)
        logger.info('DeviceCloud Started.')

    #---------------------------------------------------------------------------
    # Stream API
    #---------------------------------------------------------------------------
    def create_data_stream(self, stream_id, data_type, description, data_ttl, rollup_ttl):
        """Create and return a DataStream object"""

        if not description:
            description = ""

        data = DATA_STREAM_TEMPLATE.format(id=stream_id,
                                           description=description,
                                           data_type=data_type,
                                           data_ttl=data_ttl,
                                           rollup_ttl=rollup_ttl)

        self._conn.post("/ws/DataStream", data)
        logger.info("Data stream (%s) created successfully", stream_id)
        stream = DataStream(stream_id, data_type, description, data_ttl, rollup_ttl, self._conn)
        self._add_stream_to_cache(stream)
        return stream

    def get_streams(self, cached):
        """Return a cached (or not) list of available streams"""

        if (not cached) or (not self._streams_cache):
            self._load_streams()

        return self._streams_cache.values()

    def get_stream(self, stream_id, cached):
        """Return a stream with a given `stream_id` or None"""

        if (not cached) or (not self._streams_cache):
            self._load_streams()

        return self._streams_cache.get(stream_id)

    def stream_write(self, stream_id, data):
        """If the stream exists, write some data to it using a DataPoint"""

        stream = self._streams_cache.get(stream_id)
        if stream:
            return stream.write(data)

        raise NoSuchStreamException("No stream with id %s", stream_id)

    def stream_read(self, stream_id):
        """If the stream exists, read one or more DataPoints from a stream"""

        stream = self._streams_cache.get(stream_id)
        if stream:
            return stream.read()

        raise NoSuchStreamException("No stream with id %s", stream_id)

    def delete_stream(self, stream_id):
        """Delete a DataStream with a given `stream_id`"""
        self._conn.delete("/ws/DataStream/%s" % stream_id)


class DataStream(object):
    """Encapsulation of a DataStream's methods and attributes"""

    @classmethod
    def from_etree(cls, root, conn):
        stream_id = root.find("streamId").text
        data_type = root.find("dataType").text.lower()
        description = root.find("description").text
        data_ttl = root.find("dataTtl").text
        rollup_ttl = root.find("rollupTtl").text
        return cls(stream_id, data_type, description, data_ttl, rollup_ttl, conn)

    def __init__(self, stream_id, data_type, description, data_ttl, rollup_ttl, conn):
        self._stream_id = stream_id
        self._description = description
        self._data_type = data_type
        self._data_ttl = data_ttl
        self._rollup_ttl = rollup_ttl
        self._conn = conn

    def __repr__(self):
        return "DataStream(%s, %s)" % (self._stream_id, self._data_type)

    def get_stream_id(self):
        return self._stream_id

    def get_data_type(self):
        return self._data_type

    def get_description(self):
        return self._description

    def get_data_ttl(self):
        return self._data_ttl

    def get_rollup_ttl(self):
        return self._rollup_ttl

    def get_current_value(self):
        """Return the most recent DataPoint value written to a stream"""

        response = self._conn.get("/ws/DataStream/%s" % self._stream_id)
        data_point = ElementTree.fromstring(response.content)
        current_value = data_point.find(".//currentValue")
        if current_value:
            return current_value.find(".//data").text
        else:
            return None

    def write(self, data):
        """Write some raw data to a stream using the DataPoint API

        Type checking/conversion will be applied here.
        """

        # TODO: Handle optional DataPoint arguments

        data = DATA_POINT_TEMPLATE.format(data=data, stream=self._stream_id)
        self._conn.post("/ws/DataPoint/%s" % self._stream_id, data)

    def read(self):
        """Read one or more DataPoints from a stream"""

        # TODO: Implement me