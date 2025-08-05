import mysql.connector
import datetime
import os
from typing import List, Dict
from dotenv import load_dotenv
from .sellRequest import sellRequest
from .portfolio import get_portfolio_summary, get_cash_balance, update_cash_balance
from .market import get_quote
from .pnl import record_realized_pnl

# Load environment variables from .env file
load_dotenv()

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

def get_fifo_holdings(symbol: str, quantity_to_sell: int) -> List[Dict]:
    """Get holdings in FIFO order (oldest first) for selling"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        
        # Get all buy trades for this symbol ordered by date (FIFO)
        cursor.execute("""
            SELECT trade_id, quantity, price_at_trade, trade_date 
            FROM trades 
            WHERE stock_symbol = %s AND trade_type = 'BUY' 
            ORDER BY trade_date ASC
        """, (symbol,))
        
        buy_trades = cursor.fetchall()
        
        # Get all sell trades to calculate remaining quantities
        cursor.execute("""
            SELECT quantity, trade_date 
            FROM trades 
            WHERE stock_symbol = %s AND trade_type = 'SELL' 
            ORDER BY trade_date ASC
        """, (symbol,))
        
        sell_trades = cursor.fetchall()
        
        # Calculate available quantities using FIFO
        available_holdings = []
        total_sold = sum(float(trade['quantity']) for trade in sell_trades)  # Convert to float
        remaining_to_reduce = total_sold
        
        for buy_trade in buy_trades:
            buy_quantity = float(buy_trade['quantity'])  # Convert to float
            if remaining_to_reduce >= buy_quantity:
                # This entire buy trade has been sold
                remaining_to_reduce -= buy_quantity
                continue
            else:
                # This buy trade has partial or full quantity available
                available_quantity = buy_quantity - remaining_to_reduce
                remaining_to_reduce = 0
                
                if available_quantity > 0:
                    available_holdings.append({
                        'trade_id': buy_trade['trade_id'],
                        'available_quantity': available_quantity,
                        'price_at_trade': float(buy_trade['price_at_trade']),  # Convert to float
                        'trade_date': buy_trade['trade_date']
                    })
        
        return available_holdings
        
    except Exception as e:
        print(f"Error getting FIFO holdings: {e}")
        return []
    finally:
        if db:
            db.close()

def sell_stock(sell_request: sellRequest, current_price: float = None, user_id: str = 'default_user') -> str:
    """Sell stock using FIFO method with enhanced price fetching"""
    db = None
    
    try:
        # Get current price using API-first, database-fallback if not provided
        if current_price is None:
            price_data = get_current_price(sell_request.symbol)
            if 'error' in price_data:
                return f'Error getting price for {sell_request.symbol}: {price_data["error"]}'
            current_price = price_data['current_price']
            print(f"Using price ${current_price:.2f} from {price_data['source']} for {sell_request.symbol}")
        else:
            print(f"Using provided price ${current_price:.2f} for {sell_request.symbol}")
        
        # Get available holdings in FIFO order
        available_holdings = get_fifo_holdings(sell_request.symbol, sell_request.quantity)
        
        # Check if we have enough shares to sell
        total_available = sum(holding['available_quantity'] for holding in available_holdings)
        
        if total_available < sell_request.quantity:
            return f"Insufficient shares. Available: {total_available}, Requested: {sell_request.quantity}"
        
        db = get_db_connection()
        if not db:
            return "Database connection failed"
        
        cursor = db.cursor(dictionary=True)
        
        # Calculate realized P&L using FIFO
        remaining_to_sell = sell_request.quantity
        total_cost_basis = 0
        total_proceeds = sell_request.quantity * current_price
        
        for holding in available_holdings:
            if remaining_to_sell <= 0:
                break
                
            quantity_from_this_holding = min(remaining_to_sell, holding['available_quantity'])
            cost_basis = quantity_from_this_holding * holding['price_at_trade']  # Now already float
            total_cost_basis += cost_basis
            
            remaining_to_sell -= quantity_from_this_holding
        
        realized_pnl = total_proceeds - total_cost_basis
        
        # Record the sell transaction
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO trades (stock_symbol, trade_type, price_at_trade, quantity, trade_date, realized_pnl) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sell_request.symbol, "SELL", current_price, sell_request.quantity, date_time, realized_pnl))
        
        db.commit()
        trade_id = cursor.lastrowid
        
        # Record realized P&L in profit_and_loss table
        record_realized_pnl(sell_request.symbol, trade_id, realized_pnl)
        
        # Update holdings
        cursor.execute("""
            SELECT quantity, average_cost FROM holdings WHERE stock_symbol = %s
        """, (sell_request.symbol,))
        
        holding_result = cursor.fetchone()
        
        if holding_result:
            new_quantity = holding_result['quantity'] - sell_request.quantity
            
            if new_quantity <= 0:
                # Remove holding entirely
                cursor.execute("""
                    DELETE FROM holdings WHERE stock_symbol = %s
                """, (sell_request.symbol,))
                print("Holding removed completely")
            else:
                # Update holding quantity (average cost remains the same)
                cursor.execute("""
                    UPDATE holdings SET quantity = %s WHERE stock_symbol = %s
                """, (new_quantity, sell_request.symbol))
                print("Holding updated")
        
        db.commit()
        
        # Update cash balance with proceeds from sale
        total_proceeds = sell_request.quantity * current_price
        current_cash = get_cash_balance(user_id)
        if 'error' not in current_cash:
            new_cash_balance = current_cash['cash_balance'] + total_proceeds
            update_cash_balance(user_id, new_cash_balance)
            print(f"Cash balance updated: ${new_cash_balance:.2f} (+${total_proceeds:.2f})")
        
        print(f"Sell successful. Trade ID: {trade_id}")
        print(f"Realized P&L: ${realized_pnl:.2f}")
        
        return f"Transaction successful. Realized P&L: ${realized_pnl:.2f}"
        
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
