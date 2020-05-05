from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError

from app.main.config import app_config
from app.main.db import db
from app.main.ma import ma

# Controllers
from app.main.controller.user_controller import UserRegister, User

# Services
from app.main.service.user_service import UserService


def create_app(services, config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(app_config[config_name])
    api = Api(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify(err.messages), 400

    jwt = JWTManager(app)  # not creating /auth
    migrate = Migrate(app, db)

    db.init_app(app)
    ma.init_app(app)

    api.add_resource(UserRegister, '/register', resource_class_kwargs={'service': services["user"]})
    api.add_resource(User, '/user/<username_or_id>', resource_class_kwargs={'service': services["user"]})

    return app
