import unittest
import requests_mock
from app.main.db import db
from app.test.conftest import flask_test_client, register_mock_mailgun, register_mock_iex
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.downvote_service import DownvoteService


@requests_mock.Mocker()
class TestDownvoteService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.downvote_service = DownvoteService()
        self.app = flask_test_client()
        db.create_all()

    def create_idea_for_test(self, analyst_id: int) -> "IdeaModel":
        new_idea_dict = self.idea_service.save_new_idea(
            analyst_id=analyst_id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=313.49,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report"
        )
        return new_idea_dict["idea"]

    def test_save_new_downvote_and_get_downvote_by_id(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = self.create_idea_for_test(analyst.id)
        downvote = self.downvote_service.save_new_downvote(user_id=user.id, idea_id=idea.id)
        found_downvote = self.downvote_service.get_downvote_by_id(downvote.id)
        assert found_downvote.id == downvote.id
        assert idea.num_downvotes == 1
        assert idea.score == -1
        assert downvote.user_id == user.id
        assert downvote.idea_id == idea.id
        assert len(user.downvotes.all()) == 1

        # make sure returns none if not found
        not_found = self.downvote_service.get_downvote_by_id(10)
        assert not_found is None

    def test_delete_downvote_by_id(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = self.create_idea_for_test(analyst.id)

        downvote = self.downvote_service.save_new_downvote(user_id=user.id, idea_id=idea.id)
        self.downvote_service.delete_downvote_by_id(downvote.id)
        found_downvote = self.downvote_service.get_downvote_by_id(downvote.id)
        assert found_downvote is None
        assert len(user.downvotes.all()) == 0
        assert idea.num_downvotes == 0
        assert idea.score == 0

    def test_get_all_downvotes_for_idea(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user1 = self.user_service.save_new_user("user1@email.com", "user1", "password")
        user2 = self.user_service.save_new_user("user2@email.com", "user2", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = self.create_idea_for_test(analyst.id)
        downvote1 = self.downvote_service.save_new_downvote(user_id=user1.id, idea_id=idea.id)
        downvote2 = self.downvote_service.save_new_downvote(user_id=user2.id, idea_id=idea.id)
        downvotes = self.downvote_service.get_all_downvotes_for_idea(idea.id)
        assert len(downvotes) == 2
        assert downvotes[0].id == downvote2.id
        assert downvotes[1].id == downvote1.id

    def test_downvote_by_user_and_idea(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = self.create_idea_for_test(analyst.id)
        downvote = self.downvote_service.save_new_downvote(user_id=user.id, idea_id=idea.id)
        found_downvote = self.downvote_service.get_downvote_by_user_and_idea(user_id=user.id, idea_id=idea.id)
        assert found_downvote.id == downvote.id

        # make sure returns none if not found
        found_downvote = self.downvote_service.get_downvote_by_user_and_idea(10, 10)
        assert found_downvote is None

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
