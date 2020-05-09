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
from app.main.controller.user_controller import UserRegister, UserLogin, User, UploadProfileImage
from app.main.controller.confirmation_controller import Confirmation, ResendConfirmation
from app.main.controller.idea_controller import NewIdea, Idea, DownloadReport
from app.main.controller.follow_controller import Follow, FollowingList, FollowerList

# Services
from app.main.service.user_service import UserService
from app.main.service.confirmation_service import ConfirmationService
from app.main.service.idea_service import IdeaService
from app.main.service.download_service import DownloadService
from app.main.service.follow_service import FollowService
from app.main.service.review_service import ReviewService


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

    api.add_resource(UserRegister, '/register',
                     resource_class_kwargs={
                        'user_service': services["user"],
                        'confirmation_service': services["confirmation"]})
    api.add_resource(UserLogin, '/login',
                     resource_class_kwargs={'service': services["user"]})
    api.add_resource(UploadProfileImage, '/upload-profile-image',
                     resource_class_kwargs={'service': services["user"]})
    api.add_resource(User, '/user/<username_or_id>',
                     resource_class_kwargs={'service': services["user"]})
    api.add_resource(Confirmation, '/user/confirm/<string:confirmation_code>',
                     resource_class_kwargs={
                         'user_service': services["user"],
                         'confirmation_service': services["confirmation"]})
    api.add_resource(ResendConfirmation, '/resend-confirmation',
                     resource_class_kwargs={
                         'user_service': services["user"],
                         'confirmation_service': services["confirmation"]})
    api.add_resource(NewIdea, '/new-idea',
                     resource_class_kwargs={
                         'user_service': services["user"],
                         'idea_service': services['idea']})
    api.add_resource(Idea, '/idea/<int:idea_id>',
                     resource_class_kwargs={'idea_service': services['idea']})
    api.add_resource(DownloadReport, '/idea/<int:idea_id>/download',
                     resource_class_kwargs={
                         'idea_service': services['idea'],
                         'download_service': services['download']})
    api.add_resource(Follow, '/analyst/<int:analyst_id>/follow',
                     resource_class_kwargs={
                         'follow_service': services['follow'],
                         'user_service': services['user']})
    api.add_resource(FollowingList, '/user/<int:user_id>/following',
                     resource_class_kwargs={
                         'follow_service': services['follow'],
                         'user_service': services['user']})
    api.add_resource(FollowerList, '/analyst/<int:analyst_id>/followers',
                     resource_class_kwargs={
                         'follow_service': services['follow'],
                         'user_service': services['user']})

    return app
