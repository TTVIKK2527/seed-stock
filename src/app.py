import os
import secrets
from flask import Flask
from .controllers import pages
from .database import open_database
from .service import StockService


def create_app(database_url=None, stock=None):
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.secret_key = os.getenv("SESSION_SECRET") or secrets.token_hex(32)
    app.config.update(MAX_CONTENT_LENGTH=65536, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True)
    app.extensions["stock"] = stock or StockService(open_database(database_url or os.getenv("DATABASE_URL", "sqlite:///seed-stock.db")))
    app.register_blueprint(pages)
    return app


if __name__ == "__main__": create_app().run(host="127.0.0.1", port=5054, debug=False)
