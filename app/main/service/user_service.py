from typing import List, TextIO
from sqlalchemy import func

from app.main.db import db
from app.main.libs.s3 import S3
from app.main.model.user import UserModel
from app.main.model.confirmation import ConfirmationModel


class UserService:
    def save_new_user(self, email: str, username: str, password: str, **kwargs) -> "UserModel":
        new_user = UserModel(
            email=email,
            username=username,
            password=password,
            image_url="https://hayek-image-assets.s3.amazonaws.com/user_images/no-img.svg",
            **kwargs
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

    def change_user_image(self, user_id: int, image: TextIO, filename: str) -> str:
        client = S3.get_client()

        try:
            # upload file to s3 bucket
            client.put_object(
                ACL="public-read",
                Body=image,
                Bucket=S3.S3_BUCKET,
                Key=f"user_images/{filename}",
                ContentType=image.content_type
            )
        except Exception as e:
            print(str(e))
            return None

        # update user profile image
        user = self.get_user_by_id(user_id)
        user.image_url = f"{S3.S3_ENDPOINT_URL}/user_images/{filename}"
        self.save_changes(user)
        return user.image_url

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
