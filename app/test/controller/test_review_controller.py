import unittest
import json
import requests_mock

from flask import Response
from test.conftest import flask_test_client, services_for_test, register_mock_mailgun
from main.service.user_service import UserService
from main.service.review_service import ReviewService
from main.db import db
from main.libs.strings import get_text


@requests_mock.Mocker()
class TestReviewController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(user=UserService(), review=ReviewService()))
        self.user_service = UserService()
        self.review_service = ReviewService()
        db.create_all()

    def create_user(self, email, username, **kwargs) -> str:
        """helper function that creates a new user and returns dict with user and access token"""
        new_user = self.user_service.save_new_user(email, username, "password", **kwargs)
        # login and get access token
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password="password",
        )), content_type="application/json")
        login_data = json.loads(response.data)
        return {"access_token": login_data["accessToken"], "user": new_user}

    def create_review(self, analyst_id, access_token) -> Response:
        """Creates new review and returns response"""
        response = self.client.post(
            f'/analyst/{analyst_id}/review',
            data=json.dumps(dict(
                title="Test Title",
                body="Test Body",
                stars=5
            )),
            content_type='application/json',
            headers={"Authorization": "Bearer {}".format(access_token)})
        return response

    def test_new_review_post(self, mock) -> None:
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user", pro_tier_status="succeeded")
        user_id = user_dict["user"].id
        analyst_dict = self.create_user("analyst@email.com", "analyst", is_analyst=True)
        analyst_id = analyst_dict["user"].id

        # simple review submit
        response = self.create_review(analyst_id, user_dict["access_token"])
        response_data = json.loads(response.data)
        assert response.status_code == 201
        # returns new review
        assert response_data["title"] == "Test Title"
        assert response_data["body"] == "Test Body"
        assert response_data["stars"] == 5
        assert response_data["userId"] == user_id
        assert response_data["analystId"] == analyst_id

        # make sure can access imageUrl property on user
        assert "imageUrl" in response_data["user"]

        # missing fields
        response = self.client.post(
            f'/analyst/{analyst_id}/review',
            data=json.dumps(dict(title="Test Title")),
            content_type='application/json',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])}
        )
        assert response.status_code == 400

    def test_get_and_delete_review(self, mock) -> None:
        register_mock_mailgun(mock)

        user_dict = self.create_user("user@email.com", "user", pro_tier_status="succeeded")
        analyst_dict = self.create_user("analyst@email.com", "analyst", is_analyst=True)

        # simple review submit
        response = self.create_review(analyst_dict["user"].id, user_dict["access_token"])
        review_dict = json.loads(response.data)
        response = self.client.get(
            f'/review/{review_dict["id"]}',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])}
        )
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data["id"] == review_dict["id"]

        review = self.review_service.get_review_by_id(response_data["id"])
        assert review is not None
        response = self.client.delete(
            f"/review/{review_dict['id']}",
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data["message"] == get_text("successfully_deleted").format("Review")
        review = self.review_service.get_review_by_id(review.id)
        assert review is None

    def test_get_analyst_reviews(self, mock) -> None:
        register_mock_mailgun(mock)

        user1_dict = self.create_user("user1@email.com", "user1", pro_tier_status="succeeded")
        user2_dict = self.create_user("user2@email.com", "user2", pro_tier_status="succeeded")
        analyst_dict = self.create_user("analyst@email.com", "analyst", is_analyst=True)
        analyst_id = analyst_dict["user"].id

        # submit 2 reviews
        response1 = self.create_review(analyst_id, user1_dict["access_token"])
        response1_data = json.loads(response1.data)
        response2 = self.create_review(analyst_id, user2_dict["access_token"])
        response2_data = json.loads(response2.data)

        response = self.client.get(
            f'/analyst/{analyst_id}/reviews',
            headers={"Authorization": "Bearer {}".format(user1_dict["access_token"])})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert len(response_data) == 2
        assert response_data[0]["id"] == response2_data["id"]
        assert response_data[1]["id"] == response1_data["id"]

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
