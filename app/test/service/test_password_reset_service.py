import unittest
import requests_mock
from main.service.password_reset_service import PasswordResetService
from main.service.user_service import UserService
from main.db import db
from test.conftest import flask_test_client
from test.conftest import register_mock_mailgun


@requests_mock.Mocker()
class TestPasswordResetService(unittest.TestCase):
    def setUp(self) -> None:
        self.password_reset_service = PasswordResetService()
        self.user_service = UserService()
        self.app = flask_test_client()
        db.create_all()

    def test_send_password_reset_email(self, mock) -> None:
        register_mock_mailgun(mock)
        user = self.user_service.save_new_user("michaelmcguiness123@gmail.com", "user1", "password")
        self.password_reset_service.save_new_password_reset(user.id)
        response = self.password_reset_service.send_password_reset_email(user.id)
        assert response.status_code == 200

    def test_get_password_reset_by_id(self, mock) -> None:
        register_mock_mailgun(mock)
        user = self.user_service.save_new_user("email@email.com", "username", "password")
        password_reset = self.password_reset_service.save_new_password_reset(user.id)
        found_password_reset = self.password_reset_service.get_password_reset_by_id(password_reset.id)
        assert found_password_reset.id == password_reset.id
        assert password_reset.is_expired is False

        # if password_reset doesn't exist
        password_reset = self.password_reset_service.get_password_reset_by_id("string")
        assert password_reset is None

    def test_force_to_expire(self, mock) -> None:
        register_mock_mailgun(mock)
        user = self.user_service.save_new_user("email@email.com", "username", "password")
        password_reset = self.password_reset_service.save_new_password_reset(user.id)
        assert password_reset.is_expired is False
        self.password_reset_service.force_to_expire(password_reset.id)
        assert password_reset.is_expired is True

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()