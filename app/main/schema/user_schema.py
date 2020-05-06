from app.main.ma import ma

from app.main.libs.util import camelcase
from app.main.libs.strings import gettext
from app.main.model.user import UserModel
from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password_hash", "email", "is_admin", "connected_stripe_acct_id", "stripe_cust_id")

    @classmethod
    def on_bind_field(cls, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=Length(min=1, max=20))
    password = fields.Str(required=True, validate=Length(min=4))

    @validates('username')
    def no_special_symbols(self, value):
        """validates username"""
        special_sym = [' ', '{', '}', '(', ')', '[', ']', '#', ':', ';', '^', ',', '.', '?', '!', '|', '&', '`', '~',
                       '@', '$', '%', '/', '\\', '=', '+', '-', '*', "'", '"']

        if any(char in special_sym for char in value):
            raise ValidationError(gettext("username_invalid"))


class UserLoginSchema(Schema):
    emailOrUsername = fields.Str(required=True, validate=Length(min=1))
    password = fields.Str(required=True, validate=Length(min=1))


user_schema = UserSchema()
user_list_schema = UserSchema(many=True)
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()