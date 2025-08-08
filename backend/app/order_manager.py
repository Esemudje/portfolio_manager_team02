import mysql.connector
import datetime
from typing import List, Dict, Optional, Tuple
from .order_request import OrderRequest, OrderType, OrderSide, OrderStatus
from .utils import get_db_connection, get_current_price
from .portfolio import get_cash_balance, update_cash_balance

class OrderManager:
    """Manages market order execution"""
    
    @staticmethod
    def place_order(order_request: OrderRequest) -> Dict:
        """Place a market order (executes immediately)"""
        try:
            # All orders are market orders and execute immediately
            return OrderManager._execute_market_order(order_request)
        except Exception as e:
            return {"error": f"Failed to place order: {str(e)}"}

    @staticmethod
    def _execute_market_order(order_request: OrderRequest) -> Dict:
        """Execute market order immediately"""
        try:
            # Get current price
            price_data = get_current_price(order_request.symbol)
            if 'error' in price_data:
                return {"error": f"Failed to get price for {order_request.symbol}: {price_data['error']}"}
            
            current_price = price_data['current_price']
            
            if order_request.side == OrderSide.BUY:
                result = OrderManager._execute_buy_order(order_request, current_price)
            else:
                result = OrderManager._execute_sell_order(order_request, current_price)
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to execute market order: {str(e)}"}

    @staticmethod
    def _execute_buy_order(order_request: OrderRequest, price: float) -> Dict:
        """Execute buy order"""
        try:
            total_cost = price * order_request.quantity
            
            # Check cash balance
            cash_result = get_cash_balance(order_request.user_id)
            if 'error' in cash_result:
                return {"error": f"Failed to get cash balance: {cash_result['error']}"}
            
            available_cash = cash_result['cash_balance']
            if total_cost > available_cash:
                return {"error": f"Insufficient funds. Required: ${total_cost:.2f}, Available: ${available_cash:.2f}"}
            
            # Execute the trade
            db = get_db_connection()
            if not db:
                return {"error": "Database connection failed"}
            
            cursor = db.cursor(dictionary=True)
            
            try:
                # Start transaction
                db.start_transaction()
                
                # Insert trade record
                trade_query = """
                    INSERT INTO trades (stock_symbol, trade_type, price_at_trade, quantity, trade_date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(trade_query, (
                    order_request.symbol, 'BUY', price, order_request.quantity, 
                    datetime.datetime.now()
                ))
                
                # Update cash balance
                new_balance = available_cash - total_cost
                balance_query = """
                    UPDATE user_balance SET cash_balance = %s 
                    WHERE user_id = %s
                """
                cursor.execute(balance_query, (new_balance, order_request.user_id))
                
                # Update holdings
                OrderManager._update_holdings_after_buy(cursor, order_request.symbol, order_request.quantity, price)
                
                # Commit transaction
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Market buy order successful: {order_request.quantity} shares of {order_request.symbol} at ${price:.2f}",
                    "filled_price": price,
                    "filled_quantity": order_request.quantity,
                    "total_cost": total_cost
                }
                
            except Exception as e:
                db.rollback()
                raise e
            finally:
                cursor.close()
                db.close()
                
        except Exception as e:
            return {"error": f"Failed to execute buy order: {str(e)}"}

    @staticmethod
    def _execute_sell_order(order_request: OrderRequest, price: float) -> Dict:
        """Execute sell order"""
        try:
            # Check if user has enough shares
            db = get_db_connection()
            if not db:
                return {"error": "Database connection failed"}
            
            cursor = db.cursor(dictionary=True)
            
            # Get current holdings
            cursor.execute("""
                SELECT quantity FROM holdings 
                WHERE stock_symbol = %s
            """, (order_request.symbol,))
            
            holding = cursor.fetchone()
            if not holding or holding['quantity'] < order_request.quantity:
                available = holding['quantity'] if holding else 0
                cursor.close()
                db.close()
                return {"error": f"Insufficient shares. Requested: {order_request.quantity}, Available: {available}"}
            
            try:
                # Start transaction
                db.start_transaction()
                
                # Execute FIFO sale
                result = OrderManager._execute_fifo_sale(cursor, order_request, price)
                if 'error' in result:
                    db.rollback()
                    return result
                
                # Insert trade record
                trade_query = """
                    INSERT INTO trades (stock_symbol, trade_type, price_at_trade, quantity, trade_date, realized_pnl)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(trade_query, (
                    order_request.symbol, 'SELL', price, order_request.quantity, 
                    datetime.datetime.now(), result['realized_pnl']
                ))
                
                # Update cash balance
                proceeds = price * order_request.quantity
                cash_result = get_cash_balance(order_request.user_id)
                if 'error' in cash_result:
                    db.rollback()
                    return cash_result
                
                new_balance = cash_result['cash_balance'] + proceeds
                balance_query = """
                    UPDATE user_balance SET cash_balance = %s 
                    WHERE user_id = %s
                """
                cursor.execute(balance_query, (new_balance, order_request.user_id))
                
                # Commit transaction
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Market sell order successful: {order_request.quantity} shares of {order_request.symbol} at ${price:.2f}",
                    "filled_price": price,
                    "filled_quantity": order_request.quantity,
                    "proceeds": proceeds,
                    "realized_pnl": result['realized_pnl']
                }
                
            except Exception as e:
                db.rollback()
                raise e
            finally:
                cursor.close()
                db.close()
                
        except Exception as e:
            return {"error": f"Failed to execute sell order: {str(e)}"}

    @staticmethod
    def _execute_fifo_sale(cursor, order_request: OrderRequest, sell_price: float) -> Dict:
        """Execute FIFO sale and calculate realized P&L"""
        try:
            # Get FIFO holdings
            cursor.execute("""
                SELECT trade_id, quantity, price_at_trade, trade_date 
                FROM trades 
                WHERE stock_symbol = %s AND trade_type = 'BUY' 
                ORDER BY trade_date ASC
            """, (order_request.symbol,))
            
            buy_trades = cursor.fetchall()
            
            shares_to_sell = order_request.quantity
            total_cost_basis = 0
            realized_pnl = 0
            
            for trade in buy_trades:
                if shares_to_sell <= 0:
                    break
                
                available_shares = float(trade['quantity'])
                cost_per_share = float(trade['price_at_trade'])
                
                if available_shares <= shares_to_sell:
                    # Sell all shares from this trade
                    shares_sold = available_shares
                    shares_to_sell -= available_shares
                    
                    # Update trade quantity to 0
                    cursor.execute("""
                        UPDATE trades SET quantity = 0 WHERE trade_id = %s
                    """, (trade['trade_id'],))
                else:
                    # Partial sale from this trade
                    shares_sold = shares_to_sell
                    remaining_shares = available_shares - shares_to_sell
                    shares_to_sell = 0
                    
                    # Update trade quantity
                    cursor.execute("""
                        UPDATE trades SET quantity = %s WHERE trade_id = %s
                    """, (remaining_shares, trade['trade_id']))
                
                # Calculate realized P&L for this portion
                cost_basis = shares_sold * cost_per_share
                proceeds = shares_sold * sell_price
                trade_pnl = proceeds - cost_basis
                
                total_cost_basis += cost_basis
                realized_pnl += trade_pnl
            
            # Update holdings
            cursor.execute("""
                SELECT quantity, average_cost FROM holdings 
                WHERE stock_symbol = %s
            """, (order_request.symbol,))
            
            holding = cursor.fetchone()
            if holding:
                current_quantity = float(holding['quantity'])
                new_quantity = current_quantity - order_request.quantity
                
                if new_quantity <= 0:
                    # Delete holding if no shares left
                    cursor.execute("""
                        DELETE FROM holdings WHERE stock_symbol = %s
                    """, (order_request.symbol,))
                else:
                    # Recalculate average cost for remaining shares
                    new_avg_cost = OrderManager._calculate_remaining_average_cost(
                        cursor, order_request.symbol, order_request.quantity
                    )
                    cursor.execute("""
                        UPDATE holdings SET quantity = %s, average_cost = %s 
                        WHERE stock_symbol = %s
                    """, (new_quantity, new_avg_cost, order_request.symbol))
            
            return {"realized_pnl": round(realized_pnl, 2)}
            
        except Exception as e:
            return {"error": f"Failed to execute FIFO sale: {str(e)}"}

    @staticmethod
    def _calculate_remaining_average_cost(cursor, symbol: str, shares_sold: int) -> float:
        """Calculate new average cost after FIFO sale"""
        # This is a simplified version - you may want to implement more sophisticated logic
        cursor.execute("""
            SELECT AVG(price_at_trade) as avg_price FROM trades 
            WHERE stock_symbol = %s AND trade_type = 'BUY' AND quantity > 0
        """, (symbol,))
        
        result = cursor.fetchone()
        return float(result['avg_price']) if result and result['avg_price'] else 0

    @staticmethod
    def _update_holdings_after_buy(cursor, symbol: str, quantity: int, price: float):
        """Update holdings after a buy transaction"""
        # Check if holding exists
        cursor.execute("""
            SELECT quantity, average_cost FROM holdings 
            WHERE stock_symbol = %s
        """, (symbol,))
        
        holding = cursor.fetchone()
        
        if holding:
            # Update existing holding
            current_quantity = float(holding['quantity'])
            current_avg_cost = float(holding['average_cost'])
            
            # Calculate new average cost
            total_cost = (current_quantity * current_avg_cost) + (quantity * price)
            new_quantity = current_quantity + quantity
            new_avg_cost = total_cost / new_quantity
            
            cursor.execute("""
                UPDATE holdings SET quantity = %s, average_cost = %s 
                WHERE stock_symbol = %s
            """, (new_quantity, new_avg_cost, symbol))
        else:
            # Create new holding
            cursor.execute("""
                INSERT INTO holdings (stock_symbol, quantity, average_cost)
                VALUES (%s, %s, %s)
            """, (symbol, quantity, price))
