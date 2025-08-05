import mysql.connector
import datetime
from typing import List, Dict
from dotenv import load_dotenv
from .sellRequest import sellRequest
from .portfolio import get_portfolio_summary, get_cash_balance, update_cash_balance
from .pnl import record_realized_pnl
from .utils import get_db_connection, get_current_price

# Load environment variables from .env file
load_dotenv()

def calculate_remaining_average_cost(symbol: str, sold_shares_info: List[Dict], remaining_quantity: float) -> float:
    """Calculate the new average cost after FIFO sales"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return 0
        
        cursor = db.cursor(dictionary=True)
        
        # Get all BUY trades for this symbol in FIFO order (oldest first)
        cursor.execute("""
            SELECT price_at_trade, quantity, trade_date 
            FROM trades 
            WHERE stock_symbol = %s AND trade_type = 'BUY' 
            ORDER BY trade_date ASC
        """, (symbol.upper(),))
        
        buy_trades = cursor.fetchall()
        
        # Calculate what shares remain after the FIFO sales
        remaining_shares = []
        sold_so_far = 0
        
        # Track exactly how much was sold from each trade
        for sold_info in sold_shares_info:
            sold_so_far += sold_info['quantity']
        
        # Now determine what shares remain
        shares_to_skip = sold_so_far
        
        for trade in buy_trades:
            trade_quantity = float(trade['quantity'])
            trade_price = float(trade['price_at_trade'])
            
            if shares_to_skip >= trade_quantity:
                # This entire trade was sold
                shares_to_skip -= trade_quantity
                continue
            else:
                # Part or all of this trade remains
                remaining_from_this_trade = trade_quantity - shares_to_skip
                shares_to_skip = 0
                
                remaining_shares.append({
                    'quantity': remaining_from_this_trade,
                    'price': trade_price
                })
        
        # Calculate weighted average of remaining shares
        if not remaining_shares:
            return 0
        
        total_cost = sum(share['quantity'] * share['price'] for share in remaining_shares)
        total_quantity = sum(share['quantity'] for share in remaining_shares)
        
        new_average = total_cost / total_quantity if total_quantity > 0 else 0
        
        print(f"FIFO Average Calculation for {symbol}:")
        print(f"  Sold shares: {sold_so_far}")
        print(f"  Remaining shares: {total_quantity}")
        print(f"  New average cost: ${new_average:.4f}")
        
        return round(new_average, 4)
        
    except Exception as e:
        print(f"Error calculating remaining average cost: {e}")
        return 0
    finally:
        if db:
            db.close()

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
        
        # Calculate realized P&L using FIFO and track what was sold
        remaining_to_sell = sell_request.quantity
        total_cost_basis = 0
        total_proceeds = sell_request.quantity * current_price
        sold_shares_info = []  # Track exactly what was sold for average cost calculation
        
        for holding in available_holdings:
            if remaining_to_sell <= 0:
                break
                
            quantity_from_this_holding = min(remaining_to_sell, holding['available_quantity'])
            cost_basis = quantity_from_this_holding * holding['price_at_trade']
            total_cost_basis += cost_basis
            
            # Track what was sold
            sold_shares_info.append({
                'quantity': quantity_from_this_holding,
                'price': holding['price_at_trade']
            })
            
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
        
        # Update holdings with correct FIFO average cost calculation
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
                # Calculate new average cost based on remaining shares using FIFO
                new_average_cost = calculate_remaining_average_cost(
                    sell_request.symbol, sold_shares_info, new_quantity
                )
                
                cursor.execute("""
                    UPDATE holdings SET quantity = %s, average_cost = %s WHERE stock_symbol = %s
                """, (new_quantity, new_average_cost, sell_request.symbol))
                print(f"Holding updated: {new_quantity} shares @ ${new_average_cost:.4f} avg cost (was ${holding_result['average_cost']:.4f})")
        
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
