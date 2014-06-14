from cwear.bridge.humanapi import HumanAPI, CLIENT_ID
import unittest
import json
import httpretty


class HumanApiBase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()
        self.hapi = HumanAPI()

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def prepare_response(self, method, path, data, status=200):
        # TODO:
        #   Should probably assert on more request headers and
        #   respond with correct content type, etc.

        url = "https://api.humanapi.co/v1/apps/%s/users%s" % (CLIENT_ID, path)

        httpretty.register_uri(method,
                               url,
                               data,
                               status=status)

    def prepare_json_response(self, method, path, data, status=200):
        self.prepare_response(method, path, json.dumps(data), status=status)
