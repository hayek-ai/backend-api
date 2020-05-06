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
        assert new_idea.sector == "Technology"
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

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()