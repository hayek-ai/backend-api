from time import time
import random

from app.main.db import db

CONFIRMATION_EXPIRATION_DELTA = 1800 # 30 minutes


class ConfirmationModel(db.Model):
    __tablename__ = "confirmations"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), nullable=False)
    expire_at = db.Column(db.Integer, nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        self.is_confirmed = False
        self.code = f"{random.randint(100000, 999999)}"

    @property
    def is_expired(self) -> bool:
        return time() > self.expire_at
