import json
import unittest
import requests_mock
import datetime

from main.db import db
from main.libs.util import create_image_file
from main.libs.strings import get_text
from main.service.download_service import DownloadService
from main.service.idea_service import IdeaService
from main.service.user_service import UserService
from main.service.follow_service import FollowService
from test.conftest import flask_test_client, services_for_test, register_mock_mailgun, register_mock_iex
from main.libs.util import create_idea


@requests_mock.Mocker()
class TestIdeaController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(
            user=UserService(), idea=IdeaService(), download=DownloadService(),
            follow=FollowService()))
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.download_service = DownloadService()
        self.follow_service = FollowService()
        db.create_all()

    def create_user(self, email, username, **kwargs) -> dict:
        """helper function that creates a new user and returns dict with user and access token"""
        new_user = self.user_service.save_new_user(email, username, "password", **kwargs)
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password="password"
        )), content_type="application/json")
        login_data = json.loads(response.data)
        return {"access_token": login_data["accessToken"], "user": new_user}

    def test_new_idea_post(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        access_token = self.create_user("email@email.com", "username", is_analyst=True)["access_token"]

        # simple idea submit with exhibits
        exhibit1 = create_image_file("testexhibit1.png", "image/png")
        exhibit2 = create_image_file("testexhibit2.jpg", "image/jpg")
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "agreedToTerms": True,
            "priceTarget": 400,
            "entryPrice": 313.40,
            "thesisSummary": "Test Thesis Summary",
            "fullReport": "Test Full Report",
            'exhibits': (exhibit1, "testexhibit1.png"),
            'exhibits': (exhibit2, "testexhibit2.jpg"),
            "exhibitTitleMap": '{"testexhibit1.png": "Exhibit 1", "testexhibit2.jpg": "Exhibit 2"}'
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )
        response_data = json.loads(response.data)
        assert response.status_code == 201
        # returns new idea
        assert response_data["symbol"] == "AAPL"
        assert response_data["positionType"] == "long"
        assert response_data["agreedToTerms"] is True
        assert response_data["priceTarget"] == 400
        assert response_data["companyName"] == "Apple, Inc."
        assert response_data["marketCap"] > 500000000000  # $500bn
        assert response_data["sector"].lower() == "technology"
        assert response_data["entryPrice"] == 313.40
        # entry price withing 1% of last price
        assert abs(response_data["lastPrice"] - response_data["entryPrice"]) / response_data["lastPrice"] < 0.01
        assert response_data["closedDate"] is None
        assert response_data["score"] == 0
        assert response_data["numUpvotes"] == 0
        assert response_data["numDownvotes"] == 0
        assert response_data["numComments"] == 0
        assert response_data["numDownloads"] == 0
        assert response_data["analyst"]["id"] == 1

        # make sure can access idea property on analyst
        analyst = self.user_service.get_user_by_username("username")
        analyst_ideas = analyst.ideas.all()
        assert len(analyst_ideas) == 1
        assert analyst_ideas[0].symbol == "AAPL"

        # simple idea submit without exhibits
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "agreedToTerms": True,
            "priceTarget": 400,
            "entryPrice": 313.40,
            "thesisSummary": "Test Thesis Summary",
            "fullReport": "Test Full Report"
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )
        response_data = json.loads(response.data)
        assert response.status_code == 201
        # returns new idea
        assert response_data["symbol"] == "AAPL"

        # throws error if don't agree to terms
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "agreedToTerms": False,
            "priceTarget": 400,
            "entryPrice": 313.40,
            "thesisSummary": "Test Thesis Summary",
            "fullReport": "Test Full Report"
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )
        assert response.status_code == 400

        # invalid entry price error (must be within 1% of last price)
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "agreedToTerms": True,
            "priceTarget": 400,
            "entryPrice": 1,
            "thesisSummary": "Test Thesis Summary",
            "fullReport": "Test Full Report"
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )
        assert response.status_code == 400

        # invalid target probabilities (must add up to 1)
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "agreedToTerms": True,
            "priceTarget": 400,
            "entryPrice": 1,
            "thesisSummary": "Test Thesis Summary",
            "fullReport": "Test Full Report"
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )
        assert response.status_code == 400

        # invalid implied return
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "agreedToTerms": True,
            "priceTarget": 400,
            "entryPrice": 1,
            "thesisSummary": "Test Thesis Summary",
            "fullReport": "Test Full Report"
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )
        assert response.status_code == 400

        # missing fields
        data = {
            'symbol': "AAPL"
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )
        assert response.status_code == 400

        # incorrect position type
        data = {
            'symbol': "AAPL",
            "positionType": "market weight",
            "agreedToTerms": True,
            "priceTarget": 400,
            "entryPrice": 313.40,
            "thesisSummary": "Test Thesis Summary",
            "fullReport": "Test Full Report"
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )
        assert response.status_code == 400

    def test_get_idea(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        analyst_dict = self.create_user("email@email.com", "username", is_analyst=True)
        idea = create_idea(analyst_dict["user"].id, "aapl", False)
        response = self.client.get(
            f'/idea/{idea.id}',
            headers={"Authorization": "Bearer {}".format(analyst_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["symbol"] == "AAPL"
        assert response_data["thesisSummary"] == "Test Thesis Summary"
        assert "fullReport" not in response_data
        assert "exhibits" not in response_data

    def test_close_idea(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        analyst_dict = self.create_user("email@email.com", "username", is_analyst=True)
        idea = create_idea(analyst_dict["user"].id, "aapl", False)
        response = self.client.put(
            f'/idea/{idea.id}',
            data=json.dumps(dict(closedDate="abc")),  # text doesn't matter
            content_type='application/json',
            headers={"Authorization": "Bearer {}".format(analyst_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["closedDate"] is not None
        assert response_data["lastPrice"] is not None

    def test_delete_idea(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        analyst_dict = self.create_user("email1@email.com", "username1", is_analyst=True)
        idea = create_idea(analyst_dict["user"].id, "aapl", False)
        response = self.client.delete(
            f'/idea/{idea.id}',
            headers={"Authorization": "Bearer {}".format(analyst_dict["access_token"])})
        # only admin can delete idea
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["errors"][0]["detail"] == get_text("unauthorized_delete")

        admin_dict = self.create_user("email2@email.com", "username2", is_admin=True)
        response = self.client.delete(
            f'/idea/{idea.id}',
            headers={"Authorization": "Bearer {}".format(admin_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == get_text("successfully_deleted").format("Idea")

        idea = self.idea_service.get_idea_by_id(idea.id)
        assert idea is None


    def test_get_idea_feed(self, mock) -> None:
        register_mock_iex(mock)

        user_dict = self.create_user("user@email.com", "user")
        analyst1 = self.user_service.save_new_user("analyst1@email.com", "analyst1", "password", is_analyst=True)
        idea1 = create_idea(analyst1.id, "AAPL", False)
        idea2 = create_idea(analyst1.id, "GM", False)
        analyst2 = self.user_service.save_new_user("analyst2@email.com", "analyst2", "password", is_analyst=True)
        idea3 = create_idea(analyst2.id, "AAPL", False)
        idea4 = create_idea(analyst2.id, "GM", False)

        # "following" feed_type returns only ideas from analysts user follows
        follow = self.follow_service.save_new_follow(user_dict["user"].id, analyst1.id)
        response = self.client.get(
            '/ideas/following',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 2
        assert response_data[0]["analystId"] == analyst1.id

        self.follow_service.delete_follow(follow.id)
        response = self.client.get(
            '/ideas/following',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 0

        follow1 = self.follow_service.save_new_follow(user_dict["user"].id, analyst1.id)
        follow2 = self.follow_service.save_new_follow(user_dict["user"].id, analyst2.id)
        response = self.client.get(
            '/ideas/following',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 4

        # "discover" feed_type returns all ideas
        self.follow_service.delete_follow(follow1.id)
        self.follow_service.delete_follow(follow2.id)
        response = self.client.get(
            '/ideas/discover',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 4

        # filter by symbol
        response = self.client.get(
            '/ideas/discover?symbol=AAPL',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 2
        assert response_data[0]["symbol"] == "AAPL"

        # filter by position type
        response = self.client.get(
            '/ideas/discover?positionType=short',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 2
        assert response_data[0]["symbol"] == "GM"

        # filter by sector
        response = self.client.get(
            '/ideas/discover?sector=Consumer+Discretionary',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 2
        assert response_data[0]["symbol"] == "GM"

        # filter by multiple sectors
        response = self.client.get(
            '/ideas/discover?sector=Consumer+Discretionary&sector=Technology',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 4

        # filter by market cap
        response = self.client.get(
            '/ideas/discover?marketCap=mega',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 2
        assert response_data[0]["symbol"] == "AAPL"

        # filter by multiple market caps
        response = self.client.get(
            '/ideas/discover?marketCap=mega&marketCap=large',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 4
        assert response_data[0]["symbol"] == "GM"

        # filter by time period
        idea2.created_at = idea2.created_at - datetime.timedelta(days=100)
        self.idea_service.save_changes(idea2)
        response = self.client.get(
            '/ideas/discover?timePeriod=99',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 3

        # sort by popularity
        idea3.score = 100
        self.idea_service.save_changes(idea3)
        response = self.client.get(
            '/ideas/discover?sort=top',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 4
        assert response_data[0]["id"] == idea3.id

        # sort by latest (default)
        idea1.created_at = datetime.datetime.utcnow()
        self.idea_service.save_changes(idea1)
        response = self.client.get(
            '/ideas/discover?sort=latest',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data) == 4
        assert response_data[0]["id"] == idea1.id
        assert response_data[1]["id"] == idea4.id

        # invalid feed_type
        response = self.client.get(
            '/ideas/invalid-feed-type',
            headers={"Authorization": "Bearer {}".format(user_dict["access_token"])})
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["errors"][0]["detail"] == get_text("invalid_feed_type")

    def test_download_report(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        analyst_dict = self.create_user("email@email.com", "username", is_analyst=True)
        idea = create_idea(analyst_dict["user"].id, "aapl", False)

        response = self.client.get(
            f'/idea/{idea.id}/download',
            headers={"Authorization": "Bearer {}".format(analyst_dict["access_token"])})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data["symbol"] == "AAPL"
        assert response_data["thesisSummary"] == "Test Thesis Summary"
        assert response_data["fullReport"] == "Test Full Report"
        assert response_data["forwardPE"] == 18.14
        assert "exhibits" in response_data
        assert response_data["numDownloads"] == 1
        download = self.download_service.get_download_by_id(1)
        assert download.user_id == 1
        assert download.idea_id == idea.id
        count = self.download_service.get_idea_download_count(idea.id)
        assert count == 1
        count = self.download_service.get_user_download_count(1)
        assert count == 1
        count = self.download_service.get_analyst_download_count(1)
        assert count == 1

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
