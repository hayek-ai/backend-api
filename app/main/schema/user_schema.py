from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length

from main.libs.strings import get_text
from main.libs.util import camelcase
from main.ma import ma
from main.model.user import UserModel
from main.schema.upvote_schema import UpvoteSchema
from main.schema.downvote_schema import DownvoteSchema
from main.schema.bookmark_schema import BookmarkSchema


class UserSchema(ma.SQLAlchemyAutoSchema):
    upvotes = ma.Nested(UpvoteSchema, many=True)
    downvotes = ma.Nested(DownvoteSchema, many=True)
    bookmarks = ma.Nested(BookmarkSchema, many=True)

    class Meta:
        model = UserModel
        load_only = ("password_hash", "email", "is_admin", "connected_stripe_acct_id")

    @classmethod
    def on_bind_field(cls, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=Length(min=4, max=20))
    password = fields.Str(required=True, validate=Length(min=4))

    @validates('username')
    def no_special_symbols(self, value):
        """validates username"""
        special_sym = [' ', '{', '}', '(', ')', '[', ']', '#', ':', ';', '^', ',', '.', '?', '!', '|', '&', '`', '~',
                       '@', '$', '%', '/', '\\', '=', '+', '-', '*', "'", '"']

        if any(char in special_sym for char in value):
            raise ValidationError(get_text("username_invalid"))


class UserLoginSchema(Schema):
    emailOrUsername = fields.Str(required=True)
    password = fields.Str(required=True)


user_schema = UserSchema()
user_list_schema = UserSchema(many=True)
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
user_follow_list_schema = UserSchema(many=True, only=("id", "username", "image_url", "is_analyst"))
analyst_leaderboard_schema = UserSchema(many=True, exclude=('upvotes', 'downvotes', 'bookmarks'))
