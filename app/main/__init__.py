from flask import Flask, Blueprint
from flask_restful import Api
from flask_cors import CORS
from dotenv import load_dotenv

from app.main.config import app_config
from app.main.db import db

# Controllers
from app.main.controller.hello import HelloWorldController
from app.main.controller.user_register_controller import UserRegisterController

# Services
from app.main.service.register_user_service import RegisterUserService

load_dotenv(".env")


def create_app(services, config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(app_config[config_name])

    db.init_app(app)

    api = Api(app)

    api.add_resource(HelloWorldController, '/hello')
    api.add_resource(UserRegisterController, '/register', resource_class_kwargs={'service': services['register_user']})

    return app
