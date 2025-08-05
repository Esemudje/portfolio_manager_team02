import mysql.connector
import datetime
import os
from typing import Dict
from dotenv import load_dotenv
from .market import get_quote

# Load environment variables from .env file
load_dotenv()

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
    """Get current stock price with API-first, database-fallback strategy"""
    db = None
    api_error = None
    db_error = None
    
    try:
        # First, try to get fresh price from API
        print(f"Fetching fresh price from API for {symbol}...")
        api_data = get_quote(symbol.upper())
        
        if api_data and '05. price' in api_data:
            current_price = float(api_data['05. price'])
            
            # Cache the fresh price in database for future fallback use
            cache_success = cache_price_in_database(symbol.upper(), api_data)
            if cache_success:
                print(f"Fresh price cached in database for {symbol}")
            
            print(f"Fresh price from API for {symbol}: ${current_price}")
            return {
                "symbol": symbol.upper(),
                "current_price": current_price,
                "source": "api",
                "last_updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            api_error = "Invalid API response or missing price data"
            
    except Exception as e:
        api_error = str(e)
        print(f"API failed for {symbol}: {api_error}")
    
    # API failed, try database fallback
    try:
        print(f"API failed, trying database fallback for {symbol}...")
        db = get_db_connection()
        if db:
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
                print(f"Fallback price found in database for {symbol}: ${result['current_price']}")
                
                # Return data in both API format and database format for compatibility
                change_percent_formatted = f"{result['change_percent']}%" if result['change_percent'] is not None else "0%"
                
                return {
                    # Database format (new)
                    "symbol": result['stock_symbol'],
                    "current_price": float(result['current_price']) if result['current_price'] else 0,
                    "change_amount": float(result['change_amount']) if result['change_amount'] else 0,
                    "change_percent": change_percent_formatted,
                    "volume": int(result['volume']) if result['volume'] else 0,
                    "source": "database_fallback",
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
                    "10. change percent": change_percent_formatted
                }
            else:
                db_error = "No cached data found in database"
        else:
            db_error = "Database connection failed"
            
    except Exception as e:
        db_error = str(e)
        print(f"Database fallback failed for {symbol}: {db_error}")
    finally:
        if db:
            db.close()
    
    # Both API and database failed
    if "rate limit" in api_error.lower() if api_error else False:
        return {"error": f"Rate limit exceeded and no cached data found in database"}
    else:
        return {"error": f"Both API and database failed. API error: {api_error}. Database error: {db_error}"}

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
    """Test database connectivity"""
    db = None
    try:
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            print("Database connection test successful")
            return True
        else:
            print("Database connection test failed")
            return False
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False
    finally:
        if db:
            db.close()
