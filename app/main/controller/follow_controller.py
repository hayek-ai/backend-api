from flask_restful import Resource

from main.libs.strings import get_text
from main.libs.util import get_error
from flask_jwt_extended import get_jwt_identity, jwt_required
from main.schema.user_schema import user_schema, user_follow_list_schema


class Follow(Resource):
    def __init__(self, **kwargs):
        self.follow_service = kwargs['follow_service']
        self.user_service = kwargs['user_service']
        self.user_schema = user_schema

    @jwt_required
    def post(self, analyst_id: int):
        """Creates and deletes follow relationships"""
        user_id = get_jwt_identity()

        # make sure analyst exists
        analyst = self.user_service.get_user_by_id(analyst_id)
        if not analyst:
            return get_error(404, get_text("not_found").format("Analyst"))

        # if already followed, delete follow
        follow = self.follow_service.get_follow_by_user_and_analyst(user_id=user_id, analyst_id=analyst_id)
        if follow:
            try:
                self.follow_service.delete_follow(follow.id)
                analyst_followers = self.follow_service.get_followers(analyst_id)
                return {
                    "message": get_text("successfully_deleted").format("Follow"),
                    "analyst":
                        {
                            **user_schema.dump(analyst),
                            "followers": user_follow_list_schema.dump(analyst_followers)
                        }
                }, 201
            except Exception as e:
                return get_error(500, str(e))

        # else, create follow
        try:
            self.follow_service.save_new_follow(user_id=user_id, analyst_id=analyst_id)
            analyst_followers = self.follow_service.get_followers(analyst_id)
            return {
                "message": get_text("successfully_created").format("Follow"),
                "analyst":
                    {
                        **self.user_schema.dump(analyst),
                        "followers": user_follow_list_schema.dump(analyst_followers)
                    }
            }, 201
        except Exception as e:
            return get_error(500, str(e))


class FollowingList(Resource):
    def __init__(self, **kwargs):
        self.follow_service = kwargs['follow_service']
        self.user_service = kwargs['user_service']
        self.user_follow_list_schema = user_follow_list_schema

    @jwt_required
    def get(self, user_id: int):
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return get_error(404, get_text("not_found").format("User"))

        following = self.follow_service.get_following(user_id)
        return {"following": self.user_follow_list_schema.dump(following)}, 200


class FollowerList(Resource):
    def __init__(self, **kwargs):
        self.follow_service = kwargs['follow_service']
        self.user_service = kwargs['user_service']
        self.user_follow_list_schema = user_follow_list_schema

    @jwt_required
    def get(self, analyst_id: int):
        analyst = self.user_service.get_user_by_id(analyst_id)
        if not analyst:
            return get_error(404, get_text("not_found").format("analyst"))

        followers = self.follow_service.get_followers(analyst_id)
        return {"followers": self.user_follow_list_schema.dump(followers)}, 200

