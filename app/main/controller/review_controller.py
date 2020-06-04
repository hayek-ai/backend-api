from flask_restful import Resource, request

from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.main.schema.review_schema import review_schema, review_list_schema, new_review_schema


class NewReview(Resource):
    def __init__(self, **kwargs):
        self.review_service = kwargs['review_service']
        self.user_service = kwargs['user_service']
        self.review_schema = review_schema
        self.new_review_schema = new_review_schema

    @jwt_required
    def post(self, analyst_id: int):
        """Creates a review for given analyst"""
        review_json = request.get_json()
        user_id = get_jwt_identity()

        # analysts can't review themselves
        if user_id == analyst_id:
            return get_error(400, get_text("invalid_self_review"))

        # validate review schema
        errors = self.new_review_schema.validate(review_json)
        if errors:
            return get_error(400, get_text("incorrect_fields"), **errors)

        # make sure analyst exists
        analyst = self.user_service.get_user_by_id(analyst_id)
        if not analyst:
            return get_error(404, get_text("not_found").format("Analyst"))

        # only pro-tier users are permitted to review
        user = self.user_service.get_user_by_id(user_id)
        if user.pro_tier_status != "succeeded":
            return get_error(400, get_text("non_pro_tier_review"))

        # user can only review analysts once
        all_analyst_reviews = self.review_service.get_all_reviews_for_analyst(analyst_id)
        already_reviewed = bool([review for review in all_analyst_reviews if (review.user_id == user_id)])
        if already_reviewed:
            return get_error(400, get_text("already_reviewed"))

        # create review
        try:
            review = self.review_service.save_new_review(
                title=review_json["title"],
                body=review_json["body"],
                stars=review_json["stars"],
                user_id=user_id,
                analyst_id=analyst_id)
            return self.review_schema.dump(review), 201
        except Exception as e:
            return get_error(500, str(e))


class Review(Resource):
    def __init__(self, **kwargs):
        self.review_service = kwargs['review_service']
        self.review_schema = review_schema

    @jwt_required
    def get(self, review_id: int):
        review = self.review_service.get_review_by_id(review_id)
        if not review:
            return get_error(404, get_text("not_found").format("Review"))
        return self.review_schema.dump(review), 200

    @jwt_required
    def delete(self, review_id: int):
        review = self.review_service.get_review_by_id(review_id)
        if not review:
            return get_error(404, get_text("not_found").format("Review"))
        if review.user_id != get_jwt_identity():
            return get_error(400, get_text("unauthorized_delete"))
        try:
            self.review_service.delete_review_by_id(review_id)
            return {"message": get_text("successfully_deleted").format("Review")}, 200
        except Exception as e:
            return get_error(500, str(e))


class AnalystReviews(Resource):
    def __init__(self, **kwargs):
        self.review_service = kwargs['review_service']
        self.user_service = kwargs['user_service']
        self.review_list_schema = review_list_schema

    @jwt_required
    def get(self, analyst_id: int):
        """Returns all of the reviews for a given analyst"""
        analyst = self.user_service.get_user_by_id(analyst_id)
        if not analyst:
            return get_error(404, get_text("not_found").format("Analyst"))
        reviews = self.review_service.get_all_reviews_for_analyst(analyst_id)
        return self.review_list_schema.dump(reviews), 200


