import datetime
from typing import List

from app.main.db import db
from app.main.model.user import User

"""
This file handles all of the logic relating to the user model.
"""


class UserService:
    def save_new_user(self, email: str, username: str, password: str):
        new_user = User(
            email=email,
            username=username,
            password=password,
            image_url="https://hayek-bucket.s3.us-east-2.amazonaws.com/user_images/no-img.png"
        )
        self.save_changes(new_user)
        return new_user

    @classmethod
    def get_all_users(cls):
        return User.query.all()

    @classmethod
    def get_user_by_id(cls, user_id: int):
        return User.query.filter_by(id=user_id).first()

    @classmethod
    def get_user_by_username(cls, username: str):
        return User.query.filter_by(username=username).first()

    @classmethod
    def get_user_by_email(cls, email: str):
        return User.query.filter_by(email=email).first()

    @classmethod
    def save_changes(cls, data) :
        db.session.add(data)
        db.session.commit()
