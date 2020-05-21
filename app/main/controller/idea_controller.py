import json
from flask_restful import Resource, request
from flask_jwt_extended import get_jwt_identity, jwt_required


from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from app.main.schema.idea_schema import (
    idea_schema,
    new_idea_schema,
    idea_list_schema,
    idea_with_report_schema
)


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
        new_idea = self.idea_service.save_new_idea(
            analyst_id=analyst_id,
            symbol=request.form.get("symbol"),
            position_type=request.form.get("positionType"),
            bull_target=request.form.get("bullTarget"),
            bull_probability=request.form.get("bullProbability"),
            base_target=request.form.get("baseTarget"),
            base_probability=request.form.get("baseProbability"),
            bear_target=request.form.get("bearTarget"),
            bear_probability=request.form.get("bearProbability"),
            entry_price=request.form.get("entryPrice"),
            thesis_summary=request.form.get("thesisSummary"),
            full_report=request.form.get("fullReport"),
            exhibits=exhibits,
            exhibit_title_map=exhibit_title_map
        )

        if type(new_idea) == dict:
            return get_error(400, new_idea["error"])
        return self.idea_with_report_schema.dump(new_idea), 201


class Idea(Resource):
    def __init__(self, **kwargs):
        self.idea_service = kwargs['idea_service']
        self.user_service = kwargs['user_service']
        self.idea_schema = idea_schema

    @jwt_required
    def get(self, idea_id: int):
        idea = self.idea_service.get_idea_by_id(idea_id)
        if not idea:
            return get_error(404, get_text("not_found").format("Idea"))
        return self.idea_schema.dump(idea), 200

    @jwt_required
    def delete(self, idea_id: int):
        """Only Admin can delete idea"""
        user_id = get_jwt_identity()
        user = self.user_service.get_user_by_id(user_id)
        if not user.is_admin:
            return get_error(400, get_text("unauthorized_delete"))
        idea = self.idea_service.get_idea_by_id(idea_id)
        if not idea:
            return get_error(404, get_text("not_found").format("Idea"))
        try:
            self.idea_service.delete_idea_by_id(idea_id)
            return {"message": get_text("successfully_deleted").format("Idea")}, 200
        except Exception as e:
            return get_error(500, str(e))


class IdeaFeed(Resource):
    def __init__(self, **kwargs):
        self.idea_service = kwargs['idea_service']
        self.user_service = kwargs['user_service']
        self.follow_service = kwargs['follow_service']
        self.idea_list_schema = idea_list_schema

    @jwt_required
    def get(self, feed_type: str):
        """
        Returns idea feed for user.  feed_type can be either 'following' or 'discover'.
        Can be filtered with a querystring
        (sort, symbol, positionType, timePeriod, marketCap, sector)
        """
        user_id = get_jwt_identity()
        query_string = {}
        if request.args:
            possible_keys = ["symbol", "positionType", "timePeriod", "sort"]
            for key in possible_keys:
                if key in request.args:
                    query_string[key] = request.args[key]
            query_string["marketCap"] = request.args.getlist('marketCap')
            query_string["sector"] = request.args.getlist('sector')
        if feed_type == "following":
            following = self.follow_service.get_following(user_id)
            analyst_ids = [analyst.id for analyst in following]
            analyst_ids.append(user_id) # if analyst, own ideas should show in follow feed
            ideas = self.idea_service.query_ideas(analyst_ids=analyst_ids, query_string=query_string)
            return self.idea_list_schema.dump(ideas), 200
        elif feed_type == "discover":
            ideas = self.idea_service.query_ideas(query_string=query_string)
            return self.idea_list_schema.dump(ideas), 200
        else:
            return get_error(400, get_text("invalid_feed_type"))


class DownloadReport(Resource):
    def __init__(self, **kwargs):
        self.idea_service = kwargs["idea_service"]
        self.download_service = kwargs["download_service"]
        self.idea_with_report_schema = idea_with_report_schema

    @jwt_required
    def get(self, idea_id: int):
        user_id = get_jwt_identity()
        idea = self.idea_service.get_idea_by_id(idea_id)
        if not idea:
            return get_error(404, get_text("not_found").format("Idea"))
        financial_metrics = self.idea_service.get_idea_financial_metrics(idea.symbol)
        self.download_service.save_new_download(user_id=user_id, idea_id=idea.id)
        idea.num_downloads = idea.num_downloads + 1
        self.idea_service.save_changes(idea)
        return {
            **self.idea_with_report_schema.dump(idea),
            **financial_metrics
        }, 200
