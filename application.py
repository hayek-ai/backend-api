import os
from flask_restful import Resource, Api
from app import create_app

config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)

api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run()