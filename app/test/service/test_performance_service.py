import unittest

from app.main.db import db
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.service.performance_service import PerformanceService
from app.test.conftest import flask_test_client, register_mock_iex
from app.main.libs.util import create_idea


class TestPerformanceService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.app = flask_test_client()
        db.create_all()

    @requests_mock.Mocker()
    def test_update_performance(self, mock) -> None:
        register_mock_iex(mock)

        analyst1 = self.user_service \
            .save_new_user("email1@email.com", "analyst1", "password", is_analyst=True)

        analyst2 = self.user_service \
            .save_new_user("email2@email.com", "analyst2", "password", is_analyst=True)

        # long Apple at $313.49
        analyst1_idea1 = self.idea_service.save_new_idea(
            analyst_id=analyst1.id,
            symbol="AAPL",
            position_type="long",
            agreed_to_terms=True,
            bull_target=420,
            bull_probability=0.2,
            base_target=400,
            base_probability=0.6,
            bear_target=380,
            bear_probability=0.2,
            entry_price=313.49,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report"
        )
        # close out long apple position at $340 50 days later
        self.idea_service.close_idea_by_id(analyst1_idea1.id)
        analyst1_idea1.last_price = 340

        # short Apple
        analyst2_idea1 = self.idea_service.save_new_idea(
            analyst_id=analyst1.id,
            symbol="AAPL",
            position_type="short",
            agreed_to_terms=True,
            bull_target=350,
            bull_probability=0.2,
            base_target=250,
            base_probability=0.6,
            bear_target=150,
            bear_probability=0.2,
            entry_price=313.49,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report"
        )
