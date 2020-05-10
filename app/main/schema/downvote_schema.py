from app.main.ma import ma

from app.main.libs.util import camelcase
from app.main.model.downvote import DownvoteModel


class DownvoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DownvoteModel
        load_only = ("idea", "user")
        include_fk = True

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


downvote_schema = DownvoteSchema()
downvote_list_schema = DownvoteSchema(many=True)