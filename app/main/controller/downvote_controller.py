from flask_restful import Resource

from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.main.schema.idea_schema import idea_schema


class Downvote(Resource):
    def __init__(self, **kwargs):
        self.idea_service = kwargs["idea_service"]
        self.downvote_service = kwargs["downvote_service"]
        self.idea_schema = idea_schema

    @jwt_required
    def post(self, idea_id: int):
        """Creates and deletes downvotes"""
        user_id = get_jwt_identity()

        # make sure idea exists
        idea = self.idea_service.get_idea_by_id(idea_id)
        if not idea:
            return get_error(404, get_text("not_found").format("Idea"))

        # if downvoted, delete downvote
        downvote = self.downvote_service.get_downvote_by_user_and_idea(user_id, idea_id)
        if downvote:
            try:
                self.downvote_service.delete_downvote_by_id(downvote.id)
                return {
                    "message": get_text("successfully_deleted").format("Downvote"),
                    "idea": self.idea_schema.dump(idea)
                }, 200
            except Exception as e:
                return get_error(500, str(e))

        # else, cerate downvote
        try:
            self.downvote_service.save_new_downvote(user_id, idea_id)
            return{
                "message": get_text("successfully_created").format("Downvote"),
                "idea": self.idea_schema.dump(idea)
            }
        except Exception as e:
            return get_error(500, str(e))