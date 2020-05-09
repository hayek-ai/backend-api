import unittest
import json
from app.test.conftest import flask_test_client, services_for_test
from app.main.service.user_service import UserService
from app.main.service.review_service import ReviewService
from app.main.db import db


class TestReviewController(unittest.TestCase):
    def setUp(self) -> None: