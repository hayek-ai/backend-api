import unittest
from app.main.db import db
from app.test.conftest import flask_test_client
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.bookmark_service import BookmarkService


class TestBookmarkService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.bookmark_service = BookmarkService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_bookmark_and_get_bookmark_by_id(self) -> None:
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
        bookmark = self.bookmark_service.save_new_bookmark(user_id=user.id, idea_id=idea.id)
        found_bookmark = self.bookmark_service.get_bookmark_by_id(bookmark.id)
        assert found_bookmark.id == bookmark.id
        assert len(user.bookmarks.all()) == 1
        assert user.bookmarks.all()[0].id == bookmark.id

        # make sure returns none if not found
        not_found = self.bookmark_service.get_bookmark_by_id(10)
        assert not_found is None

    def test_delete_bookmark_by_id(self) -> None:
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
        bookmark = self.bookmark_service.save_new_bookmark(user_id=user.id, idea_id=idea.id)
        self.bookmark_service.delete_bookmark_by_id(bookmark.id)
        found_bookmark = self.bookmark_service.get_bookmark_by_id(bookmark.id)
        assert found_bookmark is None
        assert len(user.bookmarks.all()) == 0

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
