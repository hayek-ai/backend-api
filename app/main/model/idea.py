import datetime

from main.db import db


class IdeaModel(db.Model):
    __tablename__ = "ideas"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    symbol = db.Column(db.String(10), nullable=False)
    position_type = db.Column(db.String(10), nullable=False)
    agreed_to_terms = db.Column(db.Boolean, nullable=False)
    price_target = db.Column(db.Float, nullable=False)
    company_name = db.Column(db.String, nullable=False)
    market_cap = db.Column(db.BigInteger, nullable=False)
    sector = db.Column(db.String(80), nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    last_price = db.Column(db.Float, nullable=False)
    closed_date = db.Column(db.DateTime)
    score = db.Column(db.Integer, default=0)
    num_upvotes = db.Column(db.Integer, default=0)
    num_downvotes = db.Column(db.Integer, default=0)
    num_comments = db.Column(db.Integer, default=0)
    num_downloads = db.Column(db.Integer, default=0)
    thesis_summary = db.Column(db.String, nullable=False)
    full_report = db.Column(db.String, nullable=False)
    exhibits = db.Column(db.String)

    analyst_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    analyst = db.relationship("UserModel")
    comments = db.relationship("CommentModel", lazy="dynamic", cascade="all, delete-orphan")


