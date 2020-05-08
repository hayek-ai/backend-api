from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length, Range

from app.main.libs.strings import get_text
from app.main.libs.util import camelcase
from app.main.ma import ma
from app.main.model.idea import IdeaModel
from app.main.schema.user_schema import UserSchema


class IdeaSchema(ma.SQLAlchemyAutoSchema):
    analyst = ma.Nested(lambda: UserSchema(only=(
        'id', 'username', "image_url", "num_ideas", "analyst_rank",
        "analyst_rank_percentile", 'avg_return', 'success_rate',
        'avg_holding_period', "review_star_total", "num_reviews")))

    class Meta:
        model = IdeaModel
        include_fk = True

    @classmethod
    def on_bind_field(cls, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class NewIdeaSchema(Schema):
    symbol = fields.Str(required=True, validate=Length(min=1, max=10))
    positionType = fields.Str(required=True, validate=Length(min=1))
    priceTarget = fields.Float(required=True, validate=Range(min=0))
    entryPrice = fields.Float(required=True, validate=Range(min=0))
    thesisSummary = fields.Str(required=True, validate=Length(min=1))
    fullReport = fields.Str(required=True, validate=Length(min=1))
    exhibitTitleMap = fields.Str()

    @validates('positionType')
    def must_be_long_or_short(self, value):
        position_type = value.strip().lower()
        if position_type != "long" and position_type != "short":
            raise ValidationError(get_text("invalid_position_type"))


idea_schema = IdeaSchema(exclude=("full_report", "exhibits"))
idea_list_schema = IdeaSchema(many=True)
new_idea_schema = NewIdeaSchema()
idea_with_report_schema = IdeaSchema()
