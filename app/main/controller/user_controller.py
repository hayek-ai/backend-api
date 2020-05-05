import json
from flask_restful import Resource, request

from app.main.libs.strings import gettext
from app.main.libs.security import validate_signup_data
from app.main.schema.user_schema import user_schema, user_register_schema


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
                    "detail": gettext("incorrect_fields")
                }
            ]}, 400

        valid_dict = validate_signup_data(user_json)
        if not valid_dict["valid"]:
            return {"errors": valid_dict["errors"]}, 400
        
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
            return self.user_schema.dump(new_user), 201
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