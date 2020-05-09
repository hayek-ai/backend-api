from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length, Range

from app.main.libs.util import camelcase
from app.main.ma import ma
from app.main.model.review import ReviewModel


class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReviewModel
        load_only=("user", "analyst")
        include_fk = True

    @classmethod
    def on_bind_field(cls, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class NewReviewSchema(Schema):
    title = fields.Str(required=True, validate=Length(min=1, max=160))
    body = fields.Str(required=True, validate=Length(min=1, max=1000))
    stars = fields.Integer(required=True, validate=Range(min=1, max=5))
    user_id = fields.Integer(required=True, validate=Range(min=1))
    analyst_id = fields.Integer(required=True, validate=Range(min=1))


review_schema = ReviewSchema()
review_list_schema = ReviewSchema(many=True)
new_review_schema = NewReviewSchema()
