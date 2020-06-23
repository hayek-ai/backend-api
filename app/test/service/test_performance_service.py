import unittest
import datetime

import requests_mock
from main.db import db
from main.service.user_service import UserService
from main.service.idea_service import IdeaService
from main.service.performance_service import PerformanceService
from test.conftest import flask_test_client, register_mock_iex
from main.libs.util import create_idea


class TestPerformanceService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.performance_service = PerformanceService()
        self.app = flask_test_client()
        db.create_all()

    @requests_mock.Mocker()
    def test_update_performance(self, mock) -> None:
        register_mock_iex(mock)

        analyst1 = self.user_service \
            .save_new_user("email1@email.com", "analyst1", "password", is_analyst=True)
        analyst2 = self.user_service \
            .save_new_user("email2@email.com", "analyst2", "password", is_analyst=True)
        analyst3 = self.user_service \
            .save_new_user("email3@email.com", "analyst3", "password", is_analyst=True)

        # aapl = long (entry and last prices always $313.49)
        # gm = short ($23.21)
        analyst1_idea1 = create_idea(analyst1.id, "aapl", False)
        analyst1_idea2 = create_idea(analyst1.id, "gm", False)
        analyst2_idea1 = create_idea(analyst2.id, "aapl", False)
        analyst3_idea1 = create_idea(analyst3.id, "gm", False)

        analyst1_idea1.entry_price = 300  # gain of ~4.5%
        analyst1_idea1.created_at = analyst1_idea1.created_at - datetime.timedelta(days=100)
        analyst1_idea2.entry_price = 10  # loss of ~132.1%
        analyst2_idea1.entry_price = 400  # loss of ~21.6%
        analyst2_idea1.created_at = analyst2_idea1.created_at - datetime.timedelta(days=40)
        analyst3_idea1.entry_price = 50  # gain of ~53.6%
        analyst3_idea1.price_target = 40  # price_target_capture > 100%
        analyst3_idea1.created_at = analyst3_idea1.created_at - datetime.timedelta(days=20)
        self.idea_service.save_changes(analyst1_idea1)
        self.idea_service.save_changes(analyst1_idea2)
        self.idea_service.save_changes(analyst2_idea1)
        self.idea_service.save_changes(analyst3_idea1)

        self.performance_service.update_performance()

        assert abs(analyst1.avg_return + 0.638) < 0.01
        assert abs(analyst1.avg_price_target_capture - 0.0675) < 0.01
        assert abs(analyst1.success_rate - 0.5) < 0.01
        assert abs(analyst1.avg_holding_period - 50) < 1
        assert abs(analyst2.avg_return + 0.216) < 0.01
        assert analyst2.avg_price_target_capture == 0
        assert analyst2.success_rate == 0
        assert abs(analyst2.avg_holding_period - 40) < 1
        assert abs(analyst3.avg_return - 0.536) < 0.01
        assert analyst3.avg_price_target_capture == 1
        assert analyst3.success_rate == 1
        assert abs(analyst3.avg_holding_period - 20) < 1

        assert abs(analyst1.avg_return_percentile - 0.33) < 0.01
        assert abs(analyst2.avg_return_percentile - 0.67) < 0.01
        assert analyst3.avg_return_percentile == 1

        assert abs(analyst2.avg_price_target_capture_percentile - 0.33) < 0.01
        assert abs(analyst1.avg_price_target_capture_percentile - 0.67) < 0.01
        assert analyst3.avg_price_target_capture_percentile == 1

        assert abs(analyst2.success_rate_percentile - 0.33) < 0.01
        assert abs(analyst1.success_rate_percentile - 0.67) < 0.01
        assert analyst3.success_rate_percentile == 1

        assert abs(analyst3.avg_holding_period_percentile - 0.33) < 0.01
        assert abs(analyst2.avg_holding_period_percentile - 0.67) < 0.01
        assert analyst1.avg_holding_period_percentile == 1

        assert abs(analyst3.num_ideas_percentile - 0.5) < 0.01
        assert abs(analyst2.num_ideas_percentile - 0.5) < 0.01
        assert analyst1.num_ideas_percentile == 1

        assert analyst1.analyst_rank == 3
        assert analyst2.analyst_rank == 2
        assert analyst3.analyst_rank == 1

        assert abs(analyst1.analyst_rank_percentile - 0.33) < 0.01
        assert abs(analyst2.analyst_rank_percentile - 0.67) < 0.01
        assert analyst3.analyst_rank_percentile == 1

