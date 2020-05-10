import unittest
from app.main.db import db
from app.test.conftest import flask_test_client
from app.main.service.user_service import UserService
from app.main.service.review_service import ReviewService


class TestReviewService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.review_service = ReviewService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_review_and_get_review_by_id(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        review = self.review_service.save_new_review(
            title="Great analyst",
            body="One of the best analysts on the site",
            stars=5,
            user_id=user.id,
            analyst_id=analyst.id)
        found_review = self.review_service.get_review_by_id(review.id)
        assert found_review.id == review.id
        assert analyst.review_star_total == 5
        assert analyst.num_reviews == 1
        assert review.title == "Great analyst"
        assert review.body == "One of the best analysts on the site"
        assert review.stars == 5
        assert review.user_id == user.id
        assert review.analyst_id == analyst.id

        # make sure returns None if not found
        not_found = self.review_service.get_review_by_id(10)
        assert not_found is None

    def test_get_review_by_user_and_analyst(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        review = self.review_service.save_new_review(
            title="Great analyst",
            body="One of the best analysts on the site",
            stars=5,
            user_id=user.id,
            analyst_id=analyst.id)
        found_review = self.review_service.get_review_by_user_and_analyst(user_id=user.id, analyst_id=analyst.id)
        assert found_review.id == review.id

        # make sure returns None if not found
        not_found = self.review_service.get_review_by_user_and_analyst(10, 10)
        assert not_found is None

    def test_delete_review_by_id(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        review = self.review_service.save_new_review(
            title="Great analyst",
            body="One of the best analysts on the site",
            stars=5,
            user_id=user.id,
            analyst_id=analyst.id)
        self.review_service.delete_review_by_id(review.id)
        assert analyst.review_star_total == 0
        assert analyst.num_reviews == 0
        review = self.review_service.get_review_by_id(review.id)
        assert review is None

    def test_get_all_reviews_for_analyst(self) -> None:
        user1 = self.user_service.save_new_user("user1@email.com", "user1", "password")
        user2 = self.user_service.save_new_user("user2@email.com", "user2", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        self.review_service.save_new_review(
            title="Great analyst",
            body="One of the best analysts on the site",
            stars=5,
            user_id=user1.id,
            analyst_id=analyst.id)
        self.review_service.save_new_review(
            title="Great analyst",
            body="One of the best analysts on the site",
            stars=4,
            user_id=user2.id,
            analyst_id=analyst.id)
        reviews = self.review_service.get_all_reviews_for_analyst(analyst.id)
        assert len(reviews) == 2
        assert reviews[0].user_id == user2.id
        assert reviews[1].user_id == user1.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
