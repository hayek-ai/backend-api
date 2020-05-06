from typing import List
from sqlalchemy import func

from app.main.db import db
from app.main.model.user import UserModel
from app.main.model.confirmation import ConfirmationModel
from app.main.libs.mailgun import Mailgun

"""
This file handles all of the logic relating to the user model.
"""


class UserService:
    def save_new_user(self, email: str, username: str, password: str) -> "User":
        new_user = UserModel(
            email=email,
            username=username,
            password=password,
            image_url="https://hayek-bucket.s3.us-east-2.amazonaws.com/user_images/no-img.png"
        )
        self.save_changes(new_user)
        confirmation = ConfirmationModel(new_user.id)
        self.save_changes(confirmation)
        return new_user

    @classmethod
    def get_all_users(cls) -> List["UserModel"]:
        return UserModel.query.all()

    @classmethod
    def get_user_by_id(cls, user_id: int) -> "UserModel":
        return UserModel.query.filter_by(id=user_id).first()

    @classmethod
    def get_user_by_username(cls, username: str) -> "UserModel":
        return UserModel.query.filter(func.lower(UserModel.username) == username.lower()).first()

    @classmethod
    def get_user_by_email(cls, email: str) -> "UserModel":
        return UserModel.query.filter(func.lower(UserModel.email) == email.lower()).first()

    def send_confirmation_email(self, user_id):
        user = self.get_user_by_id(user_id)
        subject = f"Hi {user.username}! Please confirm your registration"
        code = user.most_recent_confirmation.code
        text = f"Welcome to hayek.ai! Your signup passcode is {code}"
        html = f"<html>Welcome to hayek.ai! Your signup passcode is {code}</html>"
        return Mailgun.send_email([user.email], subject, text, html)

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
