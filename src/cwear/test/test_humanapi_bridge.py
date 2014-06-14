import json
from cwear.bridge.bridge import HumanApiDeviceCloudBridge
from mock import Mock
import os
import unittest


class TestHumanAPIBridge(unittest.TestCase):

    def setUp(self):
        self.bridge = HumanApiDeviceCloudBridge()

    def _load_batch(self, endpoint):
        with open(os.path.join(os.path.dirname(__file__), "data", "{}.json".format(endpoint)), 'r') as f:
            return json.loads(f.read())

    def test_activities(self):
        data = self._load_batch("activities")
        stream_writer = Mock()
        self.bridge.process_batch_for_endpoint("activities", data, stream_writer)

        # There should be a write 5 * (11 + 1 - 2) = 50 times (timeSeries, timeZone are not present in this data)
        self.assertEqual(stream_writer.write.call_count, 50)



if __name__ == '__main__':
    unittest.main()
