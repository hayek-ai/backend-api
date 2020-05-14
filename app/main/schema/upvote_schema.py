from app.main.ma import ma

from app.main.libs.util import camelcase
from app.main.model.upvote import UpvoteModel


class UpvoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UpvoteModel
        load_only = ("id", "created_at", "idea", "user")
        include_fk = True

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


upvote_schema = UpvoteSchema()
upvote_list_schema = UpvoteSchema(many=True)
