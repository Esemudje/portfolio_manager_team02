from flask import Blueprint, jsonify, request
from .market import (
    get_quote, 
    get_stock_overview, 
    get_intraday_data, 
    get_daily_data, 
    get_news_sentiment, 
    get_company_earnings,
    test_api_connection
)

bp = Blueprint("api", __name__) # helps organize routes 

@bp.get("/stocks/<symbol>")
def stock_quote(symbol):
    """Get real-time quote for a stock symbol"""
    try:
        print(f"API request received for quote: {symbol}")
        data = get_quote(symbol.upper())
        if not data:
            print(f"No data found for symbol: {symbol}")
            return {"error": "Symbol not found"}, 404
        print(f"Quote data sent for: {symbol}")
        return jsonify(data)
    except Exception as e:
        print(f"Error getting quote for {symbol}: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/stocks/<symbol>/overview")
def stock_overview(symbol):
    """Get comprehensive company overview"""
    try:
        print(f"API request received for overview: {symbol}")
        data = get_stock_overview(symbol.upper())
        if not data:
            print(f"No overview data found for symbol: {symbol}")
            return {"error": "Symbol not found"}, 404
        print(f"Overview data sent for: {symbol}")
        return jsonify(data)
    except Exception as e:
        print(f"Error getting overview for {symbol}: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/stocks/<symbol>/intraday")
def stock_intraday(symbol):
    """Get intraday data for a stock"""
    try:
        interval = request.args.get('interval', '5min')
        print(f"API request received for intraday: {symbol} ({interval})")
        data = get_intraday_data(symbol.upper(), interval)
        if not data:
            print(f"No intraday data found for symbol: {symbol}")
            return {"error": "Symbol not found"}, 404
        print(f"Intraday data sent for: {symbol}")
        return jsonify(data)
    except Exception as e:
        print(f"Error getting intraday data for {symbol}: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/stocks/<symbol>/daily")
def stock_daily(symbol):
    """Get daily data for a stock"""
    try:
        print(f"API request received for daily: {symbol}")
        data = get_daily_data(symbol.upper())
        if not data:
            print(f"No daily data found for symbol: {symbol}")
            return {"error": "Symbol not found"}, 404
        print(f"Daily data sent for: {symbol}")
        return jsonify(data)
    except Exception as e:
        print(f"Error getting daily data for {symbol}: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/stocks/<symbol>/news")
def stock_news(symbol):
    """Get news and sentiment for a stock"""
    try:
        topics = request.args.get('topics')
        print(f"API request received for news: {symbol}")
        data = get_news_sentiment(symbol.upper(), topics)
        if not data:
            print(f"No news data found for symbol: {symbol}")
            return {"error": "Symbol not found"}, 404
        print(f"News data sent for: {symbol}")
        return jsonify(data)
    except Exception as e:
        print(f"Error getting news for {symbol}: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/stocks/<symbol>/earnings")
def stock_earnings(symbol):
    """Get earnings data for a stock"""
    try:
        print(f"🔍 API request received for earnings: {symbol}")
        data = get_company_earnings(symbol.upper())
        if not data:
            print(f"No earnings data found for symbol: {symbol}")
            return {"error": "Symbol not found"}, 404
        print(f"Earnings data sent for: {symbol}")
        return jsonify(data)
    except Exception as e:
        print(f"Error getting earnings for {symbol}: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/test-connection")
def test_connection():
    """Test API connection"""
    try:
        print("Testing API connection...")
        success = test_api_connection()
        if success:
            print("API connection test successful")
            return jsonify({"status": "success", "message": "API connection working"})
        else:
            print("API connection test failed")
            return jsonify({"status": "failed", "message": "API connection failed"}), 500
    except Exception as e:
        print(f"Error testing connection: {str(e)}")
        return {"error": str(e)}, 500
