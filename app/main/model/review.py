import datetime

from app.main.db import db


class ReviewModel(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    stars = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel", foreign_keys=[user_id])

    analyst_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    analyst = db.relationship("UserModel", foreign_keys=[analyst_id])

