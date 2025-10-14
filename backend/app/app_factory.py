import os
from flask import Flask
from flask_cors import CORS
from config.config import config


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Enable CORS for cross-origin requests
    CORS(app, origins=["http://localhost:*", "http://127.0.0.1:*"])

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register blueprints
    from app.views.api_routes import api_bp

    app.register_blueprint(api_bp)

    return app
