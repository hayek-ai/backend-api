from flask_restful import Resource
from main.libs.strings import get_text
from main.libs.util import get_error


class UpdatePerformance(Resource):
    def __init__(self, **kwargs):
        self.performance_service = kwargs['performance_service']

    def get(self):
        # try:
        self.performance_service.update_performance()
        return {"message": get_text("successfully_updated")}, 200
        # except Exception as e:
        #     return get_error(500, str(e))
