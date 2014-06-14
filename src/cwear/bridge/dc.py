from connection import HttpConnection
from requests.auth import HTTPBasicAuth
from StringIO import StringIO
import logging

logger = logging.getLogger('dc')


class DataPoint(object):

    def __init__(self, path, data, description=None, timestamp=None,
                 quality=None, location=None, data_type=None, unit=None):
        self.path = path
        self.data = data
        self.description = description
        self.timestamp = timestamp
        self.quality = quality
        self.location = location
        self.data_type = data_type
        self.unit = unit

    def to_xml(self):
        out = StringIO()
        out.write("<DataPoint>")
        out.write("<data>%s</data>" % self.data)
        if self.description is not None:
            out.write("<description>%s</description>" % self.description)
        if self.timestamp is not None:
            out.write("<timestamp>%s</timestamp>" % self.timestamp)
        if self.quality is not None:
            out.write("<quality>%s</quality>" % self.quality)
        if self.location is not None:
            out.write("<location>%s</location>" % self.location)
        if self.data_type:
            out.write("<streamType>%s</streamType>" % self.data_type)
        if self.unit:
            out.write("<streamUnits>%s</streamUnits>" % self.unit)
        out.write("</DataPoint>")
        return out.getvalue()


class DeviceCloud(object):
    def __init__(self, username, password, base_url="https://login.etherios.com"):
        self._conn = HttpConnection(HTTPBasicAuth(username, password), base_url)
        logger.info('DeviceCloud Started.')

    #---------------------------------------------------------------------------
    # Stream API
    #---------------------------------------------------------------------------
    def batch_stream_write(self, path, data_points):
        datapoints_out = StringIO()
        datapoints_out.write("<list>")
        for dp in data_points:
            datapoints_out.write(dp.to_xml())
        datapoints_out.write("</list>")

        dc_path = "/ws/DataPoint" + path
        self._conn.post(dc_path, datapoints_out)

        logger.info('DataPoint batch written: %s', path)
