from flask import Flask, jsonify, request
import os
from .buyRequest import buyRequest
from .buy import buy_stock, test_database_connection

def create_app():
    app = Flask(__name__)

    from .routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api") # Registering the API blueprint to the app

    @app.route("/")          # sanity check
    def health():
        print("Health check endpoint accessed")
        
        # Test database connection
        db_status = "connected" if test_database_connection() else "disconnected"
        
        return jsonify({
            "status": "ok",
            "message": "Portfolio Manager API is running",
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