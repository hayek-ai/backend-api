import datetime
import json
from flask_restful import Resource, request
from flask_jwt_extended import get_jwt_identity, jwt_required


from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from app.main.schema.idea_schema import (
    idea_schema,
    idea_list_schema,
    new_idea_schema,
    idea_with_report_schema)


class NewIdea(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']
        self.idea_service = kwargs['idea_service']
        self.idea_with_report_schema = idea_with_report_schema
        self.new_idea_schema = new_idea_schema

    @jwt_required
    def post(self):
        """Allows analyst to upload a new idea"""
        errors = self.new_idea_schema.validate(request.form)
        if errors:
            return get_error(400, get_text("incorrect_fields"), **errors)

        analyst_id = get_jwt_identity()
        analyst = self.user_service.get_user_by_id(analyst_id)
        if not analyst:
            return get_error(404, get_text("not_found").format("Analyst"))
        if not analyst.is_analyst:
            return get_error(400, get_text("not_an_analyst"))

        exhibits = request.files.getlist('exhibits')
        exhibit_title_map = json.loads(request.form.get("exhibitTitleMap")) if request.form.get("exhibitTitleMap") else None
        new_idea_dict = self.idea_service.save_new_idea(
            analyst_id=analyst_id,
            symbol=request.form.get("symbol"),
            position_type=request.form.get("positionType"),
            price_target=request.form.get("priceTarget"),
            entry_price=request.form.get("entryPrice"),
            thesis_summary=request.form.get("thesisSummary"),
            full_report=request.form.get("fullReport"),
            exhibits=exhibits,
            exhibit_title_map=exhibit_title_map
        )
        if "error" in new_idea_dict:
            return get_error(400, new_idea_dict["error"])
        return self.idea_with_report_schema.dump(new_idea_dict["idea"]), 201


class Idea(Resource):
    def __init__(self, **kwargs):
        self.idea_service = kwargs['idea_service']
        self.idea_schema = idea_schema

    @jwt_required
    def get(self, idea_id: int):
        idea = self.idea_service.get_idea_by_id(idea_id)
        if not idea:
            return get_error(404, get_text("not_found").format("Idea"))
        return self.idea_schema.dump(idea), 200


class DownloadReport(Resource):
    def __init__(self, **kwargs):
        self.idea_service = kwargs["idea_service"]
        self.idea_with_report_schema = idea_with_report_schema

    @jwt_required
    def get(self, idea_id: int):
        idea = self.idea_service.get_idea_by_id(idea_id)
        if not idea:
            return get_error(404, get_text("not_found").format("Idea"))
        idea.num_downloads = idea.num_downloads + 1
        self.idea_service.save_changes(idea)
        return self.idea_with_report_schema.dump(idea), 200
