from typing import List
from app.main.db import db
from app.main.model.user import UserModel
from app.main.model.follow import FollowModel
from sqlalchemy import and_


class FollowService:
    def save_new_follow(self, user_id: int, analyst_id: int) -> "FollowModel":
        follow = FollowModel(user_id=user_id, analyst_id=analyst_id)
        user = UserModel.query.filter_by(id=user_id).first()
        analyst = UserModel.query.filter_by(id=analyst_id).first()
        user.num_following = user.num_following + 1
        analyst.num_followers = analyst.num_followers + 1
        self.save_changes(user)
        self.save_changes(analyst)
        self.save_changes(follow)
        return follow

    @classmethod
    def get_follow_by_id(cls, follow_id: int) -> "FollowModel":
        return FollowModel.query.filter_by(id=follow_id).first()

    @classmethod
    def get_follow_by_user_and_analyst(cls, user_id: int, analyst_id: int) -> "FollowModel":
        filters = [FollowModel.user_id == user_id, FollowModel.analyst_id == analyst_id]
        return FollowModel.query.filter(and_(*filters)).first()

    def delete_follow(self, follow_id: int) -> None:
        follow = self.get_follow_by_id(follow_id)
        user = UserModel.query.filter_by(id=follow.user_id).first()
        analyst = UserModel.query.filter_by(id=follow.analyst_id).first()
        user.num_following = user.num_following - 1
        analyst.num_followers = analyst.num_followers - 1
        self.save_changes(user)
        self.save_changes(analyst)
        self.delete_from_db(follow)

    @classmethod
    def get_followers(cls, analyst_id: int) -> List["UserModel"]:
        """Returns all of the users that are following a given analyst"""
        return UserModel.query.join(FollowModel, UserModel.id == FollowModel.user_id)\
            .order_by(db.desc(FollowModel.created_at))\
            .filter_by(analyst_id=analyst_id).all()

    @classmethod
    def get_following(cls, user_id: int) -> List["UserModel"]:
        """Returns all of the analysts that a given user is following"""
        return UserModel.query.join(FollowModel, UserModel.id == FollowModel.analyst_id)\
            .order_by(db.desc(FollowModel.created_at))\
            .filter_by(user_id=user_id).all()

    @classmethod
    def delete_from_db(cls, data) -> None:
        db.session.delete(data)
        db.session.commit()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()