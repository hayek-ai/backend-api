import unittest
import datetime
import requests_mock
from main.db import db
from test.conftest import flask_test_client, register_mock_iex, register_mock_mailgun
from main.service.user_service import UserService
from main.service.idea_service import IdeaService
from main.service.download_service import DownloadService
from main.model.idea import IdeaModel
from main.libs.util import create_idea


@requests_mock.Mocker()
class TestDownloadService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.download_service = DownloadService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_download_and_get_download_by_id(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        download1 = self.download_service.save_new_download(user.id, idea.id)
        assert download1.user_id == user.id
        assert download1.idea_id == idea.id
        download2 = self.download_service.save_new_download(analyst.id, idea.id)
        found_download = self.download_service.get_download_by_id(download2.id)
        assert found_download.id == download2.id

    def test_get_idea_download_count(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        time_stamp1 = datetime.datetime.utcnow()
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        self.download_service.save_new_download(user.id, idea.id)
        time_stamp2 = datetime.datetime.utcnow()
        self.download_service.save_new_download(user.id, idea.id)
        count = self.download_service.get_idea_download_count(idea.id, time_stamp1)
        assert count == 2
        count = self.download_service.get_idea_download_count(idea.id, time_stamp1, time_stamp2)
        assert count == 1
        count = self.download_service.get_idea_download_count(idea.id, time_stamp2, time_stamp2)
        assert count == 0
        count = self.download_service.get_idea_download_count(idea.id, time_stamp2)
        assert count == 1
        count = self.download_service.get_idea_download_count(idea.id)
        assert count == 2

    def test_get_user_download_count(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        time_stamp1 = datetime.datetime.utcnow()
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        self.download_service.save_new_download(user.id, idea.id)
        time_stamp2 = datetime.datetime.utcnow()
        self.download_service.save_new_download(user.id, idea.id)
        count = self.download_service.get_user_download_count(user.id, time_stamp1)
        assert count == 2
        count = self.download_service.get_user_download_count(user.id, time_stamp1, time_stamp2)
        assert count == 1
        count = self.download_service.get_user_download_count(user.id, time_stamp2, time_stamp2)
        assert count == 0
        count = self.download_service.get_user_download_count(user.id, time_stamp2)
        assert count == 1
        count = self.download_service.get_user_download_count(user.id)
        assert count == 2

    def test_get_analyst_download_count(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        time_stamp1 = datetime.datetime.utcnow()
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        self.download_service.save_new_download(user.id, idea.id)
        time_stamp2 = datetime.datetime.utcnow()
        self.download_service.save_new_download(user.id, idea.id)
        count = self.download_service.get_analyst_download_count(analyst.id, time_stamp1)
        assert count == 2
        count = self.download_service.get_analyst_download_count(analyst.id, time_stamp1, time_stamp2)
        assert count == 1
        count = self.download_service.get_analyst_download_count(analyst.id, time_stamp2, time_stamp2)
        assert count == 0
        count = self.download_service.get_analyst_download_count(analyst.id, time_stamp2)
        assert count == 1
        count = self.download_service.get_analyst_download_count(analyst.id)
        assert count == 2

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
