from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import os
from .BuyRequest import BuyRequest
from .buy import buy_stock

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

    @app.route("/buy", methods=["POST"])
    def buy():
        data = request.json
        try:
            buy_request = BuyRequest(
                symbol=data["symbol"],
                quantity=int(data["quantity"]),
            )
            print(buy_stock(buy_request, 'portfolio', 1000.0))
            return jsonify({"message": "Buy successful"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return app