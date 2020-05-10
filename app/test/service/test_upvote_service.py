import unittest
from app.main.db import db
from app.test.conftest import flask_test_client
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.upvote_service import UpvoteService


class TestUpvoteService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.upvote_service = UpvoteService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_upvote_and_get_upvote_by_id(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=309.93,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
        )["idea"]
        upvote = self.upvote_service.save_new_upvote(user_id=user.id, idea_id=idea.id)
        found_upvote = self.upvote_service.get_upvote_by_id(upvote.id)
        assert found_upvote.id == upvote.id
        assert idea.num_upvotes == 1
        assert idea.score == 1
        assert upvote.user_id == user.id
        assert upvote.idea_id == idea.id
        assert len(user.upvotes.all()) == 1

        # make sure returns none if not found
        not_found = self.upvote_service.get_upvote_by_id(10)
        assert not_found is None

    def test_delete_upvote_by_id(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=309.93,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
        )["idea"]
        upvote = self.upvote_service.save_new_upvote(user_id=user.id, idea_id=idea.id)
        self.upvote_service.delete_upvote_by_id(upvote.id)
        found_upvote = self.upvote_service.get_upvote_by_id(upvote.id)
        assert found_upvote is None
        assert len(user.upvotes.all()) == 0
        assert idea.num_upvotes == 0
        assert idea.score == 0

    def test_get_all_upvotes_for_idea(self) -> None:
        user1 = self.user_service.save_new_user("user1@email.com", "user1", "password")
        user2 = self.user_service.save_new_user("user2@email.com", "user2", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=309.93,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
        )["idea"]
        upvote1 = self.upvote_service.save_new_upvote(user_id=user1.id, idea_id=idea.id)
        upvote2 = self.upvote_service.save_new_upvote(user_id=user2.id, idea_id=idea.id)
        upvotes = self.upvote_service.get_all_upvotes_for_idea(idea.id)
        assert len(upvotes) == 2
        assert upvotes[0].id == upvote2.id
        assert upvotes[1].id == upvote1.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
