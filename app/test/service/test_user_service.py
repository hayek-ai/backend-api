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
        assert str(type(new_user.most_recent_confirmation)) == "<class 'app.main.model.confirmation.ConfirmationModel'>"

    def test_get_all_users(self):
        self.service.save_new_user("user1@email.com", "user1", "password")
        self.service.save_new_user("user2@email.com", "user2", "password")
        self.service.save_new_user("user3@email.com", "user3", "password")

        users = self.service.get_all_users()
        assert len(users) == 3
        assert users[0].username == "user1"
        assert users[1].username == "user2"
        assert users[2].username == "user3"

    def test_get_user_by_id(self):
        self.service.save_new_user("user1@email.com", "user1", "password")
        self.service.save_new_user("user2@email.com", "user2", "password")

        user = self.service.get_user_by_id(1)
        assert user.username == "user1"
        user = self.service.get_user_by_id(2)
        assert user.username == "user2"

        # if user doesn't exist
        user = self.service.get_user_by_id(3)
        assert user is None

    def test_get_user_by_username(self):
        self.service.save_new_user("user1@email.com", "user1", "password")
        self.service.save_new_user("user2@email.com", "user2", "password")

        user = self.service.get_user_by_username("user1")
        assert user.username == "user1"
        user = self.service.get_user_by_username("user2")
        assert user.username == "user2"

        # if user doesn't exist
        user = self.service.get_user_by_username("nonexistent-username")
        assert user is None

        # make sure case insensitive
        user = self.service.get_user_by_username("USER1")
        assert user.username == "user1"

    def test_get_user_by_email(self):
        self.service.save_new_user("user1@email.com", "user1", "password")
        self.service.save_new_user("user2@email.com", "user2", "password")

        user = self.service.get_user_by_email("user1@email.com")
        assert user.username == "user1"
        user = self.service.get_user_by_email("user2@email.com")
        assert user.username == "user2"

        # if user doesn't exist
        user = self.service.get_user_by_email("nonexistent@email.com")
        assert user is None

        # make sure case insensitive
        user = self.service.get_user_by_email("USER2@email.com")
        assert user.username == "user2"

    def test_send_confirmation_email(self):
        self.service.save_new_user("michaelmcguiness123@gmail.com", "user1", "password")
        response = self.service.send_confirmation_email(1)
        assert response.status_code == 200

    def tearDown(self):
        db.session.remove()
        db.drop_all()
