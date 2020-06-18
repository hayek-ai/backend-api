import unittest
import requests_mock
from main.db import db
from test.conftest import flask_test_client, register_mock_iex, register_mock_mailgun
from main.service.user_service import UserService
from main.service.idea_service import IdeaService
from main.service.bookmark_service import BookmarkService
from main.libs.util import create_idea


@requests_mock.Mocker()
class TestBookmarkService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.bookmark_service = BookmarkService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_bookmark_and_get_bookmark_by_id(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        bookmark = self.bookmark_service.save_new_bookmark(user_id=user.id, idea_id=idea.id)
        found_bookmark = self.bookmark_service.get_bookmark_by_id(bookmark.id)
        assert found_bookmark.id == bookmark.id
        assert len(user.bookmarks.all()) == 1
        assert user.bookmarks.all()[0].id == bookmark.id

        # make sure returns none if not found
        not_found = self.bookmark_service.get_bookmark_by_id(10)
        assert not_found is None

    def test_delete_bookmark_by_id(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        bookmark = self.bookmark_service.save_new_bookmark(user_id=user.id, idea_id=idea.id)
        self.bookmark_service.delete_bookmark_by_id(bookmark.id)
        found_bookmark = self.bookmark_service.get_bookmark_by_id(bookmark.id)
        assert found_bookmark is None
        assert len(user.bookmarks.all()) == 0

    def test_get_bookmark_by_user_and_idea(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea = create_idea(analyst.id, "aapl", False)
        bookmark = self.bookmark_service.save_new_bookmark(user_id=user.id, idea_id=idea.id)
        found_bookmark = self.bookmark_service.get_bookmark_by_user_and_idea(user_id=user.id, idea_id=idea.id)
        assert found_bookmark.id == bookmark.id

        # make sure returns none if not found
        found_bookmark = self.bookmark_service.get_bookmark_by_user_and_idea(10, 10)
        assert found_bookmark is None

    def test_get_users_bookmarked_ideas(self, mock) -> None:
        register_mock_iex(mock)
        register_mock_mailgun(mock)

        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea1 = create_idea(analyst.id, "aapl", False)
        idea2 = create_idea(analyst.id, "gm", False)
        self.bookmark_service.save_new_bookmark(user_id=user.id, idea_id=idea1.id)
        self.bookmark_service.save_new_bookmark(user_id=user.id, idea_id=idea2.id)
        bookmarked_ideas = self.bookmark_service.get_users_bookmarked_ideas(user.id)
        assert len(bookmarked_ideas) == 2
        assert bookmarked_ideas[0].id == idea2.id
        assert bookmarked_ideas[1].id == idea1.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
