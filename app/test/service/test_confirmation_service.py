import unittest
import requests_mock
from main.service.confirmation_service import ConfirmationService
from main.service.user_service import UserService
from main.db import db
from test.conftest import flask_test_client
from test.conftest import register_mock_mailgun


@requests_mock.Mocker()
class TestConfirmationService(unittest.TestCase):
    def setUp(self) -> None:
        self.confirmation_service = ConfirmationService()
        self.user_service = UserService()
        self.app = flask_test_client()
        db.create_all()

    def test_send_confirmation_email(self, mock) -> None:
        register_mock_mailgun(mock)
        self.user_service.save_new_user("email@email.com", "user1", "password")
        response = self.confirmation_service.send_confirmation_email(1)
        assert response.status_code == 200

    def test_get_confirmation_by_id(self, mock) -> None:
        register_mock_mailgun(mock)
        self.user_service.save_new_user("email@email.com", "username", "password")
        confirmation = self.confirmation_service.get_confirmation_by_id(1)
        assert confirmation.id == 1
        assert len(confirmation.code) == 6
        assert confirmation.is_expired is False

        # if confirmation doesn't exist
        confirmation = self.confirmation_service.get_confirmation_by_id(2)
        assert confirmation is None

    def test_force_to_expire(self, mock) -> None:
        register_mock_mailgun(mock)

        new_user = self.user_service.save_new_user("email@email.com", "username", "password")
        confirmation = new_user.most_recent_confirmation
        assert confirmation.is_expired is False
        self.confirmation_service.force_to_expire(confirmation.id)
        assert confirmation.is_expired is True

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
