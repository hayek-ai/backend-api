from flask_restful import Resource

from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.main.schema.idea_schema import idea_schema, idea_list_schema


class Upvote(Resource):
    def __init__(self, **kwargs):
        self.idea_service = kwargs["idea_service"]
        self.upvote_service = kwargs["upvote_service"]
        self.idea_schema = idea_schema

    @jwt_required
    def post(self, idea_id: int):
        """Creates and deletes upvotes"""
        user_id = get_jwt_identity()

        # make sure idea exists
        idea = self.idea_service.get_idea_by_id(idea_id)
        if not idea:
            return get_error(404, get_text("not_found").format("Idea"))

        # if upvoted, delete upvote
        upvote = self.upvote_service.get_upvote_by_user_and_idea(user_id=user_id, idea_id=idea_id)
        if upvote:
            try:
                self.upvote_service.delete_upvote_by_id(upvote.id)
                return {
                    "message": get_text("successfully_deleted").format("Upvote"),
                    "idea": self.idea_schema.dump(idea)
                }, 200
            except Exception as e:
                return get_error(500, str(e))

        # else, create upvote
        try:
            self.upvote_service.save_new_upvote(user_id=user_id, idea_id=idea_id)
            return {
                "message": get_text("successfully_created").format("Upvote"),
                "idea": self.idea_schema.dump(idea)
            }
        except Exception as e:
            return get_error(500, str(e))


class UpvoteFeed(Resource):
    def __init__(self, **kwargs):
        self.upvote_service = kwargs["upvote_service"]
        self.user_service = kwargs["user_service"]
        self.idea_list_schema = idea_list_schema

    @jwt_required
    def get(self, username: str):
        user = self.user_service.get_user_by_username(username)
        if not user:
            return get_error(404, get_text("not_found").format("User"))
        ideas = self.upvote_service.get_users_upvoted_ideas(user.id)
        return {"ideas": self.idea_list_schema.dump(ideas)}, 200
