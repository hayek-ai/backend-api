import unittest
import datetime
from app.main.service.user_service import UserService
from app.main.service.idea_service import IdeaService
from app.main.db import db
from app.test.conftest import flask_test_client


class TestIdeaService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_service = UserService()
        self.idea_service = IdeaService()
        self.app = flask_test_client()
        db.create_all()

    def test_save_new_idea(self) -> None:
        analyst = self.user_service\
            .save_new_user("email@email.com", "analyst", "password", is_analyst=True)
        new_idea = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            company_name="Apple, Inc.",
            market_cap=1303162664400,
            sector="Technology",
            entry_price=300.66,
            last_price=300.66,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
            exhibits="Serialized list of URLs to S3 image assets"
        )

        assert new_idea.analyst_id == analyst.id
        assert new_idea.symbol == "AAPL"
        assert new_idea.position_type == "long"
        assert new_idea.price_target == 400
        assert new_idea.company_name == "Apple, Inc."
        assert new_idea.market_cap == 1303162664400
        assert new_idea.sector == "technology"
        assert new_idea.entry_price == 300.66
        assert new_idea.last_price == 300.66
        assert new_idea.thesis_summary == "My Thesis Summary"
        assert new_idea.full_report == "My Full Report"
        assert new_idea.exhibits == "Serialized list of URLs to S3 image assets"
        assert new_idea.score == 0
        assert new_idea.num_upvotes == 0
        assert new_idea.num_downvotes == 0
        assert new_idea.num_comments == 0
        assert new_idea.num_downloads == 0
        assert new_idea.created_at < datetime.datetime.utcnow()
        assert str(type(new_idea.analyst)) == "<class 'app.main.model.user.UserModel'>"

    def test_get_idea_by_id(self) -> None:
        analyst = self.user_service\
            .save_new_user("email@email.com", "analyst", "password", is_analyst=True)
        new_idea = self.idea_service.save_new_idea(
            analyst_id=analyst.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            company_name="Apple, Inc.",
            market_cap=1303162664400,
            sector="Technology",
            entry_price=300.66,
            last_price=300.66,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
            exhibits="Serialized list of URLs to S3 image assets"
        )
        idea = self.idea_service.get_idea_by_id(new_idea.id)
        assert idea.id == new_idea.id

        # if idea doesn't exist
        idea = self.idea_service.get_idea_by_id(3)
        assert idea is None

    def test_query_ideas(self) -> None:
        analyst1 = self.user_service\
            .save_new_user("email1@email.com", "analyst1", "password", is_analyst=True)
        idea1 = self.idea_service.save_new_idea(
            analyst_id=analyst1.id,
            symbol="AAPL",
            position_type="long",
            price_target=400,
            company_name="Apple, Inc.",
            market_cap=1303162664400,
            sector="Technology",
            entry_price=300.66,
            last_price=300.66,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
            exhibits="Serialized list of URLs to S3 image assets"
        )
        analyst2 = self.user_service\
            .save_new_user("email2@email.com", "analyst2", "password", is_analyst=True)
        idea2 = self.idea_service.save_new_idea(
            analyst_id=analyst2.id,
            symbol="GM",
            position_type="short",
            price_target=10,
            company_name="General Motors Company",
            market_cap=31000000000,
            sector="Industrials",
            entry_price=21.89,
            last_price=21.89,
            thesis_summary="My Thesis Summary",
            full_report="My Full Report",
            exhibits="Serialized list of URLs to S3 image assets"
        )

        # no filters
        ideas = self.idea_service.query_ideas()
        assert len(ideas) == 2

        # filter by symbol
        ideas = self.idea_service.query_ideas(query_string={"symbol": "aapl"})
        assert len(ideas) == 1
        assert ideas[0].symbol == "AAPL"

        # filter by position_type
        ideas = self.idea_service.query_ideas(query_string={"positionType": "short"})
        assert len(ideas) == 1
        assert ideas[0].symbol == "GM"

        # filter by sector
        ideas = self.idea_service.query_ideas(query_string={"sector": ["Industrials"]})
        assert len(ideas) == 1
        assert ideas[0].symbol == "GM"

        # filter by multiple sectors
        ideas = self.idea_service.query_ideas(query_string={"sector": ["Industrials", "Technology"]})
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

        # sort by popularity
        idea2.score = 100
        self.idea_service.save_changes(idea2)
        ideas = self.idea_service.query_ideas(query_string={"sort": "top"})
        assert len(ideas) == 2
        assert ideas[0].symbol == idea2.symbol

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()