import os
from dotenv import load_dotenv

load_dotenv(".env")


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True


class DevelopmentConfig(Config):
    """Configurations for Development."""
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI')


class TestingConfig(Config):
    """Configurations for Testing ,with a separate test database."""
    ENV = 'testing'
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI')


class ProductionConfig(Config):
    """Configurations for Production."""
    ENV = 'production'
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}