import datetime

from flask_restful import Resource, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from app.main.schema.idea_schema import idea_schema, idea_list_schema, new_idea_schema


class NewIdea(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']
        self.idea_service = kwargs['idea_service']
        self.idea_schema = idea_schema
        self.idea_list_schema = idea_list_schema
        self.new_idea_schema = new_idea_schema

    @jwt_required
    def post(self):
        """Allows analyst to upload a new idea"""
        pass
