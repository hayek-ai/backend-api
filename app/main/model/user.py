import datetime
from main.db import db
from main.libs.security import encrypt_password, check_encrypted_password
from main.model.confirmation import ConfirmationModel
from main.model.password_reset import PasswordResetModel
from main.model.subscription import SubscriptionModel


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(256))
    is_analyst = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_confirmed = db.Column(db.Boolean, default=False)
    prefers_darkmode = db.Column(db.Boolean, default=False)
    bio = db.Column(db.String(1000))
    stripe_cust_id = db.Column(db.String(80), unique=True)
    pro_tier_status = db.Column(db.String(80), default=False)

    # Analyst Data
    connected_stripe_acct_id = db.Column(db.String(80), unique=True)
    num_followers = db.Column(db.Integer, default=0)
    num_following = db.Column(db.Integer, default=0)
    analyst_rank = db.Column(db.Integer)
    analyst_rank_percentile = db.Column(db.Float)
    avg_return = db.Column(db.Float)
    avg_return_percentile = db.Column(db.Float)
    avg_price_target_capture = db.Column(db.Float)
    avg_price_target_capture_percentile = db.Column(db.Float)
    success_rate = db.Column(db.Float)
    success_rate_percentile = db.Column(db.Float)
    statistical_significance = db.Column(db.Float)
    statistical_significance_percentile = db.Column(db.Float)
    avg_holding_period = db.Column(db.Float)
    avg_holding_period_percentile = db.Column(db.Float)
    num_ideas = db.Column(db.Integer, default=0)
    num_ideas_percentile = db.Column(db.Float)
    review_star_total = db.Column(db.Integer, default=0)
    num_reviews = db.Column(db.Integer, default=0)
    percent_buys = db.Column(db.Float)

    confirmation = db.relationship("ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan")
    password_reset = db.relationship("PasswordResetModel", lazy="dynamic", cascade="all, delete-orphan")
    ideas = db.relationship("IdeaModel", lazy="dynamic", cascade="all, delete-orphan")
    subscriptions = db.relationship("SubscriptionModel", lazy="dynamic", cascade="all, delete-orphan")
    upvotes = db.relationship("UpvoteModel", lazy="dynamic", cascade="all, delete-orphan")
    downvotes = db.relationship("DownvoteModel", lazy="dynamic", cascade="all, delete-orphan")
    bookmarks = db.relationship("BookmarkModel", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def password(self) -> None:
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password) -> bool:
        self.password_hash = encrypt_password(password)

    def check_password(self, password) -> bool:
        return check_encrypted_password(password, self.password_hash)

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    @property
    def most_recent_password_reset(self) -> "PasswordResetModel":
        return self.password_reset.order_by(db.desc(PasswordResetModel.expire_at)).first()

    @property
    def most_recent_subscription(self) -> "SubscriptionModel":
        return self.subscriptions.order_by(db.desc(SubscriptionModel.current_period_end)).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)
