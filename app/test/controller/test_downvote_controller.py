import unittest
import json
import requests_mock

from test.conftest import flask_test_client, services_for_test, register_mock_mailgun, register_mock_iex
from main.service.user_service import UserService
from main.service.idea_service import IdeaService
from main.service.downvote_service import DownvoteService
from main.service.upvote_service import UpvoteService
from main.db import db
from main.libs.strings import get_text
from main.libs.util import create_idea


@requests_mock.Mocker()
class TestDownvoteController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(
            user=UserService(), idea=IdeaService(), downvote=DownvoteService(), upvote=UpvoteService()))
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.downvote_service = DownvoteService()
        self.upvote_service = UpvoteService()
        db.create_all()

    def create_user(self, email, username, **kwargs) -> dict:
        """helper function that creates a new user and returns dict with user and access token"""
        new_user = self.user_service.save_new_user(email, username, "password", **kwargs)
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password="password",
        )), content_type="application/json")
        login_data = json.loads(response.data)
        return {"access_token": login_data["accessToken"], "user": new_user}

    def downvote_idea(self, idea_id, access_token):
        """Creates/Deletes downvote and returns response"""
        response = self.client.post(
            f"/idea/{idea_id}/downvote",
            headers={"Authorization": "Bearer {}".format(access_token)})
        return response

    def test_create_and_delete_downvote_post(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)

        # create downvote
        response = self.downvote_idea(idea.id, user_dict["access_token"])
        assert response.status_code == 200
        downvote = self.downvote_service.get_downvote_by_id(1)
        assert downvote is not None
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_created").format("Downvote")
        assert response_data["idea"]["id"] == idea.id
        assert response_data["idea"]["numDownvotes"] == 1
        assert response_data["idea"]["score"] == -1

        response = self.downvote_idea(idea.id, user_dict["access_token"])
        assert response.status_code == 200
        downvote = self.downvote_service.get_downvote_by_id(1)
        assert downvote is None
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_deleted").format("Downvote")
        assert response_data["idea"]["id"] == idea.id
        assert response_data["idea"]["numDownvotes"] == 0
        assert response_data["idea"]["score"] == 0

    def test_delete_upvote_if_upvote_exists(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)

        # create upvote
        self.upvote_service.save_new_upvote(user_dict["user"].id, idea.id)
        assert idea.num_upvotes == 1
        assert idea.score == 1

        # create downvote
        response = self.downvote_idea(idea.id, user_dict["access_token"])
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_created").format("Downvote")
        assert response_data["idea"]["id"] == idea.id
        assert response_data["idea"]["numDownvotes"] == 1
        assert response_data["idea"]["score"] == -1
        assert response_data["idea"]["numUpvotes"] == 0
        assert idea.num_upvotes == 0
        assert idea.num_downvotes == 1
        assert idea.score == -1

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

