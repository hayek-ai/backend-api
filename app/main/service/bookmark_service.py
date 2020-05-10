from typing import List
from app.main.db import db
from app.main.model.bookmark import BookmarkModel
from app.main.model.idea import IdeaModel


class BookmarkService:
    def save_new_bookmark(self, user_id: int, idea_id: int) -> "BookmarkModel":
        bookmark = BookmarkModel(user_id=user_id, idea_id=idea_id)
        self.save_changes(bookmark)
        return bookmark

    @classmethod
    def get_bookmark_by_id(cls, bookmark_id: int) -> "BookmarkModel":
        return BookmarkModel.query.filter_by(id=bookmark_id).first()

    def delete_bookmark_by_id(self, bookmark_id: int) -> None:
        bookmark = self.get_bookmark_by_id(bookmark_id)
        self.delete_from_db(bookmark)

    @classmethod
    def delete_from_db(cls, data) -> None:
        db.session.delete(data)
        db.session.commit()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
