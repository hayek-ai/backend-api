from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from marshmallow.validate import Length, Range

from app.main.libs.strings import get_text
from app.main.libs.util import camelcase
from app.main.ma import ma
from app.main.model.idea import IdeaModel
from app.main.schema.user_schema import UserSchema
from app.main.schema.comment_schema import CommentSchema


class IdeaSchema(ma.SQLAlchemyAutoSchema):
    analyst = ma.Nested(UserSchema(only=(
        'id', 'username', "image_url", "num_ideas", "analyst_rank",
        "analyst_rank_percentile", 'avg_return', 'success_rate',
        'avg_holding_period', "review_star_total", "num_reviews")))
    comments = ma.Nested(CommentSchema(many=True))

    class Meta:
        model = IdeaModel
        include_fk = True

    @classmethod
    def on_bind_field(cls, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class NewIdeaSchema(Schema):
    symbol = fields.Str(required=True, validate=Length(min=1, max=10))
    positionType = fields.Str(required=True, validate=Length(min=1))
    bullTarget = fields.Float(required=True, validate=Range(min=0))
    bullProbability = fields.Float(required=True, validate=Range(min=0, max=1))
    baseTarget = fields.Float(required=True, validate=Range(min=0))
    baseProbability = fields.Float(required=True, validate=Range(min=0, max=1))
    bearTarget = fields.Float(required=True, validate=Range(min=0))
    bearProbability = fields.Float(required=True, validate=Range(min=0, max=1))
    entryPrice = fields.Float(required=True, validate=Range(min=0))
    thesisSummary = fields.Str(required=True, validate=Length(min=1))
    fullReport = fields.Str(required=True, validate=Length(min=1))
    exhibitTitleMap = fields.Str()

    @validates('positionType')
    def must_be_long_or_short(self, value):
        position_type = value.strip().lower()
        if position_type != "long" and position_type != "short":
            raise ValidationError(get_text("invalid_position_type"))

    @validates_schema
    def validate_price_target(self, data, **kwargs):
        if data["bullProbability"] + data["baseProbability"] + data["bearProbability"] != 1:
            raise ValidationError(get_text("incorrect_target_probabilities"))

        price_target = (data["bullTarget"] * data["bullProbability"])\
            + (data["baseTarget"] * data["baseProbability"])\
            + (data["bearTarget"] * data["bearProbability"])
        position_type = data["positionType"].strip().lower()
        if position_type == "long":
            implied_return = (price_target / data["entryPrice"]) - 1
        else:
            implied_return = 1 - (price_target / data["entryPrice"])
        if implied_return < 0:
            raise ValidationError(get_text("negative_implied_return"))


idea_schema = IdeaSchema(exclude=("full_report", "exhibits", "comments"))
idea_list_schema = IdeaSchema(many=True, exclude=("full_report", "exhibits", "comments"))
new_idea_schema = NewIdeaSchema()
idea_with_report_schema = IdeaSchema()
