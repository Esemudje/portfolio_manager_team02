import mysql.connector
import datetime
import os
import time
import threading
from typing import List, Dict
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

def get_owned_symbols() -> List[str]:
    """Get list of stock symbols that are currently owned (in holdings)"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return []
        
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT stock_symbol 
            FROM holdings 
            WHERE quantity > 0
        """)
        
        results = cursor.fetchall()
        symbols = [row[0] for row in results]
        print(f"Found {len(symbols)} owned symbols: {symbols}")
        return symbols
        
    except Exception as e:
        print(f"Error getting owned symbols: {e}")
        return []
    finally:
        if db:
            db.close()

def update_single_stock_price(symbol: str) -> bool:
    """Update price for a single stock symbol"""
    db = None
    try:
        # Get fresh price from API
        print(f"Updating price for {symbol}...")
        api_data = get_quote(symbol.upper())
        
        if not api_data or '05. price' not in api_data:
            print(f"Failed to get price data for {symbol}")
            return False
        
        # Extract data from API response
        current_price = float(api_data.get('05. price', 0))
        open_price = float(api_data.get('02. open', current_price))
        high_price = float(api_data.get('03. high', current_price))
        low_price = float(api_data.get('04. low', current_price))
        previous_close = float(api_data.get('08. previous close', current_price))
        change_amount = float(api_data.get('09. change', 0))
        change_percent = api_data.get('10. change percent', '0%').rstrip('%')
        volume = int(api_data.get('06. volume', 0))
        latest_trading_day = api_data.get('07. latest trading day', datetime.date.today().strftime('%Y-%m-%d'))
        
        # Update database
        db = get_db_connection()
        if not db:
            return False
        
        cursor = db.cursor()
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
        print(f"[WORKS] Updated {symbol}: ${current_price:.2f}")
        return True
        
    except Exception as e:
        print(f"[XXXXXX] Error updating {symbol}: {e}")
        return False
    finally:
        if db:
            db.close()

def update_all_owned_prices() -> Dict[str, bool]:
    """Update prices for all owned stocks"""
    print(f"\n Starting price update cycle at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    owned_symbols = get_owned_symbols()
    if not owned_symbols:
        print("No owned stocks to update")
        return {}
    
    results = {}
    successful_updates = 0
    
    for symbol in owned_symbols:
        try:
            success = update_single_stock_price(symbol)
            results[symbol] = success
            if success:
                successful_updates += 1
            
            # Small delay between API calls to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"[XXXXXXXXX] Failed to update {symbol}: {e}")
            results[symbol] = False
    
    print(f"Price update completed: {successful_updates}/{len(owned_symbols)} successful")
    return results

def start_background_price_updater(interval_minutes: int = 1):
    """Start background thread that updates prices every N minutes"""
    def price_update_loop():
        print(f"Background price updater started (every {interval_minutes} minute(s))")
        
        while True:
            try:
                update_all_owned_prices()
                
                # Wait for the specified interval
                sleep_seconds = interval_minutes * 60
                print(f"💤 Sleeping for {interval_minutes} minute(s)...")
                time.sleep(sleep_seconds)
                
            except KeyboardInterrupt:
                print("[STOPPED] Background price updater stopped")
                break
            except Exception as e:
                print(f"[XXXXXXXXX] Error in price update loop: {e}")
                # Continue running even if there's an error
                time.sleep(30)  # Wait 30 seconds before retrying
    
    # Start the background thread
    update_thread = threading.Thread(target=price_update_loop, daemon=True)
    update_thread.start()
    return update_thread

def stop_price_updater():
    """Stop the background price updater (for testing/shutdown)"""
    # This would be implemented if needed for graceful shutdown
    pass

def manual_price_update():
    """Manually trigger a price update (for testing)"""
    print("Manual price update triggered")
    return update_all_owned_prices()

if __name__ == "__main__":
    # For testing - run a single update cycle
    print("Testing price updater...")
    results = manual_price_update()
    print(f"Test results: {results}")
