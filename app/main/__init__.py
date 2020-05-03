from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from app.main.config import app_config
from app.main.db import db
from app.main.controller.hello import HelloWorldController
from dotenv import load_dotenv

load_dotenv(".env")


def create_app(config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(app_config[config_name])

    db.init_app(app)

    api = Api(app)

    api.add_resource(HelloWorldController, '/hello')

    return app
