from flask_restful import Resource, request
import json
from marshmallow import Schema, fields


class UserRegisterSchema(Schema):
    """ /api/register - POST

    Parameters:
     - email (str)
     - username (str)
     - password (str)
    """
    email = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class UserRegisterController(Resource):
    def __init__(self, **kwargs):
        # register_user_service does the work for registering a user
        self.register_user_service = kwargs['service']
        self.register_user_schema = UserRegisterSchema()

    def post(self):
        """
        Takes email, username, password and whether or not the user is an analyst.
        Then sends confirmation email.
        """
        errors = self.register_user_schema.validate(request.form)
        if errors:
            return {'error': 'Wrong input params'}, 400

        response = self.register_user_service.register_user(
            request.form['email'],
            request.form['username'],
            request.form['password']
        )

        return self.register_user_schema.dump(response), 201
