import os
from dotenv import load_dotenv

# Not sure if this is supposed to be here or in the app
load_dotenv(".env")


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    ENV = 'development'


class TestingConfig(Config):
    """Configurations for Testing ,with a separate test database."""
    ENV = 'testing'
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/test_db'


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