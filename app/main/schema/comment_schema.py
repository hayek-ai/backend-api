from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length

from main.libs.strings import get_text
from main.libs.util import camelcase
from main.ma import ma
from main.model.comment import CommentModel
from main.schema.user_schema import UserSchema


class CommentSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested(UserSchema(only=("id", "username", "image_url")))

    class Meta:
        model = CommentModel
        load_only = ("idea",)
        include_fk = True

    @classmethod
    def on_bind_field(cls, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class NewCommentSchema(Schema):
    body = fields.Str(required=True, validate=Length(min=1, max=1000))


comment_schema = CommentSchema()
comment_list_schema = CommentSchema(many=True)
new_comment_schema = NewCommentSchema()