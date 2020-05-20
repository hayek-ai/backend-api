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
from app.main.controller.user_controller import UserRegister, UserLogin, User
from app.main.controller.confirmation_controller import Confirmation, ResendConfirmation
from app.main.controller.idea_controller import NewIdea, Idea, IdeaFeed, DownloadReport
from app.main.controller.follow_controller import Follow, FollowingList, FollowerList
from app.main.controller.review_controller import NewReview, Review, AnalystReviews
from app.main.controller.comment_controller import NewComment, Comment, IdeaComments
from app.main.controller.upvote_controller import Upvote, UpvoteFeed
from app.main.controller.downvote_controller import Downvote
from app.main.controller.bookmark_controller import Bookmark, BookmarkFeed
from app.main.controller.stock_data_controller import StockData, SearchAutocomplete

# Services
from app.main.service.user_service import UserService
from app.main.service.confirmation_service import ConfirmationService
from app.main.service.idea_service import IdeaService
from app.main.service.download_service import DownloadService
from app.main.service.follow_service import FollowService
from app.main.service.review_service import ReviewService
from app.main.service.comment_service import CommentService
from app.main.service.upvote_service import UpvoteService
from app.main.service.downvote_service import DownvoteService
from app.main.service.bookmark_service import BookmarkService


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
                     resource_class_kwargs={
                         'user_service': services["user"],
                         'follow_service': services['follow']
                     })
    api.add_resource(User, '/user/<username_or_id>',
                     resource_class_kwargs={
                         'user_service': services["user"],
                         'follow_service': services['follow']
                     })
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
                     resource_class_kwargs={
                        'user_service': services['user'],
                        'idea_service': services['idea']})
    api.add_resource(IdeaFeed, '/ideas/<string:feed_type>',
                     resource_class_kwargs={
                         'idea_service': services['idea'],
                         'user_service': services['user'],
                         'follow_service': services['follow']
                     })
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
    api.add_resource(NewReview, '/analyst/<int:analyst_id>/review',
                     resource_class_kwargs={
                         'user_service': services['user'],
                         'review_service': services['review']})
    api.add_resource(Review, '/review/<int:review_id>', resource_class_kwargs={'review_service': services['review']})
    api.add_resource(AnalystReviews, '/analyst/<int:analyst_id>/reviews',
                     resource_class_kwargs={
                         'user_service': services['user'],
                         'review_service': services['review']})
    api.add_resource(NewComment, '/idea/<int:idea_id>/comment',
                     resource_class_kwargs={
                         "idea_service": services["idea"],
                         "comment_service": services["comment"]})
    api.add_resource(Comment, '/comment/<int:comment_id>',
                     resource_class_kwargs={
                         "comment_service": services["comment"],
                         "idea_service": services["idea"]})
    api.add_resource(IdeaComments, '/idea/<int:idea_id>/comments',
                     resource_class_kwargs={
                         "idea_service": services["idea"],
                         "comment_service": services["comment"]})
    api.add_resource(Upvote, '/idea/<int:idea_id>/upvote',
                     resource_class_kwargs={
                         "idea_service": services["idea"],
                         "downvote_service": services["downvote"],
                         "upvote_service": services["upvote"]})
    api.add_resource(UpvoteFeed, '/user/<string:username>/upvotes',
                     resource_class_kwargs={
                         "upvote_service": services["upvote"],
                         "user_service": services["user"]})
    api.add_resource(Downvote, '/idea/<int:idea_id>/downvote',
                     resource_class_kwargs={
                         "idea_service": services["idea"],
                         "upvote_service": services["upvote"],
                         "downvote_service": services["downvote"]})
    api.add_resource(Bookmark, '/idea/<int:idea_id>/bookmark',
                     resource_class_kwargs={
                         "idea_service": services["idea"],
                         "bookmark_service": services["bookmark"]})
    api.add_resource(BookmarkFeed, '/user/<string:username>/bookmarks',
                     resource_class_kwargs={
                         "bookmark_service": services["bookmark"],
                         "user_service": services["user"]})
    api.add_resource(StockData, '/stock/<string:symbol>')
    api.add_resource(SearchAutocomplete, '/autosearch')

    return app
