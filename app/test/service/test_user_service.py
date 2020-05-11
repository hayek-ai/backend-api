import unittest

from app.main.db import db
from app.main.libs.s3 import S3
from app.main.libs.util import create_image_file
from app.main.service.user_service import UserService
from app.test.conftest import flask_test_client
from app.test.conftest import register_mock_mailgun, requests_session

register_mock_mailgun(requests_session())


class TestUserService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = UserService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_user(self) -> None:
        new_user = self.service.save_new_user("email@email.com", "username", "password")

        assert new_user.username == "username"
        assert new_user.email == "email@email.com"
        assert new_user.password_hash != "password"
        assert new_user.is_analyst is False
        assert str(type(new_user.most_recent_confirmation)) == "<class 'app.main.model.confirmation.ConfirmationModel'>"

        # try creating analyst
        new_analyst = self.service \
            .save_new_user("email2@email.com", "analyst", "password", is_analyst=True)
        assert new_analyst.is_analyst is True

    def test_get_all_users(self) -> None:
        self.service.save_new_user("user1@email.com", "user1", "password")
        self.service.save_new_user("user2@email.com", "user2", "password")
        self.service.save_new_user("user3@email.com", "user3", "password")

        users = self.service.get_all_users()
        assert len(users) == 3
        assert users[0].username == "user1"
        assert users[1].username == "user2"
        assert users[2].username == "user3"

    def test_get_user_by_id(self) -> None:
        self.service.save_new_user("user1@email.com", "user1", "password")
        self.service.save_new_user("user2@email.com", "user2", "password")

        user = self.service.get_user_by_id(1)
        assert user.username == "user1"
        user = self.service.get_user_by_id(2)
        assert user.username == "user2"

        # if user doesn't exist
        user = self.service.get_user_by_id(3)
        assert user is None

    def test_get_user_by_username(self) -> None:
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

    def test_get_user_by_email(self) -> None:
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

    def test_change_user_image(self) -> None:
        user = self.service.save_new_user("user@email.com", "username", "password")
        image = create_image_file("test.jpg", "image/jpg")
        image_url = self.service.change_user_image(user.id, image, "test.jpg")
        assert image_url == f"{S3.S3_ENDPOINT_URL}/user_images/test.jpg"

        # make sure changes have been saved to user
        assert user.image_url == image_url

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
