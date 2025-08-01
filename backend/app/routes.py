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
from .portfolio import (
    get_portfolio_summary,
    get_trade_history,
    get_cash_balance,
    get_portfolio_performance
)
from .buy import buy_stock, get_stock_quote, validate_buy_request
from .sell import sell_stock, get_fifo_holdings
from .buyRequest import buyRequest
from .sellRequest import sellRequest

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

# Portfolio Management Endpoints
@bp.get("/portfolio")
def portfolio_summary():
    """Get complete portfolio summary"""
    try:
        symbol = request.args.get('symbol')
        print(f"API request received for portfolio summary: {symbol if symbol else 'all holdings'}")
        data = get_portfolio_summary(symbol)
        return jsonify(data)
    except Exception as e:
        print(f"Error getting portfolio summary: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/portfolio/trades")
def trade_history():
    """Get trade history"""
    try:
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 50))
        print(f"API request received for trade history: {symbol if symbol else 'all'}")
        data = get_trade_history(symbol, limit)
        return jsonify(data)
    except Exception as e:
        print(f"Error getting trade history: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/portfolio/cash")
def cash_balance():
    """Get current cash balance"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        print(f"API request received for cash balance: {user_id}")
        data = get_cash_balance(user_id)
        return jsonify(data)
    except Exception as e:
        print(f"Error getting cash balance: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/portfolio/performance")
def portfolio_performance():
    """Get portfolio performance metrics"""
    try:
        days = int(request.args.get('days', 30))
        print(f"API request received for portfolio performance: {days} days")
        data = get_portfolio_performance(days)
        return jsonify(data)
    except Exception as e:
        print(f"Error getting portfolio performance: {str(e)}")
        return {"error": str(e)}, 500

# Trading Endpoints
@bp.post("/trade/buy")
def trade_buy():
    """Execute buy order"""
    try:
        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400
        
        # Validate required fields
        if 'symbol' not in data or 'quantity' not in data:
            return {"error": "Symbol and quantity are required"}, 400
        
        # Create buy request
        buy_req = buyRequest(data['symbol'], int(data['quantity']))
        
        # Validate request
        validation_error = validate_buy_request(buy_req)
        if validation_error:
            return {"error": validation_error}, 400
        
        # Get cash balance or use provided amount
        cash = data.get('cash')
        user_id = data.get('user_id', 'default_user')
        
        print(f"API request received for buy: {buy_req.quantity} shares of {buy_req.symbol}")
        result = buy_stock(buy_req, cash, user_id)
        
        # Check if transaction was successful
        if "successful" in result.lower():
            return jsonify({"status": "success", "message": result})
        else:
            return jsonify({"status": "failed", "message": result}), 400
            
    except ValueError as e:
        return {"error": f"Invalid data format: {str(e)}"}, 400
    except Exception as e:
        print(f"Error processing buy order: {str(e)}")
        return {"error": str(e)}, 500

@bp.post("/trade/sell")
def trade_sell():
    """Execute sell order"""
    try:
        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400
        
        # Validate required fields
        if 'symbol' not in data or 'quantity' not in data:
            return {"error": "Symbol and quantity are required"}, 400
        
        # Create sell request
        sell_req = sellRequest(data['symbol'], int(data['quantity']))
        
        # Get current price from database
        quote_data = get_stock_quote(sell_req.symbol)
        if 'error' in quote_data:
            return {"error": f"Cannot get current price: {quote_data['error']}"}, 400
        
        current_price = quote_data['current_price']
        
        print(f"API request received for sell: {sell_req.quantity} shares of {sell_req.symbol}")
        result = sell_stock(sell_req, current_price)
        
        # Check if transaction was successful
        if "successful" in result.lower():
            return jsonify({"status": "success", "message": result})
        else:
            return jsonify({"status": "failed", "message": result}), 400
            
    except ValueError as e:
        return {"error": f"Invalid data format: {str(e)}"}, 400
    except Exception as e:
        print(f"Error processing sell order: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/trade/holdings/<symbol>")
def get_holdings_info(symbol):
    """Get FIFO holdings information for a symbol"""
    try:
        quantity = int(request.args.get('quantity', 1))
        print(f"API request received for holdings info: {symbol}")
        data = get_fifo_holdings(symbol.upper(), quantity)
        return jsonify({"symbol": symbol.upper(), "fifo_holdings": data})
    except Exception as e:
        print(f"Error getting holdings info: {str(e)}")
        return {"error": str(e)}, 500
