import unittest
from app.main.db import db
from app.test.conftest import flask_test_client
from app.main.service.user_service import UserService
from app.main.service.follow_service import FollowService


class TestFollowService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.follow_service = FollowService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_follow_and_get_follow_by_id(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        follow = self.follow_service.save_new_follow(user_id=user.id, analyst_id=analyst.id)
        found_follow = self.follow_service.get_follow_by_id(follow.id)
        assert found_follow.id == follow.id
        assert user.num_following == 1
        assert user.num_followers == 0
        assert analyst.num_following == 0
        assert analyst.num_followers == 1
        assert follow.analyst_id == analyst.id
        assert follow.user_id == user.id

        # make sure returns None if not found
        not_found = self.follow_service.get_follow_by_id(10)
        assert not_found is None

    def test_get_follow_by_user_and_analyst(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        follow = self.follow_service.save_new_follow(user_id=user.id, analyst_id=analyst.id)
        found_follow = self.follow_service.get_follow_by_user_and_analyst(user_id=user.id, analyst_id=analyst.id)
        assert found_follow.id == follow.id

        # make sure returns None if not found
        not_found = self.follow_service.get_follow_by_user_and_analyst(10, 10)
        assert not_found is None

    def test_delete_follow(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        follow = self.follow_service.save_new_follow(user_id=user.id, analyst_id=analyst.id)
        self.follow_service.delete_follow(follow.id)
        assert user.num_following == 0
        assert user.num_followers == 0
        assert analyst.num_following == 0
        assert analyst.num_followers == 0
        follow = self.follow_service.get_follow_by_id(follow.id)
        assert follow is None

    def test_get_followers_and_get_following(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        self.follow_service.save_new_follow(user_id=user.id, analyst_id=analyst.id)
        analyst_followers = self.follow_service.get_followers(analyst.id)
        analyst_following = self.follow_service.get_following(analyst.id)
        user_followers = self.follow_service.get_followers(user.id)
        user_following = self.follow_service.get_following(user.id)
        assert len(analyst_followers) == 1
        assert len(analyst_following) == 0
        assert len(user_followers) == 0
        assert len(user_following) == 1
        assert analyst_followers[0].id == user.id
        assert user_following[0].id == analyst.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
