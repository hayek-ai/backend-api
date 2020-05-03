import unittest
import json
from app.test.conftest import flask_test_client


class TestHelloWorldController(unittest.TestCase):
    def setUp(self):
        self.client = flask_test_client()

    def test_get(self):
        response = self.client.get('/hello')
        assert json.loads(response.data) == {'hello': 'world'}
