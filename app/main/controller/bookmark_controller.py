from flask_restful import Resource

from main.libs.strings import get_text
from main.libs.util import get_error
from flask_jwt_extended import get_jwt_identity, jwt_required
from main.schema.idea_schema import idea_schema, idea_list_schema


class Bookmark(Resource):
    def __init__(self, **kwargs):
        self.idea_service = kwargs["idea_service"]
        self.bookmark_service = kwargs["bookmark_service"]
        self.idea_schema = idea_schema

    @jwt_required
    def post(self, idea_id: int):
        """Creates and deletes bookmarks"""
        user_id = get_jwt_identity()

        # make sure idea exists
        idea = self.idea_service.get_idea_by_id(idea_id)
        if not idea:
            return get_error(404, get_text("not_found").format("Idea"))

        # if bookmarked, delete bookmark
        bookmark = self.bookmark_service.get_bookmark_by_user_and_idea(user_id, idea_id)
        if bookmark:
            try:
                self.bookmark_service.delete_bookmark_by_id(bookmark.id)
                return {
                    "message": get_text("successfully_deleted").format("Bookmark"),
                    "idea": self.idea_schema.dump(idea)
                }, 200
            except Exception as e:
                return get_error(500, str(e))

        # else, create bookmark
        try:
            self.bookmark_service.save_new_bookmark(user_id, idea_id)
            return {
                "message": get_text("successfully_created").format("Bookmark"),
                "idea": self.idea_schema.dump(idea)
            }
        except Exception as e:
            return get_error(500, str(e))


class BookmarkFeed(Resource):
    def __init__(self, **kwargs):
        self.bookmark_service = kwargs["bookmark_service"]
        self.user_service = kwargs["user_service"]
        self.idea_list_schema = idea_list_schema

    @jwt_required
    def get(self, username: str):
        user = self.user_service.get_user_by_username(username)
        if not user:
            return get_error(404, get_text("not_found").format("User"))
        ideas = self.bookmark_service.get_users_bookmarked_ideas(user.id)
        return {"ideas": self.idea_list_schema.dump(ideas)}, 200

