import json
import unittest
import requests_mock

from main.db import db
from main.libs.s3 import S3
from main.libs.strings import get_text
from main.libs.util import create_image_file
from main.service.user_service import UserService
from main.service.follow_service import FollowService
from test.conftest import flask_test_client, services_for_test, register_mock_mailgun


@requests_mock.Mocker()
class TestUserController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(
            user=UserService(), follow=FollowService()))
        self.user_service = UserService()
        self.follow_service = FollowService()
        db.create_all()

    def login(self, username, password) -> str:
        """Logs user in and returns accessToken"""
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password=password
        )), content_type='application/json')
        login_data = json.loads(response.data)
        return login_data["accessToken"]

    def test_register_user_post(self, mock) -> None:
        register_mock_mailgun(mock)

        response = self.client.post('/register', data=json.dumps(dict(
            email='email@email.com',
            username='username',
            password='password'
        )), content_type='application/json')
        data = json.loads(response.data)
        assert "accessToken" in data
        new_user = data["user"]
        assert new_user["username"] == "username"
        assert "password" not in new_user
        assert new_user["isAnalyst"] is False
        assert new_user["isConfirmed"] is False
        assert len(new_user["following"]) == 0
        assert len(new_user["followers"]) == 0
        assert response.status_code == 201
        assert data["confirmationEmailSent"] is True


        # underscores are valid in username
        response = self.client.post('/register', data=json.dumps(dict(
            email='email2@email.com',
            username='user_name',
            password='password'
        )), content_type='application/json')
        assert response.status_code == 201

        # email must be unique
        response = self.client.post('/register', data=json.dumps(dict(
            email="email2@email.com",
            username='user_name2',
            password="password"
        )), content_type="application/json")
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("email_exists")
        assert response.status_code == 409

        # username must be unique (case insensitive)
        response = self.client.post('/register', data=json.dumps(dict(
            email="email3@email.com",
            username="User_Name",
            password="password"
        )), content_type="application/json")
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("username_exists")
        assert response.status_code == 409

        # invalid email
        response = self.client.post('/register', data=json.dumps(dict(
            email='email.com',
            username='username',
            password='password'
        )), content_type='application/json')
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == 'Not a valid email address.'
        assert data["errors"][0]["field"] == 'email'
        assert response.status_code == 400

        # invalid username (with spaces)
        response = self.client.post('/register', data=json.dumps(dict(
            email='email@email.com',
            username='user name',
            password='password'
        )), content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("username_invalid")
        assert data["errors"][0]["field"] == 'username'

        # invalid username (with special characters)
        response = self.client.post('/register', data=json.dumps(dict(
            email='email@email.com',
            username='username&',
            password='password'
        )), content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("username_invalid")
        assert data["errors"][0]["field"] == 'username'

        # invalid username AND invalid email
        response = self.client.post('/register', data=json.dumps(dict(
            email='email.com',
            username='username&',
            password='password'
        )), content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == 'Not a valid email address.'
        assert data["errors"][0]["field"] == 'email'
        assert data["errors"][1]["detail"] == get_text("username_invalid")
        assert data["errors"][1]["field"] == 'username'

    def test_get_user(self, mock) -> None:
        register_mock_mailgun(mock)

        # create users
        user1 = self.user_service.save_new_user("email1@email.com", "username1", "password")
        user2 = self.user_service.save_new_user("email2@email.com", "username2", "password")
        analyst = self.user_service.save_new_user("email3@email.com", "analyst", "password", is_analyst=True)
        self.follow_service.save_new_follow(user1.id, analyst.id)
        self.follow_service.save_new_follow(user2.id, analyst.id)

        # login
        access_token = self.login("username1", "password")

        # try to get user without authorization header -- error
        response = self.client.get('/user/1')
        assert response.status_code == 401

        # get by id
        response = self.client.get(
            '/user/1',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        assert response.status_code == 200
        user = json.loads(response.data)
        assert user["username"] == "username1"
        assert len(user["following"]) == 1
        assert user["following"][0]["id"] == 3

        # get by username
        response = self.client.get(
            '/user/analyst',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        assert response.status_code == 200
        user = json.loads(response.data)
        assert user["username"] == "analyst"
        assert len(user["followers"]) == 2
        assert user["followers"][0]["id"] == 2

        # user not found
        response = self.client.get(
            '/user/nonexistent-user',
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("not_found").format("User")
        assert response.status_code == 404

    def test_edit_user_put(self, mock) -> None:
        register_mock_mailgun(mock)

        user1 = self.user_service.save_new_user("email@email.com", "user1", "password")
        user2 = self.user_service.save_new_user("email2@email.com", "user2", "password")
        analyst = self.user_service.save_new_user("email3@email.com", "analyst", "password", is_analyst=True)
        self.follow_service.save_new_follow(user1.id, analyst.id)
        self.follow_service.save_new_follow(user2.id, analyst.id)

        # login
        access_token = self.login("user1", "password")

        # try to edit user without authorization header -- error
        response = self.client.put(
            "/user/1",
            data=dict(bio="test bio", prefersDarkmode=True),
            follow_redirects=True,
            content_type='multipart/form-data')
        assert response.status_code == 401

        # try to edit profile other than your own
        response = self.client.put(
            "/user/2",
            data=dict(bio="test bio", prefersDarkmode=True),
            follow_redirects=True,
            content_type='multipart/form-data',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("unauthorized_user_edit")
        assert response.status_code == 403

        # handle user not found
        response = self.client.put(
            "/user/5",
            data=dict(bio="test bio", prefersDarkmode=True),
            follow_redirects=True,
            content_type='multipart/form-data',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("not_found").format("User")
        assert response.status_code == 404

        # update bio, prefersDarkmode, and profileImage
        profileImage = create_image_file("testProfileImage.jpeg", "image/jpeg")
        data = {
            "bio": "test bio",
            "prefersDarkmode": "true",
            "profileImage": (profileImage, "testProfileImage.jpeg")
        }
        response = self.client.put(
            "/user/1",
            data=data,
            follow_redirects=True,
            content_type='multipart/form-data',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        assert response.status_code == 201
        updated_user = json.loads(response.data)
        assert updated_user["bio"] == "test bio"
        assert updated_user["prefersDarkmode"] is True
        assert updated_user["imageUrl"] == f"{S3.S3_ENDPOINT_URL}/user_images/user1-profile-image.jpeg"
        assert len(updated_user["following"]) == 1
        assert updated_user["following"][0]["id"] == 3


        # invalid profileImage file extension
        data = {'profileImage': (create_image_file("test.pdf", "application/pdf"), "test.pdf")}
        response = self.client.put(
            '/user/1',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        data = json.loads(response.data)
        assert data['errors'][0]['detail'] == get_text("invalid_file_extension")
        assert response.status_code == 400

    def test_login_user_post(self, mock) -> None:
        register_mock_mailgun(mock)

        self.user_service.save_new_user("email@email.com", "username", "password")

        # login with username
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername="username",
            password="password"
        )), content_type='application/json')
        data = json.loads(response.data)
        assert "accessToken" in data
        assert data["user"]["username"] == "username"
        assert response.status_code == 200

        # login with email
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername="email@email.com",
            password="password"
        )), content_type='application/json')
        data = json.loads(response.data)
        assert "accessToken" in data
        assert data["user"]["username"] == "username"
        assert len(data["user"]["following"]) == 0
        assert len(data["user"]["followers"]) == 0
        assert response.status_code == 200

        # invalid username/email
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername="nonexistent-username",
            password="password"
        )), content_type='application/json')
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("user_invalid_credentials")
        assert response.status_code == 401

        # invalid password
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername="username",
            password="wrong_password"
        )), content_type="application/json")
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("user_invalid_credentials")
        assert response.status_code == 401

        # incorrect input fields
        response = self.client.post('/login', data=json.dumps(dict(
            wrong="wrong"
        )), content_type='application/json')
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("incorrect_fields")
        assert response.status_code == 400

    def test_get_analysts_for_leaderboard(self, mock) -> None:
        register_mock_mailgun(mock)
        user1 = self.user_service.save_new_user("user1@email.com", "user1", "password")
        analyst1 = self.user_service.save_new_user("analyst1@email.com", "analyst1", "password", is_analyst=True)
        analyst2 = self.user_service.save_new_user("analyst2@email.com", "analyst2", "password", is_analyst=True)
        analyst3 = self.user_service.save_new_user("analyst3@email.com", "analyst3", "password", is_analyst=True)

        analyst1.num_ideas = 10
        analyst1.analyst_rank = 10
        analyst2.num_ideas = 9
        analyst2.analyst_rank = 1
        self.user_service.save_changes(analyst1)
        self.user_service.save_changes(analyst2)

        access_token = self.login("user1", "password")
        response = self.client.get(
            '/leaderboard',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        assert response.status_code == 200
        analysts = json.loads(response.data)
        assert len(analysts) == 2
        # sorts by analyst_rank by default
        assert analysts[0]["id"] == analyst2.id
        assert analysts[1]["id"] == analyst1.id

        response = self.client.get(
            '/leaderboard?sortColumn=num_ideas&orderType=desc',
            headers={'Authorization': 'Bearer {}'.format(access_token)})
        assert response.status_code == 200
        analysts = json.loads(response.data)
        assert analysts[0]["id"] == analyst1.id
        assert analysts[1]["id"] == analyst2.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
