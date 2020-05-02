import os
import unittest

from flask import current_app
from application import app
from app.main.config import TestingConfig, DevelopmentConfig, ProductionConfig


class TestTestingConfig(unittest.TestCase):
    def test_app_is_testing(self):
        config = TestingConfig()
        self.assertTrue(config.ENV == 'testing')
        self.assertFalse(config.DEBUG)
        self.assertTrue(config.CSRF_ENABLED)
        self.assertTrue(config.SECRET == 'dev-secret')
        self.assertTrue(
            config.SQLALCHEMY_DATABASE_URI == 'postgresql://localhost/test_db'
        )
        self.assertFalse(config.SQLALCHEMY_TRACK_MODIFICATIONS)
        self.assertTrue(config.PROPAGATE_EXCEPTIONS)


class TestDevelopmentConfig(unittest.TestCase):
    def test_app_is_development(self):
        config = DevelopmentConfig()
        self.assertTrue(config.ENV == 'development')
        self.assertTrue(config.DEBUG)
        self.assertTrue(config.CSRF_ENABLED)
        self.assertTrue(config.SECRET == 'dev-secret')
        self.assertTrue(
            config.SQLALCHEMY_DATABASE_URI == 'postgresql://localhost/flask_api'
        )
        self.assertFalse(config.SQLALCHEMY_TRACK_MODIFICATIONS)
        self.assertTrue(config.PROPAGATE_EXCEPTIONS)


class TestProductionConfig(unittest.TestCase):
    def test_app_is_production(self):
        config = ProductionConfig()
        self.assertTrue(config.ENV == 'production')
        self.assertFalse(config.DEBUG)
