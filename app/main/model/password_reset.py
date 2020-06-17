from uuid import uuid4
from time import time

from main.db import db

RESET_EXPIRATION_DELTA = 1800  # 30 minutes


class PasswordResetModel(db.Model):
    __tablename__ = "password_resets"

    id = db.Column(db.String(50), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex
        self.expire_at = int(time()) + RESET_EXPIRATION_DELTA

    @property
    def is_expired(self) -> bool:
        return time() > self.expire_at
