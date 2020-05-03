import unittest
from app.main.service.register_user_service import RegisterUserService


class TestUserRegisterService(unittest.TestCase):
    def setUp(self):
        self.service = RegisterUserService()

    def test_register_user_returns_dict(self):
        response = self.service.register_user('email', 'username', 'password')

        assert response == {'email': 'email', 'username': 'username', 'password': 'password'}
