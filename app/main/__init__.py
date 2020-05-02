from flask import Flask
from flask_cors import CORS
from app.main.config import app_config
from app.main.db import db

import json


def create_app(config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(app_config[config_name])

    @app.route("/hello")
    def hello():
        return json.dumps({'hello': 'world'})

    db.init_app(app)

    return app
