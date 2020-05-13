import datetime
import json
import unittest

import requests_mock

from app.main.db import db
from app.main.libs.s3 import S3
from app.main.libs.util import create_image_file
from app.main.service.idea_service import IdeaService
from app.main.service.user_service import UserService
from app.test.conftest import flask_test_client
from app.test.conftest import register_mock_iex


class TestIdeaService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.app = flask_test_client()
        db.create_all()

    @requests_mock.Mocker()
    def test_save_new_idea(self, mock) -> None:
        register_mock_iex(mock)

        analyst = self.user_service \
            .save_new_user("email@email.com", "analyst", "password", is_analyst=True)

        exhibit1 = create_image_file("testexhibit1.png", "image/png")
        exhibit2 = create_image_file("testexhibit2.jpg", "image/jpg")

        new_idea_dict = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=313.49,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
            exhibits=[exhibit1, exhibit2],
            exhibit_title_map={"testexhibit1.png": "Exhibit 1", "testexhibit2.jpg": "Exhibit 2"}
        )
        new_idea = new_idea_dict["idea"]
        assert new_idea.analyst_id == analyst.id
        assert new_idea.symbol == "AAPL"
        assert new_idea.position_type == "long"
        assert new_idea.price_target == 400
        assert new_idea.company_name == "Apple, Inc."
        assert new_idea.market_cap > 500000000000
        assert new_idea.sector == "technology"
        assert new_idea.entry_price == 313.49
        # entry price withing 1% of last price
        assert abs(new_idea.last_price - new_idea.entry_price) / new_idea.last_price < 0.01
        assert new_idea.thesis_summary == "My Thesis Summary"
        assert new_idea.full_report == "My Full Report"
        exhibits = json.loads(new_idea.exhibits)
        assert f"{S3.S3_ENDPOINT_URL}/report_exhibits/" in exhibits[0]["url"]
        assert exhibits[0]["title"] == "Exhibit 1"
        assert f"{S3.S3_ENDPOINT_URL}/report_exhibits/" in exhibits[1]["url"]
        assert exhibits[1]["title"] == "Exhibit 2"
        assert new_idea.score == 0
        assert new_idea.num_upvotes == 0
        assert new_idea.num_downvotes == 0
        assert new_idea.num_comments == 0
        assert new_idea.num_downloads == 0
        assert new_idea.created_at < datetime.datetime.utcnow()
        assert str(type(new_idea.analyst)) == "<class 'app.main.model.user.UserModel'>"

    def test_upload_exhibit(self):
        image = create_image_file("test.png", "image/png")
        response_dict = self.idea_service.upload_exhibit("Title", "test.png", image)
        assert response_dict["url"] == f"{S3.S3_ENDPOINT_URL}/report_exhibits/test.png"
        assert response_dict["title"] == "Title"

    @requests_mock.Mocker()
    def test_get_idea_by_id(self, mock) -> None:
        register_mock_iex(mock)

        analyst = self.user_service \
            .save_new_user("email@email.com", "analyst", "password", is_analyst=True)

        new_idea_dict = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=313.49,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report"
        )
        new_idea = new_idea_dict["idea"]
        idea_in_db = self.idea_service.get_idea_by_id(new_idea.id)
        assert idea_in_db.id == new_idea.id

        # if idea doesn't exist
        idea = self.idea_service.get_idea_by_id(3)
        assert idea is None

    @requests_mock.Mocker()
    def test_query_ideas(self, mock) -> None:
        register_mock_iex(mock)

        analyst1 = self.user_service \
            .save_new_user("email1@email.com", "analyst1", "password", is_analyst=True)
        idea1_dict = self.idea_service.save_new_idea(
            analyst_id=analyst1.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            entry_price=313.49,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
        )
        idea1 = idea1_dict["idea"]

        analyst2 = self.user_service \
            .save_new_user("email2@email.com", "analyst2", "password", is_analyst=True)
        idea2_dict = self.idea_service.save_new_idea(
            analyst_id=analyst2.id,
            symbol="GM",
            position_type="short",
            price_target=10,
            entry_price=23.21,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
        )
        idea2 = idea2_dict["idea"]

        # no filters
        ideas = self.idea_service.query_ideas()
        assert len(ideas) == 2

        # filter by analyst
        ideas = self.idea_service.query_ideas(analyst_ids=[2])
        assert len(ideas) == 1
        assert ideas[0].symbol == "GM"

        # filter by symbol
        ideas = self.idea_service.query_ideas(query_string={"symbol": "aapl"})
        assert len(ideas) == 1
        assert ideas[0].symbol == "AAPL"

        # filter by position_type
        ideas = self.idea_service.query_ideas(query_string={"positionType": "short"})
        assert len(ideas) == 1
        assert ideas[0].symbol == "GM"

        # filter by sector
        ideas = self.idea_service.query_ideas(query_string={"sector": ["Consumer Discretionary"]})
        assert len(ideas) == 1
        assert ideas[0].symbol == "GM"

        # filter by multiple sectors
        ideas = self.idea_service.query_ideas(query_string={"sector": ["Consumer Discretionary", "Technology"]})
        assert len(ideas) == 2
        assert ideas[0].symbol == "GM"
        assert ideas[1].symbol == "AAPL"

        # filter by market cap
        ideas = self.idea_service.query_ideas(query_string={"marketCap": ["mega"]})
        assert len(ideas) == 1
        assert ideas[0].symbol == "AAPL"

        # filter by multiple market caps
        ideas = self.idea_service.query_ideas(query_string={"marketCap": ["mega", "large"]})
        assert len(ideas) == 2
        assert ideas[0].symbol == "GM"
        assert ideas[1].symbol == "AAPL"

        # filter by time period
        idea2.created_at = idea2.created_at - datetime.timedelta(days=100)
        self.idea_service.save_changes(idea2)
        ideas = self.idea_service.query_ideas(query_string={"timePeriod": 99})
        assert len(ideas) == 1
        assert ideas[0].symbol == idea1.symbol

        # sort by popularity (default)
        idea1.created_at = datetime.datetime.utcnow()
        self.idea_service.save_changes(idea1)
        ideas = self.idea_service.query_ideas()
        assert len(ideas) == 2
        assert ideas[0].symbol == idea1.symbol

        # sort by latest
        idea1.created_at = datetime.datetime.utcnow()
        self.idea_service.save_changes(idea1)
        ideas = self.idea_service.query_ideas(query_string={"sort": "latest"})
        assert len(ideas) == 2
        assert ideas[0].symbol == idea1.symbol

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
