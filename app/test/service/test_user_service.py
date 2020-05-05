import unittest
from app.main.service.user_service import UserService
from app.main.db import db
from app.test.conftest import flask_test_client


class TestUserService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = UserService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_user_returns_dict(self) -> None:
        new_user = self.service.save_new_user("email@email.com", "username", "password")

        assert new_user.username == "username"
        assert new_user.email == "email@email.com"
        assert new_user.password_hash != "password"

    def tearDown(self):

        db.session.remove()
        db.drop_all()
