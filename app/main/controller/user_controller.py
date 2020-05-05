import datetime
import json
from flask_restful import Resource, request

from app.main.libs.strings import gettext
from app.main.schema.user_schema import user_schema, user_register_schema, user_login_schema
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


class UserRegister(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['service']
        self.user_schema = user_schema
        self.user_register_schema = user_register_schema

    def post(self):
        """
        Takes email, username, and password.  Then creates user (defaults to not analyst).
        Then sends confirmation email and returns new user.
        """
        user_json = request.get_json()
        errors = self.user_register_schema.validate(user_json)
        if errors:
            return {"errors": [
                {
                    "status": 400,
                    "detail": gettext("incorrect_fields"),
                    **errors
                }
            ]}, 400
        
        user = self.user_service.get_user_by_email(user_json['email'])
        if user:
            return {"errors": [
                {
                    "status": 409,
                    "detail": gettext("email_exists"),
                    "field": "email"
                }
            ]}, 409
        
        user = self.user_service.get_user_by_username(user_json['username'])
        if user:
            return {"errors": [
                {
                    "status": 409,
                    "detail": gettext("username_exists"),
                    "field": "username"
                }
            ]}, 409
        
        try:
            new_user = self.user_service.save_new_user(
                user_json["email"],
                user_json["username"],
                user_json["password"]
            )
            expires = datetime.timedelta(days=30)
            access_token = create_access_token(identity=new_user.id, expires_delta=expires, fresh=True)
            return {
                "user": self.user_schema.dump(new_user),
                "accessToken": access_token
            }, 201
        except Exception as e:
            return {"errors": [
                {
                    "status": 500,
                    "detail": str(e),
                    "field": "general"
                }
            ]}, 500


class User(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['service']
        self.user_schema = user_schema

    @jwt_required
    def get(self, username_or_id):
        if username_or_id.isdigit():
            user = self.user_service.get_user_by_id(username_or_id)
        else:
            user = self.user_service.get_user_by_username(username_or_id)
        
        if user:
            return self.user_schema.dump(user), 200
        else:
            return {"errors": [
                {
                    "status": 404,
                    "detail": gettext("not_found").format("User")
                }
            ]}, 404

    @jwt_required
    def put(self, username_or_id):
        if username_or_id.isdigit():
            user = self.user_service.get_user_by_id(username_or_id)
        else:
            user = self.user_service.get_user_by_username(username_or_id)
        if not user:
            return {"errors": [
                {
                    "status": 404,
                    "detail": gettext("not_found").format("User")
                }
            ]}, 404
        # users are only permitted to edit their own account details.
        if user.id != get_jwt_identity():
            return {"errors": [
                {
                    "status": 403,
                    "detail": gettext("unauthorized_user_edit")
                }
            ]}, 403

        user_details = request.get_json()
        if "bio" in user_details:
            if user_details["bio"].strip() == "":
                user.bio = None
            else:
                user.bio = user_details["bio"]
        if "prefersDarkmode" in user_details:
            user.prefers_darkmode = user_details["prefersDarkmode"]

        self.user_service.save_changes(user)
        return self.user_schema.dump(user), 201


class UserLogin(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['service']
        self.user_schema = user_schema
        self.user_login_schema = user_login_schema

    def post(self):
        credentials = request.get_json()
        errors = self.user_login_schema.validate(credentials)
        if errors:
            return {"errors": [
                {
                    "status": 400,
                    "detail": gettext("incorrect_fields"),
                    **errors
                }
            ]}, 400

        # allow user to login with email or username
        user = self.user_service.get_user_by_email(credentials["emailOrUsername"])
        if user is None:
            user = self.user_service.get_user_by_username(credentials["emailOrUsername"])

        if user and user.check_password(credentials["password"]):
            expires = datetime.timedelta(days=30)
            access_token = create_access_token(identity=user.id, expires_delta=expires, fresh=True)
            return {
                       "user": self.user_schema.dump(user),
                       "accessToken": access_token,
                   }, 200

        return {"errors": [
            {
                "status": 401,
                "detail": gettext("user_invalid_credentials"),
                "field": "general"
            }
        ]}, 401

