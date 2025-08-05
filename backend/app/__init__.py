from flask import Flask, jsonify, request
import os
from .buyRequest import buyRequest
from .buy import buy_stock, test_database_connection
from .price_updater import start_background_price_updater, manual_price_update

def create_app():
    app = Flask(__name__)

    from .routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api") # Registering the API blueprint to the app

    # Start background price updater for owned stocks
    # Only starting if not in reloader process (prevents duplicate threads)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("Starting background price updater...")
        start_background_price_updater(interval_minutes=2)  # Update every 2 minutes

    @app.route("/")          # sanity check
    def health():
        print("Health check endpoint accessed")
        
        # Test database connection
        db_status = "connected" if test_database_connection() else "disconnected"
        
        # Get owned stocks count for price updater status
        try:
            from .price_updater import get_owned_symbols
            owned_stocks = get_owned_symbols()
            price_updater_status = f"monitoring {len(owned_stocks)} stocks"
        except:
            price_updater_status = "unknown"
        
        return jsonify({
            "status": "ok",
            "message": "Portfolio Manager API is running",
            "database_status": db_status,
            "price_updater_status": price_updater_status,
            "endpoints": {
                "quotes": "/api/stocks/<symbol>",
                "overview": "/api/stocks/<symbol>/overview",
                "intraday": "/api/stocks/<symbol>/intraday",
                "daily": "/api/stocks/<symbol>/daily",
                "news": "/api/stocks/<symbol>/news",
                "earnings": "/api/stocks/<symbol>/earnings",
                "test": "/api/test-connection",
                "manual_price_update": "/api/prices/update",
                "owned_stocks": "/api/prices/owned-stocks"
            }
        })

    return app