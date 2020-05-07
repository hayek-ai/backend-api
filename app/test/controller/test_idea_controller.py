import unittest
import json
import io
from app.test.conftest import flask_test_client, services_for_test
from app.main.libs.strings import get_text
from app.main.libs.s3 import S3
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.db import db


class TestIdeaController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(user=UserService(), idea=IdeaService))
        self.user_service = UserService()
        self.idea_service = IdeaService()
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
        data = {
            'symbol': "AAPL",
            "positionType": "long",
            "priceTarget": 400,
            "entryPrice": 300,
            "thesisSummary": "Test Thesis Summary",
            "fullReport": "Test Full Report",
            'exhibits': (io.BytesIO(b"abcdef"), "testexhibit1.png"),
            'exhibits': (io.BytesIO(b"abcdef"), "testexhibit2.jpg"),
            "exhibitTitleMap": {"testexhibit1.png":"Exhibit 1","testexhibit2.jpg":"Exhibit 2"}
        }
        response = self.client.post(
            '/new-idea',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={"Authorization": "Bearer {}".format(access_token)}
        )

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()