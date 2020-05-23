import os
from requests import Response
from time import time

from app.main.db import db
from app.main.model.user import UserModel
from app.main.model.password_reset import PasswordResetModel
from app.main.libs.email import Email


class PasswordResetService:
    CLIENT_BASE_URL = os.environ.get("CLIENT_BASE_URL", None)

    def save_new_password_reset(self, user_id: int) -> "PasswordResetModel":
        new_password_reset = PasswordResetModel(user_id)
        self.save_changes(new_password_reset)
        return new_password_reset

    @classmethod
    def send_password_reset_email(cls, user_id: int) -> Response:
        user = UserModel.query.filter_by(id=user_id).first()
        subject = "Reset Your Password"
        link = f"{cls.CLIENT_BASE_URL}/password-reset/{user.most_recent_password_reset.id}"
        text = f"It looks like you forgot your password. Please click the link to reset it: {link}"
        html = f"<html>It looks like you forgot your password. \
        Please click the link to reset it: <a href={link}>reset password</a></html>"
        return Email.send_email([user.email], subject, text, html)

    @classmethod
    def get_password_reset_by_id(cls, password_reset_id: str) -> "PasswordResetModel":
        return PasswordResetModel.query.filter_by(id=password_reset_id).first()

    def force_to_expire(self, password_reset_id: str) -> None:
        password_reset = self.get_password_reset_by_id(password_reset_id)
        if not password_reset.is_expired:
            password_reset.expire_at = int(time())
            self.save_changes(password_reset)

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
