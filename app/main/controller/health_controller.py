from flask_restful import Resource


class HealthCheck(Resource):
    @classmethod
    def get(cls):
        """Just a health check endpoint to make sure API is working"""
        return {"status": "working"}, 200
