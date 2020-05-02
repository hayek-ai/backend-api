import os
from flask_restful import Resource, Api
from app.main import create_app

config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)

api = Api(app)

if __name__ == '__main__':
    app.run()