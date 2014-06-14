from cwear.test.test_utilities import HumanApiBase
import unittest

HUMANAPI_URL = "https://api.humanapi.co/v1/apps"


EXAMPLE_ACTIVITIES = [
    {
        "id": "539b60a3e186de9b7f00ce1b",
        "userId": "537ac6902f143657390c766e",
        "startTime": "2014-06-13T12:50:00.000Z",
        "endTime": "2014-06-13T20:28:00.000Z",
        "type": "unknown",
        "source": "jawbone",
        "duration": 0,
        "distance": 2654,
        "steps": 3210,
        "calories": 154.63800016,
        "sourceData": {},
        "createdAt": "2014-06-13T20:35:47.475Z",
        "updatedAt": "2014-06-13T20:35:47.475Z"
    }
]


class TestHumanApi(HumanApiBase):
    def test_get_activities(self):
        self.prepare_json_response('GET', '/activities', EXAMPLE_ACTIVITIES)
        data = self.hapi.get_batch('activities')
        self.assertEqual(len(data), 1)


if __name__ == "__main__":
    unittest.main()
