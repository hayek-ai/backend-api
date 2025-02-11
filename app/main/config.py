import os
from dotenv import load_dotenv

load_dotenv(".env")


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.environ['SECRET']
    SQLALCHEMY_DATABASE_URI = os.environ['PROD_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]


class DevelopmentConfig(Config):
    """Configurations for Development."""
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['DEV_DATABASE_URI']


class LocalConfig(Config):
    """Configurations for local development"""
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['LOCAL_DATABASE_URI']


class TestingConfig(Config):
    """Configurations for Testing ,with a separate test database."""
    ENV = 'testing'
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URI']


class ProductionConfig(Config):
    """Configurations for Production."""
    ENV = 'production'
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'local': LocalConfig
}