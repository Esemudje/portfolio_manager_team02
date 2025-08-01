import mysql.connector
import datetime
import os
from typing import Dict, Optional
from .buyRequest import buyRequest
from .config import Config
from .portfolio import get_cash_balance, update_cash_balance

def get_db_connection():
    """Get database connection using config"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def test_database_connection() -> bool:
    """Test database connection and basic operations"""
    try:
        db = get_db_connection()
        if not db:
            return False
        
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        db.close()
        
        return result is not None
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False

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

        # Get current stock price
        cursor.execute(
            "SELECT current_price FROM api_stock_information WHERE stock_symbol = %s",
            (buy_request.symbol.upper(),)
        )
        result = cursor.fetchone()

        if not result:
            return f'Symbol {buy_request.symbol} not found in database'

        price = float(result['current_price'])
        total_cost = price * buy_request.quantity

        # Use provided cash or get from database
        if cash is None:
            cash_result = get_cash_balance(user_id)
            if 'error' in cash_result:
                return f"Error getting cash balance: {cash_result['error']}"
            cash = cash_result['cash_balance']

        if cash < total_cost:
            return f'Insufficient funds. Required: ${total_cost:.2f}, Available: ${cash:.2f}'

        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert into trades
        cursor.execute(
            "INSERT INTO trades (stock_symbol, trade_type, price_at_trade, quantity, trade_date) VALUES (%s, %s, %s, %s, %s)",
            (buy_request.symbol.upper(), "BUY", price, buy_request.quantity, date_time)
        )
        
        trade_id = cursor.lastrowid
        print(f"Trade successful. Trade ID: {trade_id}")

        # Check existing holdings
        cursor.execute(
            "SELECT quantity, average_cost FROM holdings WHERE stock_symbol = %s",
            (buy_request.symbol.upper(),)
        )
        results = cursor.fetchall()

        if results:
            # Update existing holding with new average cost
            existing_quantity = float(results[0]['quantity'])
            existing_avg_cost = float(results[0]['average_cost'])

            new_quantity = existing_quantity + buy_request.quantity
            new_avg_cost = (
                (existing_quantity * existing_avg_cost) + (buy_request.quantity * price)
            ) / new_quantity

            cursor.execute(
                "UPDATE holdings SET quantity = %s, average_cost = %s WHERE stock_symbol = %s",
                (new_quantity, round(new_avg_cost, 4), buy_request.symbol.upper())
            )
            print(f"Holding updated: {new_quantity} shares @ ${new_avg_cost:.4f} avg cost")
        else:
            # Insert new holding
            cursor.execute(
                "INSERT INTO holdings (stock_symbol, quantity, average_cost) VALUES (%s, %s, %s)",
                (buy_request.symbol.upper(), buy_request.quantity, price)
            )
            print(f"New holding added: {buy_request.quantity} shares @ ${price:.2f}")

        # Update cash balance if using database cash management
        if cash is not None:
            new_cash_balance = cash - total_cost
            update_cash_balance(user_id, new_cash_balance)
            print(f"Cash balance updated: ${new_cash_balance:.2f}")

        db.commit()
        
        return f"Transaction successful. Bought {buy_request.quantity} shares of {buy_request.symbol.upper()} at ${price:.2f} per share. Total cost: ${total_cost:.2f}"

    except mysql.connector.Error as err:
        if db:
            db.rollback()
        print(f"Database error: {err}")
        return f"Database error: {str(err)}"
    except ValueError as e:
        print(f"Value error: {e}")
        return f"Invalid data: {str(e)}"
    except Exception as e:
        if db:
            db.rollback()
        print(f"Unexpected error: {e}")
        return f"Error: {str(e)}"
    finally:
        if db:
            db.close()

def get_stock_quote(symbol: str) -> Dict:
    """Get current stock quote from database"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return {"error": "Database connection failed"}
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT stock_symbol, current_price, updated_at 
            FROM api_stock_information 
            WHERE stock_symbol = %s
        """, (symbol.upper(),))
        
        result = cursor.fetchone()
        if result:
            return {
                "symbol": result['stock_symbol'],
                "current_price": float(result['current_price']),
                "last_updated": result['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if result['updated_at'] else None
            }
        else:
            return {"error": f"Symbol {symbol} not found"}
            
    except Exception as e:
        print(f"Error getting stock quote: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()

def validate_buy_request(buy_request: buyRequest) -> Optional[str]:
    """Validate buy request parameters"""
    if not buy_request.symbol:
        return "Symbol is required"
    
    if len(buy_request.symbol.strip()) == 0:
        return "Symbol cannot be empty"
    
    if buy_request.quantity <= 0:
        return "Quantity must be positive"
    
    if not isinstance(buy_request.quantity, (int, float)):
        return "Quantity must be a number"
    
    return None  # No errors
