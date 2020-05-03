import unittest
from app.main import create_app
from app.test.conftest import flask_test_client

flask_client = flask_test_client()


class TestEndpointsConfiguration(unittest.TestCase):
    def setUp(self):
        endpoints = []
        for rule in flask_client.application.url_map.iter_rules():
            endpoints.append(str(rule))
        self.endpoints = endpoints

    def test_config(self):
        assert not create_app('development').testing
        assert create_app('testing').testing

    def test_hello_endpoint_configured(self):
        assert '/hello' in self.endpoints
