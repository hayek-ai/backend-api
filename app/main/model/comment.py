import datetime

from main.db import db


class CommentModel(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    body = db.Column(db.String(1000), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    idea = db.relationship("IdeaModel")
