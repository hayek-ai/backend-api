from typing import List
from main.db import db
from main.model.user import UserModel
from main.model.review import ReviewModel
from sqlalchemy import and_


class ReviewService:
    def save_new_review(self, title: str, body: str, stars: int, user_id: int, analyst_id: int)\
            -> "ReviewModel":
        review = ReviewModel(
            title=title,
            body=body,
            stars=stars,
            user_id=user_id,
            analyst_id=analyst_id)

        analyst = UserModel.query.filter_by(id=analyst_id).first()
        analyst.review_star_total = analyst.review_star_total + stars
        analyst.num_reviews = analyst.num_reviews + 1
        self.save_changes(analyst)
        self.save_changes(review)
        return review

    @classmethod
    def get_review_by_id(cls, review_id: int) -> "ReviewModel":
        return ReviewModel.query.filter_by(id=review_id).first()

    @classmethod
    def get_review_by_user_and_analyst(cls, user_id: int, analyst_id: int) -> "ReviewModel":
        filters = [ReviewModel.user_id == user_id, ReviewModel.analyst_id == analyst_id]
        return ReviewModel.query.filter(and_(*filters)).first()

    def delete_review_by_id(self, review_id: int) -> None:
        review = self.get_review_by_id(review_id)
        analyst = UserModel.query.filter_by(id=review.analyst_id).first()
        analyst.review_star_total = analyst.review_star_total - review.stars
        analyst.num_reviews = analyst.num_reviews - 1
        self.save_changes(analyst)
        self.delete_from_db(review)

    @classmethod
    def get_all_reviews_for_analyst(cls, analyst_id: int) -> List["ReviewModel"]:
        return ReviewModel.query.join(UserModel, ReviewModel.analyst_id == UserModel.id)\
            .order_by(db.desc(ReviewModel.created_at))\
            .filter(ReviewModel.analyst_id == analyst_id).all()

    @classmethod
    def delete_from_db(cls, data) -> None:
        db.session.delete(data)
        db.session.commit()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
