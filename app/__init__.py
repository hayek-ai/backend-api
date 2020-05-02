from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(".env")

from instance.config import app_config
from app.db import db

def create_app(config_name):
    app = Flask(__name__)
    CORS(app)    
    app.config.from_object(app_config[config_name])
    db.init_app(app)

    return app