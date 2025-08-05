import mysql.connector
import os
from typing import Dict, List, Optional

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

def get_portfolio_summary(symbol: str = None) -> Dict:
    """Get enhanced portfolio summary with P&L data"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return {"error": "Database connection failed"}
        
        cursor = db.cursor(dictionary=True)
        
        if symbol:
            # Get specific symbol summary even if the current price is not in api_stock_information, so left join is good
            cursor.execute("""
                SELECT h.stock_symbol, h.quantity, h.average_cost, s.current_price
                FROM holdings h
                LEFT JOIN api_stock_information s ON h.stock_symbol = s.stock_symbol
                WHERE h.stock_symbol = %s
            """, (symbol,))
        else:
            # Get all holdings with current prices
            cursor.execute("""
                SELECT h.stock_symbol, h.quantity, h.average_cost, s.current_price
                FROM holdings h
                LEFT JOIN api_stock_information s ON h.stock_symbol = s.stock_symbol
                ORDER BY h.stock_symbol
            """)
        
        holdings = cursor.fetchall()
        
        # Get total realized P&L for the period
        if symbol:
            cursor.execute("""
                SELECT COALESCE(SUM(realized_pnl), 0) as total_realized_pnl 
                FROM trades WHERE stock_symbol = %s AND trade_type = 'SELL'
            """, (symbol,))
        else:
            cursor.execute("""
                SELECT COALESCE(SUM(realized_pnl), 0) as total_realized_pnl 
                FROM trades WHERE trade_type = 'SELL'
            """)
        
        pnl_result = cursor.fetchone()
        total_realized_pnl = pnl_result['total_realized_pnl'] if pnl_result else 0
        
        # Calculate total portfolio value and unrealized P&L
        portfolio_value = 0
        total_cost_basis = 0
        unrealized_pnl = 0
        enhanced_holdings = []
        
        for holding in holdings:
            quantity = float(holding['quantity'])
            avg_cost = float(holding['average_cost'])
            # Use current_price from the join if available, otherwise use average_cost
            current_price = float(holding['current_price']) if holding['current_price'] else avg_cost
            
            market_value = current_price * quantity
            cost_basis = avg_cost * quantity
            holding_unrealized_pnl = market_value - cost_basis
            
            portfolio_value += market_value
            total_cost_basis += cost_basis
            unrealized_pnl += holding_unrealized_pnl
            
            # Create enhanced holding info
            enhanced_holdings.append({
                'stock_symbol': holding['stock_symbol'],
                'quantity': quantity,
                'average_cost': avg_cost,
                'current_price': current_price,
                'market_value': round(market_value, 2),
                'cost_basis': round(cost_basis, 2),
                'unrealized_pnl': round(holding_unrealized_pnl, 2),
                'unrealized_pnl_percent': round((holding_unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0, 2)
            })
        
        return {
            "holdings": enhanced_holdings,
            "summary": {
                "total_portfolio_value": round(portfolio_value, 2),
                "total_cost_basis": round(total_cost_basis, 2),
                "total_unrealized_pnl": round(unrealized_pnl, 2),
                "total_realized_pnl": float(total_realized_pnl),
                "total_pnl": round(unrealized_pnl + float(total_realized_pnl), 2),
                "unrealized_pnl_percent": round((unrealized_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0, 2),
                "holdings_count": len(enhanced_holdings)
            }
        }
        
    except Exception as e:
        print(f"Error getting portfolio summary: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()

def get_trade_history(symbol: str = None, limit: int = 50) -> Dict:
    """Get trade history for portfolio or specific symbol"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return {"error": "Database connection failed"}
        
        cursor = db.cursor(dictionary=True)
        
        if symbol:
            cursor.execute("""
                SELECT trade_id, stock_symbol, trade_type, price_at_trade, quantity, 
                       trade_date, realized_pnl 
                FROM trades 
                WHERE stock_symbol = %s 
                ORDER BY trade_date DESC 
                LIMIT %s
            """, (symbol, limit))
        else:
            cursor.execute("""
                SELECT trade_id, stock_symbol, trade_type, price_at_trade, quantity, 
                       trade_date, realized_pnl 
                FROM trades 
                ORDER BY trade_date DESC 
                LIMIT %s
            """, (limit,))
        
        trades = cursor.fetchall()
        
        # Convert decimal and datetime to serializable formats
        for trade in trades:
            if trade['realized_pnl']:
                trade['realized_pnl'] = float(trade['realized_pnl'])
            trade['price_at_trade'] = float(trade['price_at_trade'])
            trade['quantity'] = float(trade['quantity'])
            trade['trade_date'] = trade['trade_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            "trades": trades,
            "total_trades": len(trades)
        }
        
    except Exception as e:
        print(f"Error getting trade history: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()

def get_cash_balance(user_id: str = 'default_user') -> Dict:
    """Get current cash balance for user"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return {"error": "Database connection failed"}
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT cash_balance, updated_at FROM user_balance WHERE user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                "user_id": user_id,
                "cash_balance": float(result['cash_balance']),
                "updated_at": result['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {"error": "User not found"}
        
    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()

def update_cash_balance(user_id: str, new_balance: float) -> bool:
    """Update cash balance for user"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return False
        
        cursor = db.cursor()
        cursor.execute("""
            UPDATE user_balance SET cash_balance = %s WHERE user_id = %s
        """, (new_balance, user_id))
        
        db.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Error updating cash balance: {e}")
        return False
    finally:
        if db:
            db.close()

def get_portfolio_performance(days: int = 30) -> Dict:
    """Get portfolio performance over specified days"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return {"error": "Database connection failed"}
        
        cursor = db.cursor(dictionary=True)
        
        # Get trades in the last N days
        cursor.execute("""
            SELECT trade_type, SUM(quantity * price_at_trade) as total_value,
                   COUNT(*) as trade_count, SUM(COALESCE(realized_pnl, 0)) as total_pnl
            FROM trades 
            WHERE trade_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY trade_type
        """, (days,))
        
        trade_summary = cursor.fetchall()
        
        # Convert to readable format
        performance = {
            "period_days": days,
            "buy_volume": 0,
            "sell_volume": 0,
            "buy_trades": 0,
            "sell_trades": 0,
            "realized_pnl": 0
        }
        
        for summary in trade_summary:
            if summary['trade_type'] == 'BUY':
                performance['buy_volume'] = float(summary['total_value'])
                performance['buy_trades'] = summary['trade_count']
            elif summary['trade_type'] == 'SELL':
                performance['sell_volume'] = float(summary['total_value'])
                performance['sell_trades'] = summary['trade_count']
                performance['realized_pnl'] = float(summary['total_pnl'])
        
        return performance
        
    except Exception as e:
        print(f"Error getting portfolio performance: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()
