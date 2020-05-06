from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length, Range

from app.main.libs.strings import get_text
from app.main.libs.util import camelcase
from app.main.ma import ma
from app.main.model.idea import IdeaModel


class IdeaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IdeaModel
        include_fk = True

    @classmethod
    def on_bind_field(cls, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class NewIdeaSchema(Schema):
    symbol = fields.Str(required=True, validate=Length(min=1, max=10))
    position_type = fields.Str(required=True, validate=Length(min=1))
    price_target = fields.Float(required=True, validate=Range(min=0))
    entry_price = fields.Float(required=True, validate=Range(min=0))
    last_price = fields.Float(required=True, validate=Range(min=0))
    thesis_summary = fields.Str(required=True, validate=Length(min=1))
    full_report = fields.Str(required=True, validate=Length(min=1))

    @validates('position_type')
    def must_be_long_or_short(self, value):
        position_type = value.strip().lower()
        if position_type != "long" or position_type != "short":
            raise ValidationError(get_text("invalid_position_type"))


idea_schema = IdeaSchema()
idea_list_schema = IdeaSchema(many=True)
new_idea_schema = NewIdeaSchema()
