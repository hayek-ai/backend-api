import datetime
from app.main.db import db


class SubscriptionModel(db.Model):
    __tablename__ = "subscriptions"

    stripe_subscription_id = db.Column(db.String(80), primary_key=True, nullable=False)
    current_period_end = db.Column(db.BigInteger, nullable=False)
    stripe_price_id = db.Column(db.String(80), nullable=False)
    latest_invoice_id = db.Column(db.String(80), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")
