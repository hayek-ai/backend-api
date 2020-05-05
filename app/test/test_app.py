import unittest
from app.test.conftest import flask_test_client

flask_client = flask_test_client()


class TestEndpointsConfiguration(unittest.TestCase):
    def setUp(self):
        endpoints = []
        for rule in flask_client.application.url_map.iter_rules():
            endpoints.append(str(rule))
        self.endpoints = endpoints

    def test_register_endpoint_configured(self):
        assert '/register' in self.endpoints
