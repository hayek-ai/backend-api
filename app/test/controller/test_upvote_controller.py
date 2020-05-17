import unittest
import json
import requests_mock

from app.test.conftest import flask_test_client, services_for_test, register_mock_iex, register_mock_mailgun
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.upvote_service import UpvoteService
from app.main.service.downvote_service import DownvoteService
from app.main.db import db
from app.main.libs.strings import get_text
from app.main.libs.util import create_idea


@requests_mock.Mocker()
class TestUpvoteController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(
            user=UserService(), idea=IdeaService(), upvote=UpvoteService(), downvote=DownvoteService()))
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.upvote_service = UpvoteService()
        self.downvote_service = DownvoteService()
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

    def upvote_idea(self, idea_id, access_token):
        """Creates/Deletes upvote and returns response"""
        response = self.client.post(
            f"/idea/{idea_id}/upvote",
            headers={"Authorization": "Bearer {}".format(access_token)})
        return response

    def test_create_and_delete_upvote_post(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)

        # create upvote
        response = self.upvote_idea(idea.id, user_dict["access_token"])
        assert response.status_code == 200
        upvote = self.upvote_service.get_upvote_by_id(1)
        assert upvote is not None
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_created").format("Upvote")
        assert response_data["idea"]["id"] == idea.id
        assert response_data["idea"]["numUpvotes"] == 1
        assert response_data["idea"]["score"] == 1

        # delete upvote
        response = self.upvote_idea(idea.id, user_dict["access_token"])
        upvote = self.upvote_service.get_upvote_by_id(1)
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_deleted").format("Upvote")
        assert response_data["idea"]["id"] == idea.id
        assert response_data["idea"]["numUpvotes"] == 0
        assert response_data["idea"]["score"] == 0
        assert upvote is None

    def test_delete_downvote_if_downvote_exists(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)

        # create downvote
        self.downvote_service.save_new_downvote(user_dict["user"].id, idea.id)
        assert idea.num_downvotes == 1
        assert idea.score == -1

        # create upvote
        response = self.upvote_idea(idea.id, user_dict["access_token"])
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_created").format("Upvote")
        assert response_data["idea"]["id"] == idea.id
        assert response_data["idea"]["numUpvotes"] == 1
        assert response_data["idea"]["score"] == 1
        assert response_data["idea"]["numDownvotes"] == 0
        assert idea.num_upvotes == 1
        assert idea.num_downvotes == 0
        assert idea.score == 1

    def test_get_upvote_feed(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea1 = create_idea(analyst.id, "aapl", False)
        idea2 = create_idea(analyst.id, "gm", False)

        self.upvote_idea(idea1.id, user_dict["access_token"])
        self.upvote_idea(idea2.id, user_dict["access_token"])

        response = self.client.get(
            f'/user/{user_dict["user"].username}/upvotes',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert len(response_data["ideas"]) == 2
        assert response_data["ideas"][0]["analyst"]["id"] == analyst.id
        assert response_data["ideas"][1]["analyst"]["id"] == analyst.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

