import unittest
import json
import requests_mock

from app.test.conftest import flask_test_client, services_for_test,register_mock_mailgun, register_mock_iex
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.bookmark_service import BookmarkService
from app.main.db import db
from app.main.libs.strings import get_text
from app.main.libs.util import create_idea


@requests_mock.Mocker()
class TestBookmarkController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(
            user=UserService(), idea=IdeaService(), bookmark=BookmarkService()))
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.bookmark_service = BookmarkService()
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

    def bookmark_idea(self, idea_id, access_token):
        """Creates/Deletes bookmark and returns response"""
        response = self.client.post(
            f"/idea/{idea_id}/bookmark",
            headers={"Authorization": "Bearer {}".format(access_token)})
        return response

    def test_create_and_delete_bookmark_post(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)

        response = self.bookmark_idea(idea.id, user_dict["access_token"])
        bookmark = self.bookmark_service.get_bookmark_by_id(1)
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_created").format("Bookmark")
        assert response_data["idea"]["id"] == idea.id
        assert bookmark is not None

        response = self.bookmark_idea(idea.id, user_dict["access_token"])
        bookmark = self.bookmark_service.get_bookmark_by_id(1)
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_deleted").format("Bookmark")
        assert response_data["idea"]["id"] == idea.id
        assert bookmark is None

    def test_get_bookmark_feed(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea1 = create_idea(analyst.id, "aapl", False)
        idea2 = create_idea(analyst.id, "gm", False)

        self.bookmark_idea(idea1.id, user_dict["access_token"])
        self.bookmark_idea(idea2.id, user_dict["access_token"])

        response = self.client.get(
            f'/user/{user_dict["user"].username}/bookmarks',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data["ideas"]) == 2
        assert response_data["ideas"][0]["analyst"]["id"] == analyst.id
        assert response_data["ideas"][1]["analyst"]["id"] == analyst.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
