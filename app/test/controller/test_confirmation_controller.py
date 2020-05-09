import json
import unittest

from app.main.db import db
from app.main.libs.strings import get_text
from app.main.service.confirmation_service import ConfirmationService
from app.main.service.user_service import UserService
from app.test.conftest import flask_test_client, services_for_test, register_mock_mailgun, requests_session

register_mock_mailgun(requests_session())


class TestConfirmationController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(
            services_for_test(user=UserService(), confirmation=ConfirmationService()))
        self.user_service = UserService()
        self.confirmation_service = ConfirmationService()
        db.create_all()

    def login(self, username, password) -> str:
        """Logs user in and returns accessToken"""
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password=password
        )), content_type='application/json')
        login_data = json.loads(response.data)
        return login_data["accessToken"]

    def test_confirm_user(self) -> None:
        user = self.user_service.save_new_user("michaelmcguiness123@gmail.com", "username", "password")
        assert user.is_confirmed is False
        code = user.most_recent_confirmation.code

        access_token = self.login("username", "password")

        # incorrect confirmation code
        response = self.client.get(
            f'/user/confirm/{000}',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = json.loads(response.data)
        assert data['errors'][0]['detail'] == get_text("incorrect_confirmation_code")
        assert response.status_code == 400
        assert user.is_confirmed is False

        # confirmation code expired
        self.confirmation_service.force_to_expire(user.most_recent_confirmation.id)
        response = self.client.get(
            f'/user/confirm/{code}',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = json.loads(response.data)
        assert data['errors'][0]['detail'] == get_text("confirmation_code_expired")
        assert response.status_code == 400
        assert user.is_confirmed is False

        # resend confirmation email
        response = self.client.post(
            '/resend-confirmation',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = json.loads(response.data)
        assert data["message"] == get_text("confirmation_resend_successful")
        assert response.status_code == 201

        # confirmation works normally
        new_code = user.most_recent_confirmation.code
        response = self.client.get(
            f'/user/confirm/{new_code}',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = json.loads(response.data)
        assert data["message"] == get_text("user_confirmed")
        assert response.status_code == 200
        assert user.is_confirmed is True

        # user is already confirmed
        response = self.client.get(
            f'/user/confirm/{code}',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = json.loads(response.data)
        assert data["errors"][0]['detail'] == get_text("user_already_confirmed")
        assert response.status_code == 400
        assert user.is_confirmed is True

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
