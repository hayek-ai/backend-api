from typing import List
from app.main.db import db
from app.main.model.comment import CommentModel
from app.main.model.idea import IdeaModel


class CommentService:
    def save_new_comment(self, body: str, user_id: int, idea_id: int) -> "CommentModel":
        comment = CommentModel(body=body, user_id=user_id, idea_id=idea_id)
        idea = IdeaModel.query.filter_by(id=idea_id).first()
        idea.num_comments = idea.num_comments + 1
        self.save_changes(idea)
        self.save_changes(comment)
        return comment

    @classmethod
    def get_comment_by_id(cls, comment_id: int) -> "CommentModel":
        return CommentModel.query.filter_by(id=comment_id).first()

    def delete_comment_by_id(self, comment_id: int) -> "CommentModel":
        comment = self.get_comment_by_id(comment_id)
        idea = IdeaModel.query.filter_by(id=comment.idea_id).first()
        idea.num_comments = idea.num_comments - 1
        self.save_changes(idea)
        self.delete_from_db(comment)

    @classmethod
    def get_all_comments_for_idea(cls, idea_id: int) -> List["CommentModel"]:
        return CommentModel.query.order_by(db.desc(CommentModel.created_at)).filter_by(idea_id=idea_id).all()

    @classmethod
    def delete_from_db(cls, data) -> None:
        db.session.delete(data)
        db.session.commit()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()