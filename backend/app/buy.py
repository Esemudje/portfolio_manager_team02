import mysql.connector
import datetime
import os
from typing import Dict, Optional
from .buyRequest import buyRequest
from .portfolio import get_cash_balance, update_cash_balance
from .market import get_quote

def get_db_connection():
    """Get database connection using environment variables"""
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

def get_current_price(symbol: str) -> Dict:
    """Get current stock price with database-first, API-fallback strategy"""
    db = None
    try:
        # First, try to get price from database (fast)
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT stock_symbol, current_price, updated_at 
                FROM api_stock_information 
                WHERE stock_symbol = %s
            """, (symbol.upper(),))
            
            result = cursor.fetchone()
            if result:
                print(f"Price found in database for {symbol}: ${result['current_price']}")
                return {
                    "symbol": result['stock_symbol'],
                    "current_price": float(result['current_price']),
                    "source": "database",
                    "last_updated": result['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if result['updated_at'] else None
                }
        
        # If not found in database, get from API and cache it
        print(f"Price not found in database for {symbol}, fetching from API...")
        api_data = get_quote(symbol.upper())
        
        if api_data and '05. price' in api_data:
            current_price = float(api_data['05. price'])
            
            # Cache the price in database for future use
            cache_price_in_database(symbol.upper(), api_data)
            
            print(f"Fresh price from API for {symbol}: ${current_price}")
            return {
                "symbol": symbol.upper(),
                "current_price": current_price,
                "source": "api",
                "last_updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {"error": f"Unable to get price for {symbol} from API"}
            
    except Exception as e:
        print(f"Error getting current price for {symbol}: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()

def cache_price_in_database(symbol: str, api_data: Dict) -> bool:
    """Cache API price data in database for future use"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return False
            
        cursor = db.cursor()
        
        # Extract relevant data from API response
        current_price = float(api_data.get('05. price', 0))
        open_price = float(api_data.get('02. open', current_price))
        high_price = float(api_data.get('03. high', current_price))
        low_price = float(api_data.get('04. low', current_price))
        previous_close = float(api_data.get('08. previous close', current_price))
        change_amount = float(api_data.get('09. change', 0))
        change_percent = api_data.get('10. change percent', '0%').rstrip('%')
        volume = int(api_data.get('06. volume', 0))
        latest_trading_day = api_data.get('07. latest trading day', datetime.date.today().strftime('%Y-%m-%d'))
        
        # Insert or update the stock information
        cursor.execute("""
            INSERT INTO api_stock_information 
            (stock_symbol, open_price, high_price, low_price, current_price, volume, 
             latest_trading_day, previous_close, change_amount, change_percent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            open_price = VALUES(open_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            current_price = VALUES(current_price),
            volume = VALUES(volume),
            latest_trading_day = VALUES(latest_trading_day),
            previous_close = VALUES(previous_close),
            change_amount = VALUES(change_amount),
            change_percent = VALUES(change_percent),
            updated_at = CURRENT_TIMESTAMP
        """, (symbol, open_price, high_price, low_price, current_price, volume,
              latest_trading_day, previous_close, change_amount, change_percent))
        
        db.commit()
        print(f"Cached fresh price data for {symbol} in database")
        return True
        
    except Exception as e:
        print(f"Error caching price for {symbol}: {e}")
        return False
    finally:
        if db:
            db.close()

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
            SELECT stock_symbol, current_price, open_price, high_price, low_price, 
                   volume, previous_close, change_amount, change_percent, 
                   latest_trading_day, updated_at 
            FROM api_stock_information 
            WHERE stock_symbol = %s
        """, (symbol.upper(),))
        
        result = cursor.fetchone()
        if result:
            # Return data in both API format and database format for compatibility
            change_percent_formatted = f"{result['change_percent']}%" if result['change_percent'] is not None else "0%"
            
            return {
                # Database format (new)
                "symbol": result['stock_symbol'],
                "current_price": float(result['current_price']) if result['current_price'] else 0,
                "change_amount": float(result['change_amount']) if result['change_amount'] else 0,
                "change_percent": change_percent_formatted,
                "volume": int(result['volume']) if result['volume'] else 0,
                "last_updated": result['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if result['updated_at'] else None,
                
                # API format compatibility (for existing frontend code)
                "01. symbol": result['stock_symbol'],
                "02. open": str(result['open_price']) if result['open_price'] else "0",
                "03. high": str(result['high_price']) if result['high_price'] else "0", 
                "04. low": str(result['low_price']) if result['low_price'] else "0",
                "05. price": str(result['current_price']) if result['current_price'] else "0",
                "06. volume": str(result['volume']) if result['volume'] else "0",
                "07. latest trading day": result['latest_trading_day'] if result['latest_trading_day'] else None,
                "08. previous close": str(result['previous_close']) if result['previous_close'] else "0",
                "09. change": str(result['change_amount']) if result['change_amount'] else "0",
                "10. change percent": change_percent_formatted,
                "source": "database"
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
