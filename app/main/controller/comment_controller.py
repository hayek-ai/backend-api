from flask_restful import Resource, request

from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.main.schema.comment_schema import comment_schema, new_comment_schema, comment_list_schema


class NewComment(Resource):
    def __init__(self, **kwargs):
        self.comment_service = kwargs["comment_service"]
        self.idea_service = kwargs["idea_service"]
        self.comment_schema = comment_schema
        self.new_comment_schema = new_comment_schema

    @jwt_required
    def post(self, idea_id: int):
        """Creates a comment on given idea"""
        comment_json = request.get_json()
        user_id = get_jwt_identity()

        # validate comment schema
        errors = self.new_comment_schema.validate(comment_json)
        if errors:
            return get_error(400, get_text("incorrect_fields"), **errors)

        # make sure idea exists
        idea = self.idea_service.get_idea_by_id(idea_id)
        if idea is None:
            return get_error(404, get_text("not_found").format("Idea"))

        # create comment
        try:
            comment = self.comment_service.save_new_comment(
                body=comment_json["body"],
                user_id=user_id,
                idea_id=idea_id)
            return self.comment_schema.dump(comment), 201
        except Exception as e:
            return get_error(500, str(e))


class Comment(Resource):
    def __init__(self, **kwargs):
        self.comment_service = kwargs["comment_service"]
        self.comment_schema = comment_schema

    @jwt_required
    def get(self, comment_id: int):
        comment = self.comment_service.get_comment_by_id(comment_id)
        if not comment:
            return get_error(404, get_text("not_found").format("Comment"))
        return self.comment_schema.dump(comment), 200

    @jwt_required
    def delete(self, comment_id: int):
        comment = self.comment_service.get_comment_by_id(comment_id)
        if not comment:
            return get_error(404, get_text("not_found").format("Comment"))
        if comment.user_id != get_jwt_identity():
            return get_error(400, get_text("unauthorized_delete"))
        try:
            self.comment_service.delete_comment_by_id(comment_id)
            return {"message": get_text("successfully_deleted").format("Comment")}, 200
        except Exception as e:
            return get_error(500, str(e))


class IdeaComments(Resource):
    def __init__(self, **kwargs):
        self.comment_service = kwargs["comment_service"]
        self.idea_service = kwargs["idea_service"]
        self.comment_list_schema = comment_list_schema

    @jwt_required
    def get(self, idea_id: int):
        idea = self.idea_service.get_idea_by_id(idea_id)
        if idea is None:
            return get_error(404, get_text("not_found").format("Idea"))
        return self.comment_list_schema.dump(
            self.comment_service.get_all_comments_for_idea(idea_id)), 200
