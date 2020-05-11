from typing import List
from app.main.db import db
from app.main.model.downvote import DownvoteModel
from app.main.model.idea import IdeaModel


class DownvoteService:
    def save_new_downvote(self, user_id: int, idea_id: int) -> "DownvoteModel":
        downvote = DownvoteModel(user_id=user_id, idea_id=idea_id)
        idea = IdeaModel.query.filter_by(id=idea_id).first()
        idea.num_downvotes = idea.num_downvotes + 1
        idea.score = idea.score - 1
        self.save_changes(idea)
        self.save_changes(downvote)
        return downvote

    @classmethod
    def get_downvote_by_id(cls, downvote_id: int) -> "DownvoteModel":
        return DownvoteModel.query.filter_by(id=downvote_id).first()

    @classmethod
    def get_downvote_by_user_and_idea(cls, user_id: int, idea_id: int) -> "DownvoteModel":
        filters = [DownvoteModel.user_id == user_id, DownvoteModel.idea_id == idea_id]
        return DownvoteModel.query.filter(*filters).first()

    def delete_downvote_by_id(self, downvote_id: int) -> None:
        downvote = self.get_downvote_by_id(downvote_id)
        idea = IdeaModel.query.filter_by(id=downvote.idea_id).first()
        idea.num_downvotes = idea.num_downvotes - 1
        idea.score = idea.score + 1
        self.save_changes(idea)
        self.delete_from_db(downvote)

    @classmethod
    def get_all_downvotes_for_idea(cls, idea_id: int) -> List["DownvoteModel"]:
        return DownvoteModel.query.order_by(db.desc(DownvoteModel.created_at)).filter_by(idea_id=idea_id).all()

    @classmethod
    def delete_from_db(cls, data) -> None:
        db.session.delete(data)
        db.session.commit()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
