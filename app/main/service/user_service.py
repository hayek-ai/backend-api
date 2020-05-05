from typing import List
from sqlalchemy import func

from app.main.db import db
from app.main.model.user import User

"""
This file handles all of the logic relating to the user model.
"""


class UserService:
    def save_new_user(self, email: str, username: str, password: str) -> "User":
        new_user = User(
            email=email,
            username=username,
            password=password,
            image_url="https://hayek-bucket.s3.us-east-2.amazonaws.com/user_images/no-img.png"
        )
        self.save_changes(new_user)
        return new_user

    @classmethod
    def get_all_users(cls) -> List["User"]:
        return User.query.all()

    @classmethod
    def get_user_by_id(cls, user_id: int) -> "User":
        return User.query.filter_by(id=user_id).first()

    @classmethod
    def get_user_by_username(cls, username: str) -> "User":
        return User.query.filter(func.lower(User.username) == username.lower()).first()

    @classmethod
    def get_user_by_email(cls, email: str) -> "User":
        return User.query.filter(func.lower(User.email) == email.lower()).first()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
