import unittest
import json
from app.test.conftest import flask_test_client, services_for_test
from app.main.service.user_service import UserService
from app.main.db import db


class TestUserController(unittest.TestCase):
    def setUp(self):
        self.client = flask_test_client(services_for_test(user=UserService()))
        db.create_all()

    def test_register_user_post(self):
        response = self.client.post('/register', data=json.dumps(dict(
            email='email@email.com',
            username='username',
            password='password'
        )), content_type='application/json')
        new_user = json.loads(response.data)
        assert new_user["username"] == "username"
        assert "password" not in new_user
        assert new_user["isAnalyst"] is False
        assert new_user["isConfirmed"] is False
        assert response.status_code == 201

    def tearDown(self):
        db.session.remove()
        db.drop_all()
