import unittest
import json
from app.test.conftest import flask_test_client
from app.main.db import db


class TestHealthController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client()
        db.create_all()

    def test_health_get(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["status"] == "working"
