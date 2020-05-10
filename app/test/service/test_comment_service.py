import unittest
from app.main.db import db
from app.test.conftest import flask_test_client
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.comment_service import CommentService


class TestCommentService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.comment_service = CommentService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_comment_and_get_comment_by_id(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea_dict = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=309.93,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
        )
        idea = idea_dict["idea"]
        comment = self.comment_service.save_new_comment(
            body="Test Comment",
            user_id=user.id,
            idea_id=idea.id
        )
        found_comment = self.comment_service.get_comment_by_id(comment.id)
        assert found_comment.id == comment.id
        assert idea.num_comments == 1
        assert comment.body == "Test Comment"
        assert comment.user_id == user.id
        assert comment.idea_id == idea.id
        assert len(idea.comments.all()) == 1
        assert idea.comments.all()[0].id == idea.id

        # make sure returns none if not found
        not_found = self.comment_service.get_comment_by_id(10)
        assert not_found is None

    def test_delete_comment_by_id(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea_dict = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=309.93,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
        )
        idea = idea_dict["idea"]
        comment = self.comment_service.save_new_comment(
            body="Test Comment",
            user_id=user.id,
            idea_id=idea.id
        )
        self.comment_service.delete_comment_by_id(comment.id)
        found_comment = self.comment_service.get_comment_by_id(comment.id)
        assert found_comment is None
        assert len(idea.comments.all()) == 0
        assert idea.num_comments == 0

    def test_get_all_comments_for_idea(self) -> None:
        user = self.user_service.save_new_user("user@email.com", "user", "password")
        analyst = self.user_service.save_new_user("analyst@email.com", "analyst", "password", is_analyst=True)
        idea_dict = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=309.93,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
        )
        idea = idea_dict["idea"]
        comment1 = self.comment_service.save_new_comment(
            body="Test Comment",
            user_id=user.id,
            idea_id=idea.id
        )
        comment2 = self.comment_service.save_new_comment(
            body="Test Comment",
            user_id=user.id,
            idea_id=idea.id
        )
        comments = self.comment_service.get_all_comments_for_idea(idea.id)
        assert len(comments) == 2
        assert comments[0].id == comment2.id
        assert comments[1].id == comment1.id

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()