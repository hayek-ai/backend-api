import unittest
import json
from app.test.conftest import flask_test_client, services_for_test, mock_mailgun_send_email
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.download_service import DownloadService
from app.main.db import db
from app.main.libs.util import create_image_file

mock_mailgun_send_email()


class TestIdeaController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(
            user=UserService(), idea=IdeaService(), download=DownloadService()))
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.download_service = DownloadService()
        db.create_all()

    def create_analyst(self, email, username) -> str:
        """helper function that creates a new analyst and returns an access token"""
        self.user_service.save_new_user(email, username, "password", is_analyst=True)
        # login and get access token
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password="password"
        )), content_type="application/json")
        login_data = json.loads(response.data)
        return login_data["accessToken"]

    def test_new_idea_post(self) -> None:
        access_token = self.create_analyst("email@email.com", "username")

        # simple idea submit with exhibits
        exhibit1 = create_image_file("testexhibit1.png", "image/png")
        exhibit2 = create_image_file("testexhibit2.jpg", "image/jpg")
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "priceTarget": 400,
            "entryPrice": 309.93,
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
        assert response_data["priceTarget"] == 400
        assert response_data["companyName"] == "Apple, Inc."
        assert response_data["marketCap"] > 500000000000  # $500bn
        assert response_data["sector"].lower() == "technology"
        assert response_data["entryPrice"] == 309.93
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
            "priceTarget": 400,
            "entryPrice": 309.93,
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

        # invalid entry price error (must be within 1% of last price)
        data = {
            'symbol': "AAPL",
            "positionType": "long",
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

    def test_get_idea(self) -> None:
        access_token = self.create_analyst("email@email.com", "username")
        exhibit1 = create_image_file("testexhibit1.png", "image/png")
        exhibit2 = create_image_file("testexhibit2.jpg", "image/jpg")
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "priceTarget": 400,
            "entryPrice": 309.93,
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
        idea_id = response_data["id"]
        response = self.client.get(
            f'/idea/{idea_id}',
            headers={"Authorization": "Bearer {}".format(access_token)})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data["symbol"] == "AAPL"
        assert response_data["thesisSummary"] == "Test Thesis Summary"
        assert "fullReport" not in response_data
        assert "exhibits" not in response_data

    def test_download_report(self) -> None:
        access_token = self.create_analyst("email@email.com", "username")
        exhibit1 = create_image_file("testexhibit1.png", "image/png")
        exhibit2 = create_image_file("testexhibit2.jpg", "image/jpg")
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "priceTarget": 400,
            "entryPrice": 309.93,
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
        idea_id = response_data["id"]
        response = self.client.get(
            f'/idea/{idea_id}/download',
            headers={"Authorization": "Bearer {}".format(access_token)})
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data["symbol"] == "AAPL"
        assert response_data["thesisSummary"] == "Test Thesis Summary"
        assert response_data["fullReport"] == "Test Full Report"
        assert "exhibits" in response_data
        assert response_data["numDownloads"] == 1
        download = self.download_service.get_download_by_id(1)
        assert download.user_id == 1
        assert download.idea_id == idea_id
        count = self.download_service.get_idea_download_count(idea_id)
        assert count == 1
        count = self.download_service.get_user_download_count(1)
        assert count == 1
        count = self.download_service.get_analyst_download_count(1)
        assert count == 1

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
