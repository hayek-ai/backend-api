import unittest
import json
from app.test.conftest import flask_test_client, services_for_test
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.upvote_service import UpvoteService
from app.main.db import db
from app.main.libs.strings import get_text


class TestUpvoteController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(
            user=UserService(), idea=IdeaService(), upvote=UpvoteService()))
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.upvote_service = UpvoteService()
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

    def create_idea(self, analyst_id) -> dict:
        new_idea_dict = self.idea_service.save_new_idea(
            analyst_id=analyst_id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=309.93,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",)
        return new_idea_dict["idea"]

    def upvote_idea(self, idea_id, access_token):
        """Creates/Deletes upvote and returns response"""
        response = self.client.post(
            f"/idea/{idea_id}/upvote",
            headers={"Authorization": "Bearer {}".format(access_token)})
        return response

    def test_create_and_delete_upvote_post(self) -> None:
        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = self.create_idea(analyst.id)

        # simple upvote
        response = self.upvote_idea(idea.id, user_dict["access_token"])
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_created").format("Upvote")
        assert response_data["idea"]["id"] == idea.id
        assert response_data["idea"]["numUpvotes"] == 1
        assert response_data["idea"]["score"] == 1

        # delete upvote
        response = self.upvote_idea(idea.id, user_dict["access_token"])
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_deleted").format("Upvote")
        assert response_data["idea"]["id"] == idea.id
        assert response_data["idea"]["numUpvotes"] == 0
        assert response_data["idea"]["score"] == 0

    def test_get_upvote_feed(self) -> None:
        user_dict = self.create_user("user@email.com", "user")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea1 = self.create_idea(analyst.id)
        idea2 = self.create_idea(analyst.id)

        # simple upvote
        self.upvote_idea(idea1.id, user_dict["access_token"])
        self.upvote_idea(idea2.id, user_dict["access_token"])

        # get user's upvote feed
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