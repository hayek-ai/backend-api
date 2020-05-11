import unittest
import json
from app.test.conftest import flask_test_client, services_for_test
from app.main.service.user_service import UserService
from app.main.service.follow_service import FollowService
from app.main.db import db
from app.main.libs.strings import get_text


class TestFollowController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(user=UserService(), follow=FollowService()))
        self.user_service = UserService()
        self.follow_service = FollowService()
        db.create_all()

    def create_user(self, email, username) -> str:
        """helper function that creates a new user and returns an access token"""
        self.user_service.save_new_user(email, username, "password")
        # login and get access token
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password="password"
        )), content_type="application/json")
        login_data = json.loads(response.data)
        return login_data["accessToken"]

    def test_follow_and_unfollow_post(self) -> None:
        access_token = self.create_user("email@email.com", "username")
        analyst = self.user_service.save_new_user(
            "analyst@email.com", "analyst", "password", is_analyst=True)
        # follow
        response = self.client.post(
            f"/analyst/{analyst.id}/follow",
            headers={"Authorization": "Bearer {}".format(access_token)})
        response_data = json.loads(response.data)
        assert response.status_code == 201
        assert response_data["message"] == get_text("successfully_created").format("Follow")
        assert response_data["analyst"]["id"] == analyst.id
        assert response_data["analyst"]["numFollowers"] == 1

        # unfollow
        response = self.client.post(
            f"/analyst/{analyst.id}/follow",
            headers={"Authorization": "Bearer {}".format(access_token)})
        response_data = json.loads(response.data)
        assert response.status_code == 201
        assert response_data["message"] == get_text("successfully_deleted").format("Follow")
        assert response_data["analyst"]["id"] == analyst.id
        assert response_data["analyst"]["numFollowers"] == 0

    def test_following_get_and_followers_get(self) -> None:
        # create follow relationship
        access_token = self.create_user("email@email.com", "username")
        analyst = self.user_service.save_new_user(
            "analyst@email.com", "analyst", "password", is_analyst=True)
        self.client.post(
            f"/analyst/{analyst.id}/follow",
            headers={"Authorization": "Bearer {}".format(access_token)})

        # get analysts user is following (user will have id 1 bc it's created first)
        response = self.client.get(
            "/user/1/following",
            headers={"Authorization": "Bearer {}".format(access_token)})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert len(response_data["following"]) == 1
        assert response_data["following"][0]["id"] == analyst.id

        # get analysts user is following (user will have id 1 bc it's created first)
        response = self.client.get(
            f"/analyst/{analyst.id}/followers",
            headers={"Authorization": "Bearer {}".format(access_token)})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert len(response_data["followers"]) == 1
        assert response_data["followers"][0]["id"] == 1

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

