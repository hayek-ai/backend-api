from typing import List
from main.db import db
from main.model.upvote import UpvoteModel
from main.model.idea import IdeaModel


class UpvoteService:
    def save_new_upvote(self, user_id: int, idea_id: int) -> "UpvoteModel":
        upvote = UpvoteModel(user_id=user_id, idea_id=idea_id)
        idea = IdeaModel.query.filter_by(id=idea_id).first()
        idea.num_upvotes = idea.num_upvotes + 1
        idea.score = idea.score + 1
        self.save_changes(idea)
        self.save_changes(upvote)
        return upvote

    @classmethod
    def get_upvote_by_id(cls, upvote_id: int) -> "UpvoteModel":
        return UpvoteModel.query.filter_by(id=upvote_id).first()

    @classmethod
    def get_upvote_by_user_and_idea(cls, user_id: int, idea_id: int) -> "UpvoteModel":
        filters = [UpvoteModel.user_id == user_id, UpvoteModel.idea_id == idea_id]
        return UpvoteModel.query.filter(*filters).first()

    def delete_upvote_by_id(self, upvote_id: int) -> None:
        upvote = self.get_upvote_by_id(upvote_id)
        if upvote is None:
            return
        idea = IdeaModel.query.filter_by(id=upvote.idea_id).first()
        if idea is None:
            return
        idea.num_upvotes = idea.num_upvotes - 1
        idea.score = idea.score - 1
        self.save_changes(idea)
        self.delete_from_db(upvote)

    def delete_upvote_by_user_and_idea_if_exists(self, user_id: int, idea_id: int) -> None:
        upvote = self.get_upvote_by_user_and_idea(user_id, idea_id)
        if upvote is None:
            return
        idea = IdeaModel.query.filter_by(id=upvote.idea_id).first()
        if idea is None:
            return
        idea.num_upvotes = idea.num_upvotes - 1
        idea.score = idea.score - 1
        self.save_changes(idea)
        self.delete_from_db(upvote)

    @classmethod
    def get_all_upvotes_for_idea(cls, idea_id: int) -> List["UpvoteModel"]:
        return UpvoteModel.query.order_by(db.desc(UpvoteModel.created_at)).filter_by(idea_id=idea_id).all()

    @classmethod
    def get_users_upvoted_ideas(cls, user_id: int) -> List["IdeaModel"]:
        return IdeaModel.query.join(UpvoteModel).order_by(db.desc(UpvoteModel.created_at))\
            .filter(UpvoteModel.user_id == user_id).all()

    @classmethod
    def delete_from_db(cls, data) -> None:
        db.session.delete(data)
        db.session.commit()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
