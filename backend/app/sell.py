import mysql.connector
import datetime
import os
from typing import List, Dict
from .sellRequest import sellRequest
from .config import Config
from .portfolio import get_portfolio_summary, get_cash_balance, update_cash_balance

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

def sell_stock(sell_request: sellRequest, current_price: float, user_id: str = 'default_user') -> str:
    """Sell stock using FIFO method"""
    db = None
    
    try:
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
