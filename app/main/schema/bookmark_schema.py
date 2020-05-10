from app.main.ma import ma

from app.main.libs.util import camelcase
from app.main.model.bookmark import BookmarkModel


class BookmarkSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BookmarkModel
        load_only = ("idea", "user")
        include_fk = True

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


bookmark_schema = BookmarkSchema()
bookmark_list_schema = BookmarkSchema(many=True)