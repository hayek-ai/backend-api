import datetime
from app.main.db import db


class SubscriptionModel(db.Model):
    __tablename__ = "subscriptions"

    stripe_subscription_id = db.Column(db.String, primary_key=True, nullable=False)
    current_period_end = db.Column(db.BigInteger, nullable=False)
    stripe_price_id = db.Column(db.String, nullable=False)
    is_active = db.Column(db.String, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")
