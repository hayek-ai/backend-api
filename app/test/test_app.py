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
        assert '/login' in self.endpoints
        assert '/upload-profile-image' in self.endpoints
        assert '/user/<username_or_id>' in self.endpoints
        assert '/user/confirm/<string:confirmation_code>' in self.endpoints
        assert '/resend-confirmation' in self.endpoints
