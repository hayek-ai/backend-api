import datetime

from app.main.db import db


class BookmarkModel(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    idea = db.relationship("IdeaModel")
