from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import os

db = SQLAlchemy() # SQLAlchemy instance for database interactions

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from .routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api") # Registering the API blueprint to the app

    @app.route("/")          # sanity check
    def health():
        print("Health check endpoint accessed")
        api_key_status = "configured" if os.getenv("ALPHA_VANTAGE_KEY") else "missing"
        return {
            "status": "ok",
            "message": "Portfolio Manager API is running",
            "api_key_status": api_key_status,
            "endpoints": {
                "quotes": "/api/stocks/<symbol>",
                "overview": "/api/stocks/<symbol>/overview",
                "intraday": "/api/stocks/<symbol>/intraday",
                "daily": "/api/stocks/<symbol>/daily",
                "news": "/api/stocks/<symbol>/news",
                "earnings": "/api/stocks/<symbol>/earnings",
                "test": "/api/test-connection"
            }
        }

    return app