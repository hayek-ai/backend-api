import json
import unittest

from app.main.db import db
from app.main.libs.s3 import S3
from app.main.libs.strings import get_text
from app.main.libs.util import create_image_file
from app.main.service.user_service import UserService
from app.test.conftest import flask_test_client, services_for_test, register_mock_mailgun, requests_session

register_mock_mailgun(requests_session())


class TestUserController(unittest.TestCase):
    def setUp(self) -> None:
        self.client = flask_test_client(services_for_test(user=UserService()))
        self.service = UserService()
        db.create_all()

    def login(self, username, password) -> str:
        """Logs user in and returns accessToken"""
        response = self.client.post('/login', data=json.dumps(dict(
            emailOrUsername=username,
            password=password
        )), content_type='application/json')
        login_data = json.loads(response.data)
        return login_data["accessToken"]

    def test_register_user_post(self) -> None:
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
        assert data["errors"][0]["detail"] == get_text("incorrect_fields")
        assert data["errors"][0]["email"] == ['Not a valid email address.']
        assert response.status_code == 400

        # invalid username (with spaces)
        response = self.client.post('/register', data=json.dumps(dict(
            email='email@email.com',
            username='user name',
            password='password'
        )), content_type='application/json')
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("incorrect_fields")
        assert data["errors"][0]["username"] == [get_text("username_invalid")]
        assert response.status_code == 400

        # invalid username (with special characters)
        response = self.client.post('/register', data=json.dumps(dict(
            email='email@email.com',
            username='username&',
            password='password'
        )), content_type='application/json')
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("incorrect_fields")
        assert data["errors"][0]["username"] == [get_text("username_invalid")]
        assert response.status_code == 400

    def test_get_user(self) -> None:
        # create users
        self.service.save_new_user("email1@email.com", "username1", "password")
        self.service.save_new_user("email2@email.com", "username2", "password")

        # login
        access_token = self.login("username1", "password")

        # try to get user without authorization header -- error
        response = self.client.get('/user/1')
        assert response.status_code == 401

        # get by id
        response = self.client.get(
            '/user/1',
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        user = json.loads(response.data)
        assert user["username"] == "username1"
        assert response.status_code == 200

        # get by username
        response = self.client.get(
            '/user/username2',
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        user = json.loads(response.data)
        assert user["username"] == "username2"
        assert response.status_code == 200

        # user not found
        response = self.client.get(
            '/user/nonexistent-user',
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("not_found").format("User")
        assert response.status_code == 404

    def test_edit_user_put(self) -> None:
        self.service.save_new_user("email@email.com", "username", "password")
        self.service.save_new_user("email2@email.com", "username2", "password")

        # login
        access_token = self.login("username", "password")

        # try to edit user without authorization header -- error
        response = self.client.put("/user/1", data=json.dumps(dict(
            emailOrUsername="username",
            password="password"
        )), content_type='application/json')
        assert response.status_code == 401

        # try to edit profile other than your own
        response = self.client.put("/user/2", data=json.dumps(
            dict(bio="test bio")),
                                   content_type='application/json',
                                   headers={'Authorization': 'Bearer {}'.format(access_token)}
                                   )
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("unauthorized_user_edit")
        assert response.status_code == 403

        # handle user not found
        response = self.client.put("/user/5", data=json.dumps(
            dict(bio="test bio")),
                                   content_type='application/json',
                                   headers={'Authorization': 'Bearer {}'.format(access_token)}
                                   )
        data = json.loads(response.data)
        assert data["errors"][0]["detail"] == get_text("not_found").format("User")
        assert response.status_code == 404

        # update bio
        response = self.client.put("/user/1", data=json.dumps(
            dict(bio="test bio")),
                                   content_type='application/json',
                                   headers={'Authorization': 'Bearer {}'.format(access_token)}
                                   )
        updated_user = json.loads(response.data)
        assert updated_user["bio"] == "test bio"
        assert response.status_code == 201

        # update prefers_darkmode
        response = self.client.put("/user/1", data=json.dumps(
            dict(prefersDarkmode=True)),
                                   content_type='application/json',
                                   headers={'Authorization': 'Bearer {}'.format(access_token)})
        updated_user = json.loads(response.data)
        assert updated_user["prefersDarkmode"] is True
        assert response.status_code == 201

    def test_login_user_post(self) -> None:
        self.service.save_new_user("email@email.com", "username", "password")

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

    def test_image_upload_post(self) -> None:
        self.service.save_new_user("email@email.com", "username", "password")

        image = create_image_file("test.jpg", "image/jpg")
        data = dict(
            file=(image, "test.jpg")
        )

        # login
        access_token = self.login("username", "password")

        response = self.client.post(
            '/upload-profile-image',
            data=data,
            follow_redirects=True,
            content_type='multipart/form-data',
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        data = json.loads(response.data)
        assert data["imageUrl"] == f"{S3.S3_ENDPOINT_URL}/user_images/username-profile-image.jpg"
        assert response.status_code == 201

        # invalid file extension
        data = {
            'file': (create_image_file("test.pdf", "application/pdf"), "test.pdf")
        }
        response = self.client.post(
            '/upload-profile-image',
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        data = json.loads(response.data)
        assert data['errors'][0]['detail'] == get_text("invalid_file_extension")
        assert response.status_code == 400

        # invalid form
        response = self.client.post(
            '/upload-profile-image',
            data=None,
            follow_redirects=True,
            content_type="multipart/form-data",
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        assert response.status_code == 400

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
