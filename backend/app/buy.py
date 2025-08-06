import mysql.connector
import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from .buyRequest import buyRequest
from .portfolio import get_cash_balance, update_cash_balance
from .utils import get_db_connection, get_current_price

# Load environment variables from .env file
load_dotenv()

def buy_stock(buy_request: buyRequest, cash: float = None, user_id: str = 'default_user') -> str:
    """Buy stock with enhanced error handling and cash management"""
    db = None

    try:
        # Validate input
        if buy_request.quantity <= 0:
            return "Quantity must be positive"
        
        if not buy_request.symbol or len(buy_request.symbol.strip()) == 0:
            return "Invalid symbol"

        db = get_db_connection()
        if not db:
            return "Database connection failed"

        cursor = db.cursor(dictionary=True)

        # Get current stock price using enhanced price fetching
        price_data = get_current_price(buy_request.symbol)
        if 'error' in price_data:
            return f'Error getting price for {buy_request.symbol}: {price_data["error"]}'

        price = price_data['current_price']
        print(f"Using price ${price:.2f} from {price_data['source']} for {buy_request.symbol}")
        total_cost = price * buy_request.quantity

        # Use provided cash or get from database
        if cash is None:
            cash_result = get_cash_balance(user_id)
            if 'error' in cash_result:
                return f"Error getting cash balance: {cash_result['error']}"
            cash = cash_result['cash_balance']

        # Check if user has enough cash
        if total_cost > cash:
            return f"Insufficient funds. Required: ${total_cost:.2f}, Available: ${cash:.2f}"

        # Start transaction
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Record the trade
        cursor.execute("""
            INSERT INTO trades (stock_symbol, trade_type, price_at_trade, quantity, trade_date) 
            VALUES (%s, %s, %s, %s, %s)
        """, (buy_request.symbol.upper(), "BUY", price, buy_request.quantity, date_time))
        
        # Update holdings - check if we already own this stock
        cursor.execute("""
            SELECT stock_symbol, quantity, average_cost FROM holdings WHERE stock_symbol = %s
        """, (buy_request.symbol.upper(),))
        
        existing_holding = cursor.fetchone()
        
        if existing_holding:
            # Update existing holding with weighted average cost
            old_quantity = float(existing_holding['quantity'])  
            old_avg_cost = float(existing_holding['average_cost'])  
            old_total_cost = old_quantity * old_avg_cost
            
            new_quantity = old_quantity + buy_request.quantity
            new_total_cost = old_total_cost + total_cost
            new_avg_cost = new_total_cost / new_quantity
            
            cursor.execute("""
                UPDATE holdings SET quantity = %s, average_cost = %s WHERE stock_symbol = %s
            """, (new_quantity, new_avg_cost, buy_request.symbol.upper()))
            
            print(f"Updated holding: {new_quantity} shares at ${new_avg_cost:.4f} avg cost")
        else:
            # Create new holding
            cursor.execute("""
                INSERT INTO holdings (stock_symbol, quantity, average_cost) VALUES (%s, %s, %s)
            """, (buy_request.symbol.upper(), buy_request.quantity, price))
            
            print(f"Created new holding: {buy_request.quantity} shares at ${price:.2f}")

        # Update cash balance
        new_cash_balance = cash - total_cost
        if not update_cash_balance(user_id, new_cash_balance):
            db.rollback()
            return "Failed to update cash balance"

        db.commit()
        print(f"Trade successful! Cash balance: ${new_cash_balance:.2f}")
        return f"Buy order successful: {buy_request.quantity} shares of {buy_request.symbol} at ${price:.2f}"

    except mysql.connector.Error as err:
        if db:
            db.rollback()
        print(f"Database error: {err}")
        return "Database error"
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error: {e}")
        return f"Error: {str(e)}"
    finally:
        if db:
            db.close()

def get_stock_quote(symbol: str) -> Dict:
    """Get stock quote from database cache (database-only, no API fallback)"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return {"error": "Database connection failed"}
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT stock_symbol, current_price, open_price, high_price, low_price,
                   volume, previous_close, change_amount, change_percent,
                   latest_trading_day, updated_at 
            FROM api_stock_information 
            WHERE stock_symbol = %s
        """, (symbol.upper(),))
        
        result = cursor.fetchone()
        
        if result and result['current_price']:
            change_percent_formatted = f"{result['change_percent']}%" if result['change_percent'] is not None else "0%"
            
            return {
                # Database format 
                "symbol": result['stock_symbol'],
                "current_price": float(result['current_price']) if result['current_price'] else 0,
                "change_amount": float(result['change_amount']) if result['change_amount'] else 0,
                "change_percent": change_percent_formatted,
                "volume": int(result['volume']) if result['volume'] else 0,
                "source": "database",
                "last_updated": result['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if result['updated_at'] else None,
                
                # API format compatibility
                "01. symbol": result['stock_symbol'],
                "02. open": str(result['open_price']) if result['open_price'] else "0",
                "03. high": str(result['high_price']) if result['high_price'] else "0", 
                "04. low": str(result['low_price']) if result['low_price'] else "0",
                "05. price": str(result['current_price']) if result['current_price'] else "0",
                "06. volume": str(result['volume']) if result['volume'] else "0",
                "07. latest trading day": result['latest_trading_day'] if result['latest_trading_day'] else None,
                "08. previous close": str(result['previous_close']) if result['previous_close'] else "0",
                "09. change": str(result['change_amount']) if result['change_amount'] else "0",
                "10. change percent": change_percent_formatted
            }
        else:
            return {"error": "No cached data found for this symbol"}
            
    except Exception as e:
        print(f"Error getting stock quote from database: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()

def validate_buy_request(buy_request: buyRequest) -> Optional[str]:
    """Validate buy request parameters"""
    if not buy_request:
        return "Buy request is required"
    
    if not buy_request.symbol or len(buy_request.symbol.strip()) == 0:
        return "Stock symbol is required"
    
    if buy_request.quantity <= 0:
        return "Quantity must be greater than 0"
    
    # Symbol length check
    if len(buy_request.symbol) > 10:
        return "Stock symbol too long"
    
    return None  # Valid request
