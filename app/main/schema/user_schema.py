from app.main.ma import ma

from app.main.libs.util import camelcase
from app.main.model.user import User
from marshmallow import Schema, fields


class UserRegisterSchema(Schema):
    email = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_only = ("password_hash", "email", "is_admin", "connected_stripe_acct_id", "stripe_cust_id")

    @classmethod
    def on_bind_field(cls, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


user_register_schema = UserRegisterSchema()
user_schema = UserSchema()
user_list_schema = UserSchema(many=True)
