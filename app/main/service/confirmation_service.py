from requests import Response
from time import time

from app.main.db import db
from app.main.model.user import UserModel
from app.main.model.confirmation import ConfirmationModel
from app.main.libs.email import Email


class ConfirmationService:
    def save_new_confirmation(self, user_id: int) -> "ConfirmationModel":
        new_confirmation = ConfirmationModel(user_id)
        self.save_changes(new_confirmation)
        return new_confirmation

    @classmethod
    def send_confirmation_email(cls, user_id: int) -> Response:
        user = UserModel.query.filter_by(id=user_id).first()
        subject = f"Hi {user.username}! Please confirm your registration"
        code = user.most_recent_confirmation.code
        text = "Welcome to hayek.ai! Your signup passcode is {code}"
        html = f"<html>Welcome to hayek.ai! Your signup passcode is {code}</html>"
        return Email.send_email([user.email], subject, text, html)

    @classmethod
    def get_confirmation_by_id(cls, confirmation_id: int) -> "ConfirmationModel":
        return ConfirmationModel.query.filter_by(id=confirmation_id).first()

    def force_to_expire(self, confirmation_id: int) -> None:
        confirmation = self.get_confirmation_by_id(confirmation_id)
        if not confirmation.is_expired:
            confirmation.expire_at = int(time())
            self.save_changes(confirmation)

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
