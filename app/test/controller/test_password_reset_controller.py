import json
import unittest
import requests_mock
from app.main.db import db
from app.main.libs.strings import get_text
from app.main.service.password_reset_service import PasswordResetService
from app.main.service.user_service import UserService
from app.test.conftest import flask_test_client, services_for_test, register_mock_mailgun


@requests_mock.Mocker()
class TestPasswordResetController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(
            services_for_test(user=UserService(), password_reset=PasswordResetService()))
        self.user_service = UserService()
        self.password_reset_service = PasswordResetService()
        db.create_all()

    def test_send_password_reset_post(self, mock) -> None:
        register_mock_mailgun(mock)
        self.user_service.save_new_user("email@email.com", "username", "password")

        # correct request
        response = self.client.post(
            "/user/reset-password",
            data=json.dumps(dict(email="email@email.com")),
            content_type="application/json")
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("password_reset_sent")

        # invalid email
        response = self.client.post(
            "/user/reset-password",
            data=json.dumps(dict(email="WRONG_EMAIL@email.com")),
            content_type="application/json")
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["errors"][0]["detail"] == get_text("not_found").format("User")

    def test_password_reset_post(self, mock) -> None:
        register_mock_mailgun(mock)
        user = self.user_service.save_new_user("email@email.com", "username", "password")
        password_reset = self.password_reset_service.save_new_password_reset(user.id)

        # correct request
        response = self.client.post(
            f"/user/reset-password/{password_reset.id}",
            data=json.dumps(dict(password="new_password")),
            content_type="application/json")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("password_changed")
        assert user.check_password("new_password") is True

        # wrong link/code
        response = self.client.post(
            "/user/reset-password/WRONG_CODE",
            data=json.dumps(dict(password="different_password")),
            content_type="application/json")
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data["errors"][0]["detail"] == get_text("not_found").format("Password Reset")
        assert user.check_password("different_password") is False

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()