import unittest
import json
from app.test.conftest import flask_test_client, services_for_test
from app.main.service.register_user_service import RegisterUserService


class TestUserRegisterController(unittest.TestCase):
    def setUp(self):
        self.client = flask_test_client(services_for_test(register_user=RegisterUserService()))

    def test_post(self):
        response = self.client.post('/register', data=dict(
            email='email@email.com',
            username='username',
            password='password'
        ))
        assert json.loads(response.data) == {
            'email': 'email@email.com',
            'username': 'username',
            'password': 'password'
        }

    def test_extra_params_returns_400(self):
        response = self.client.post('/register', data=dict(
            email='email@email.com',
            username='username',
            password='password',
            extraParam="extraParam"
        ))

        assert response.status_code == 400
        assert json.loads(response.data) == {'error': 'Wrong input params'}
