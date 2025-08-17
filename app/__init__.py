# app/__init__.py
from flask import Flask
from flask_cors import CORS

from .api.routes import api
from .core.config import settings
from .core.logging import configure_logging


def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": settings.CORS_ORIGINS}})
    app.register_blueprint(api, url_prefix=settings.API_PREFIX)  # e.g., /api/v1
    return app
