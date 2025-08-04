from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import os
from .buyRequest import buyRequest
from .buy import buy_stock, test_database_connection

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
        api_keys_str = os.getenv("ALPHA_VANTAGE_KEY")
        if api_keys_str:
            api_keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
            api_key_status = f"configured ({len(api_keys)} key{'s' if len(api_keys) > 1 else ''})"
        else:
            api_key_status = "missing"
        
        # Test database connection
        db_status = "connected" if test_database_connection() else "disconnected"
        
        return jsonify({
            "status": "ok",
            "message": "Portfolio Manager API is running",
            "api_key_status": api_key_status,
            "database_status": db_status,
            "endpoints": {
                "quotes": "/api/stocks/<symbol>",
                "overview": "/api/stocks/<symbol>/overview",
                "intraday": "/api/stocks/<symbol>/intraday",
                "daily": "/api/stocks/<symbol>/daily",
                "news": "/api/stocks/<symbol>/news",
                "earnings": "/api/stocks/<symbol>/earnings",
                "test": "/api/test-connection"
            }
        })

    return app