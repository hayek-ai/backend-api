import unittest
import json
import requests_mock

from test.conftest import flask_test_client, services_for_test,register_mock_iex, register_mock_mailgun
from main.service.user_service import UserService
from main.service.idea_service import IdeaService
from main.service.comment_service import CommentService
from main.db import db
from main.libs.strings import get_text
from main.libs.util import create_idea


@requests_mock.Mocker()
class TestCommentController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(
            user=UserService(), idea=IdeaService(), comment=CommentService()))
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.comment_service = CommentService()
        db.create_all()

    def create_user(self, email, username, **kwargs) -> dict:
        """helper function that creates a new user and returns dict with user and access token"""
        new_user = self.user_service.save_new_user(email, username, "password", **kwargs)
        # login and get access token
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password="password",
        )), content_type="application/json")
        login_data = json.loads(response.data)
        return {"access_token": login_data["accessToken"], "user": new_user}

    def create_comment(self, idea_id, access_token):
        """Creates new comment and returns response"""
        response = self.client.post(
            f"/idea/{idea_id}/comment",
            data=json.dumps(dict(body="Test Comment")),
            content_type="application/json",
            headers={"Authorization": "Bearer {}".format(access_token)})
        return response

    def test_new_comment_post(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst_dict = self.create_user("analyst@email.com", "analyst", is_analyst=True)
        idea = create_idea(analyst_dict["user"].id, "aapl", False)

        # simple comment submit
        response = self.create_comment(idea.id, user_dict["access_token"])
        response_data = json.loads(response.data)
        assert response.status_code == 201
        assert response_data["comment"]["body"] == "Test Comment"
        assert "imageUrl" in response_data["comment"]["user"]
        assert response_data["comment"]["user"]["username"] == "user"
        assert response_data["idea"]["id"] == idea.id

    def test_get_and_delete_comment(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst_dict = self.create_user("analyst@email.com", "analyst", is_analyst=True)
        idea = create_idea(analyst_dict["user"].id, "aapl", False)

        # simple comment submit
        response = self.create_comment(idea.id, user_dict["access_token"])
        comment_dict = json.loads(response.data)["comment"]
        response = self.client.get(
            f'/comment/{comment_dict["id"]}',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data["id"] == comment_dict["id"]
        comment = self.comment_service.get_comment_by_id(response_data["id"])
        assert comment is not None
        response = self.client.delete(
            f'/comment/{comment_dict["id"]}',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data["message"] == get_text("successfully_deleted").format("Comment")
        assert response_data["idea"]["id"] == idea.id

        comment = self.comment_service.get_comment_by_id(comment.id)
        assert comment is None

    def test_get_idea_comments(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst_dict = self.create_user("analyst@email.com", "analyst", is_analyst=True)
        idea = create_idea(analyst_dict["user"].id, "aapl", False)

        # submit 2 comments
        response1 = self.create_comment(idea.id, user_dict["access_token"])
        response1_data = json.loads(response1.data)
        response2 = self.create_comment(idea.id, user_dict["access_token"])
        response2_data = json.loads(response2.data)

        response = self.client.get(
            f'/idea/{idea.id}/comments',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert len(response_data) == 2
        assert response_data[0]["id"] == response2_data["comment"]["id"]
        assert response_data[1]["id"] == response1_data["comment"]["id"]

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()