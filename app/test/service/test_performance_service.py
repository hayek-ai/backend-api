import unittest

import requests_mock
from main.db import db
from main.service.user_service import UserService
from main.service.idea_service import IdeaService
from main.service.performance_service import PerformanceService
from test.conftest import flask_test_client, register_mock_iex
from main.libs.util import create_idea


class TestPerformanceService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.app = flask_test_client()
        db.create_all()

    @requests_mock.Mocker()
    def test_update_performance(self, mock) -> None:
        register_mock_iex(mock)

