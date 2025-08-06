from flask import Blueprint, jsonify, request
import datetime
from .market import (
    get_quote, 
    get_stock_overview, 
    get_intraday_data, 
    get_daily_data, 
    test_api_connection
)
from .news import get_headlines
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
from .pnl import (
    calculate_unrealized_pnl, 
    get_realized_pnl_summary, 
    get_comprehensive_pnl_report
)
from .price_updater import manual_price_update, get_owned_symbols

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

@bp.get("/stocks/<symbol>/db-only")
def stock_quote_db_only(symbol):
    """Get stock quote from database cache only (no API fallback)"""
    try:
        print(f"API request received for database-only quote: {symbol}")
        data = get_stock_quote(symbol.upper())
        if 'error' in data:
            print(f"No cached data found for symbol: {symbol}")
            return {"error": data['error']}, 404
        print(f"Cached quote data sent for: {symbol}")
        return jsonify(data)
    except Exception as e:
        print(f"Error getting cached quote for {symbol}: {str(e)}")
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
        user_id = data.get('user_id', 'default_user')
        
        print(f"API request received for sell: {sell_req.quantity} shares of {sell_req.symbol}")
        # sell_stock now handles price fetching internally
        result = sell_stock(sell_req, user_id=user_id)
        
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

# Profit & Loss Endpoints
@bp.get("/pnl/unrealized")
def unrealized_pnl():
    """Get unrealized P&L for all holdings or specific symbol"""
    try:
        symbol = request.args.get('symbol')
        user_id = request.args.get('user_id', 'default_user')
        
        print(f"API request received for unrealized P&L: {symbol if symbol else 'all holdings'}")
        data = calculate_unrealized_pnl(symbol, user_id)
        
        if 'error' in data:
            return {"error": data['error']}, 500
            
        return jsonify(data)
    except Exception as e:
        print(f"Error getting unrealized P&L: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/pnl/realized")
def realized_pnl():
    """Get realized P&L summary"""
    try:
        symbol = request.args.get('symbol')
        days = int(request.args.get('days', 30))
        
        print(f"API request received for realized P&L: {symbol if symbol else 'all'} ({days} days)")
        data = get_realized_pnl_summary(symbol, days)
        
        if 'error' in data:
            return {"error": data['error']}, 500
            
        return jsonify(data)
    except Exception as e:
        print(f"Error getting realized P&L: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/pnl/comprehensive")
def comprehensive_pnl():
    """Get comprehensive P&L report (realized + unrealized)"""
    try:
        symbol = request.args.get('symbol')
        days = int(request.args.get('days', 30))
        
        print(f"API request received for comprehensive P&L: {symbol if symbol else 'all'} ({days} days)")
        data = get_comprehensive_pnl_report(symbol, days)
        
        if 'error' in data:
            return {"error": data['error']}, 500
            
        return jsonify(data)
    except Exception as e:
        print(f"Error getting comprehensive P&L: {str(e)}")
        return {"error": str(e)}, 500

# Price Update Endpoints
@bp.post("/prices/update")
def manual_update_prices():
    """Manually trigger price update for all owned stocks"""
    try:
        print("API request received to manually update prices")
        results = manual_price_update()
        
        successful_updates = sum(1 for success in results.values() if success)
        total_stocks = len(results)
        
        return jsonify({
            "status": "completed",
            "message": f"Updated {successful_updates}/{total_stocks} stocks",
            "results": results,
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"Error in manual price update: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/prices/owned-stocks")
def get_owned_stocks():
    """Get list of currently owned stock symbols"""
    try:
        print("API request received for owned stocks list")
        symbols = get_owned_symbols()
        
        return jsonify({
            "owned_stocks": symbols,
            "count": len(symbols),
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"Error getting owned stocks: {str(e)}")
        return {"error": str(e)}, 500

@bp.get("/news")
def get_news():
    try:
        print("Headline Request received")
        headlines = get_headlines()

        if isinstance(headlines, dict) and "error" in headlines:
            return {"error": headlines["error"]}, 500

        # Format the list of tuples into list of dicts for JSON response
        formatted = [{"headline": h, "reported_by": r} for h, r in headlines]
        return jsonify(formatted)

    except Exception as e:
        print(f"Error fetching headlines: {e}")
        return {"error": str(e)}, 500