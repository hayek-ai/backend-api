import datetime

from main.db import db


class FollowModel(db.Model):
    __tablename__ = "follows"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel", foreign_keys=[user_id])

    analyst_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    analyst = db.relationship("UserModel", foreign_keys=[analyst_id])
