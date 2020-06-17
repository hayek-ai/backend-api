import unittest
import os
from test.conftest import flask_test_client


class TestTestingConfig(unittest.TestCase):
    def test_app_is_testing(self):
        config = flask_test_client({}, 'testing').application.config
        self.assertTrue(config['ENV'] == 'testing')
        self.assertFalse(config['DEBUG'])
        self.assertTrue(config['CSRF_ENABLED'])
        self.assertTrue(config['SECRET'] == 'dev-secret')
        self.assertTrue(
            config['SQLALCHEMY_DATABASE_URI'] == os.environ.get("TEST_DATABASE_URI")
        )
        self.assertFalse(config['SQLALCHEMY_TRACK_MODIFICATIONS'])
        self.assertTrue(config['PROPAGATE_EXCEPTIONS'])


class TestDevelopmentConfig(unittest.TestCase):
    def test_app_is_development(self):
        config = flask_test_client({}, 'development').application.config
        self.assertTrue(config['ENV'] == 'development')
        self.assertTrue(config['DEBUG'])
        self.assertTrue(config['CSRF_ENABLED'])
        self.assertTrue(config['SECRET'] == 'dev-secret')
        self.assertTrue(
            config['SQLALCHEMY_DATABASE_URI'] == os.environ.get("DEV_DATABASE_URI")
        )
        self.assertFalse(config['SQLALCHEMY_TRACK_MODIFICATIONS'])
        self.assertTrue(config['PROPAGATE_EXCEPTIONS'])


class TestProductionConfig(unittest.TestCase):
    def test_app_is_production(self):
        config = flask_test_client({}, 'production').application.config
        self.assertTrue(config['ENV'] == 'production')
        self.assertFalse(config['DEBUG'])
        self.assertTrue(
            config['SQLALCHEMY_DATABASE_URI'] == os.environ.get("PROD_DATABASE_URI")
        )