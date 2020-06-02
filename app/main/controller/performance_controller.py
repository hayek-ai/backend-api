from flask_restful import Resource


class UpdatePerformance(Resource):
    def __init__(self, **kwargs):
        self.performance_service = kwargs['performance_service']

    def get(self):
        self.performance_service.update_performance()
