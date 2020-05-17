import unittest

import requests_mock

from app.main.db import db
from app.main.model.idea import IdeaModel
from app.main.service.idea_service import IdeaService
from app.main.service.upvote_service import UpvoteService
from app.main.service.user_service import UserService
from app.test.conftest import flask_test_client, register_mock_iex, register_mock_mailgun
from app.main.libs.util import create_idea


@requests_mock.Mocker()
class TestUpvoteService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.upvote_service = UpvoteService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_upvote_and_get_upvote_by_id(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
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

    def test_delete_upvote_by_id(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        upvote = self.upvote_service.save_new_upvote(user_id=user.id, idea_id=idea.id)
        self.upvote_service.delete_upvote_by_id(upvote.id)
        found_upvote = self.upvote_service.get_upvote_by_id(upvote.id)
        assert found_upvote is None
        assert len(user.upvotes.all()) == 0
        assert idea.num_upvotes == 0
        assert idea.score == 0

    def test_delete_upvote_by_user_and_idea_if_exists(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        upvote = self.upvote_service.save_new_upvote(user_id=user.id, idea_id=idea.id)
        self.upvote_service.delete_upvote_by_user_and_idea_if_exists(user.id, idea.id)
        found_upvote = self.upvote_service.get_upvote_by_id(upvote.id)
        assert found_upvote is None
        assert len(user.upvotes.all()) == 0
        assert idea.num_upvotes == 0
        assert idea.score == 0

    def test_get_all_upvotes_for_idea(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user1 = self.user_service.save_new_user("user1@email.com", "user1", "password")
        user2 = self.user_service.save_new_user("user2@email.com", "user2", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        upvote1 = self.upvote_service.save_new_upvote(user_id=user1.id, idea_id=idea.id)
        upvote2 = self.upvote_service.save_new_upvote(user_id=user2.id, idea_id=idea.id)
        upvotes = self.upvote_service.get_all_upvotes_for_idea(idea.id)
        assert len(upvotes) == 2
        assert upvotes[0].id == upvote2.id
        assert upvotes[1].id == upvote1.id

    def test_get_upvote_by_user_and_idea(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        upvote = self.upvote_service.save_new_upvote(user_id=user.id, idea_id=idea.id)
        found_upvote = self.upvote_service.get_upvote_by_user_and_idea(user_id=user.id, idea_id=idea.id)
        assert found_upvote.id == upvote.id

        # make sure returns none if not found
        found_upvote = self.upvote_service.get_upvote_by_user_and_idea(10, 10)
        assert found_upvote is None

    def test_get_users_upvoted_ideas(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea1 = create_idea(analyst.id, "aapl", False)
        idea2 = create_idea(analyst.id, "gm", False)
        self.upvote_service.save_new_upvote(user_id=user.id, idea_id=idea1.id)
        self.upvote_service.save_new_upvote(user_id=user.id, idea_id=idea2.id)
        upvoted_ideas = self.upvote_service.get_users_upvoted_ideas(user.id)
        assert len(upvoted_ideas) == 2
        assert upvoted_ideas[0].id == idea2.id
        assert upvoted_ideas[1].id == idea1.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
