from typing import List
from sqlalchemy import func

from app.main.db import db
from app.main.model.user import UserModel
from app.main.model.confirmation import ConfirmationModel


class UserService:
    def save_new_user(self, email: str, username: str, password: str, is_analyst=False) -> "UserModel":
        new_user = UserModel(
            email=email,
            username=username,
            password=password,
            is_analyst=is_analyst,
            image_url="https://hayek-image-assets.s3.amazonaws.com/user_images/no-img.svg"
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

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
