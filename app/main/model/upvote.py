import datetime

from main.db import db


class UpvoteModel(db.Model):
    __tablename__ = "upvotes"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    idea = db.relationship("IdeaModel")
