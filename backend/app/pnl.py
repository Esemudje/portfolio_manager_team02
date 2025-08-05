import mysql.connector
import datetime
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

def record_realized_pnl(stock_symbol: str, trade_id: int, realized_pnl: float) -> bool:
    """Record realized P&L in the profit_and_loss table"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return False
        
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO profit_and_loss (stock_symbol, trade_id, realized_pnl, calculation_date)
            VALUES (%s, %s, %s, %s)
        """, (stock_symbol.upper(), trade_id, realized_pnl, datetime.datetime.now()))
        
        db.commit()
        print(f"Recorded realized P&L: ${realized_pnl:.2f} for {stock_symbol}")
        return True
        
    except Exception as e:
        print(f"Error recording realized P&L: {e}")
        return False
    finally:
        if db:
            db.close()

def calculate_unrealized_pnl(stock_symbol: str = None, user_id: str = 'default_user') -> Dict:
    """Calculate unrealized P&L for holdings"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return {"error": "Database connection failed"}
        
        cursor = db.cursor(dictionary=True)
        
        # Build query based on whether specific symbol is requested
        if stock_symbol:
            holdings_query = """
                SELECT h.stock_symbol, h.quantity, h.average_cost, s.current_price
                FROM holdings h
                LEFT JOIN api_stock_information s ON h.stock_symbol = s.stock_symbol
                WHERE h.stock_symbol = %s
            """
            cursor.execute(holdings_query, (stock_symbol.upper(),))
        else:
            holdings_query = """
                SELECT h.stock_symbol, h.quantity, h.average_cost, s.current_price
                FROM holdings h
                LEFT JOIN api_stock_information s ON h.stock_symbol = s.stock_symbol
                WHERE h.quantity > 0
            """
            cursor.execute(holdings_query)
        
        holdings = cursor.fetchall()
        
        if not holdings:
            return {"unrealized_pnl": 0, "holdings": [], "total_market_value": 0, "total_cost_basis": 0}
        
        unrealized_positions = []
        total_unrealized_pnl = 0
        total_market_value = 0
        total_cost_basis = 0
        
        for holding in holdings:
            symbol = holding['stock_symbol']
            quantity = float(holding['quantity'])
            avg_cost = float(holding['average_cost'])
            current_price = float(holding['current_price']) if holding['current_price'] else avg_cost
            
            cost_basis = quantity * avg_cost
            market_value = quantity * current_price
            unrealized_pnl = market_value - cost_basis
            unrealized_pnl_percent = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            total_unrealized_pnl += unrealized_pnl
            total_market_value += market_value
            total_cost_basis += cost_basis
            
            unrealized_positions.append({
                "symbol": symbol,
                "quantity": quantity,
                "average_cost": avg_cost,
                "current_price": current_price,
                "cost_basis": round(cost_basis, 2),
                "market_value": round(market_value, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "unrealized_pnl_percent": round(unrealized_pnl_percent, 2)
            })
        
        return {
            "unrealized_pnl": round(total_unrealized_pnl, 2),
            "total_market_value": round(total_market_value, 2),
            "total_cost_basis": round(total_cost_basis, 2),
            "unrealized_pnl_percent": round((total_unrealized_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0, 2),
            "holdings": unrealized_positions
        }
        
    except Exception as e:
        print(f"Error calculating unrealized P&L: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()

def get_realized_pnl_summary(stock_symbol: str = None, days: int = 30) -> Dict:
    """Get realized P&L summary for specified period"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return {"error": "Database connection failed"}
        
        cursor = db.cursor(dictionary=True)
        
        # Calculate date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        if stock_symbol:
            query = """
                SELECT 
                    t.stock_symbol,
                    t.trade_id,
                    t.realized_pnl,
                    t.trade_date,
                    t.quantity,
                    t.price_at_trade
                FROM trades t
                WHERE t.trade_type = 'SELL' 
                AND t.stock_symbol = %s
                AND t.trade_date >= %s
                AND t.realized_pnl IS NOT NULL
                ORDER BY t.trade_date DESC
            """
            cursor.execute(query, (stock_symbol.upper(), start_date))
        else:
            query = """
                SELECT 
                    t.stock_symbol,
                    t.trade_id,
                    t.realized_pnl,
                    t.trade_date,
                    t.quantity,
                    t.price_at_trade
                FROM trades t
                WHERE t.trade_type = 'SELL' 
                AND t.trade_date >= %s
                AND t.realized_pnl IS NOT NULL
                ORDER BY t.trade_date DESC
            """
            cursor.execute(query, (start_date,))
        
        realized_trades = cursor.fetchall()
        
        if not realized_trades:
            return {
                "total_realized_pnl": 0,
                "trades_count": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "average_win": 0,
                "average_loss": 0,
                "trades": []
            }
        
        total_realized_pnl = 0
        winning_trades = 0
        losing_trades = 0
        total_wins = 0
        total_losses = 0
        
        trades_list = []
        
        for trade in realized_trades:
            pnl = float(trade['realized_pnl'])
            total_realized_pnl += pnl
            
            if pnl > 0:
                winning_trades += 1
                total_wins += pnl
            elif pnl < 0:
                losing_trades += 1
                total_losses += pnl
            
            trades_list.append({
                "symbol": trade['stock_symbol'],
                "trade_id": trade['trade_id'],
                "realized_pnl": round(pnl, 2),
                "trade_date": trade['trade_date'].strftime('%Y-%m-%d %H:%M:%S'),
                "quantity": float(trade['quantity']),
                "price": float(trade['price_at_trade'])
            })
        
        total_trades = len(realized_trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        average_win = (total_wins / winning_trades) if winning_trades > 0 else 0
        average_loss = (total_losses / losing_trades) if losing_trades > 0 else 0
        
        return {
            "total_realized_pnl": round(total_realized_pnl, 2),
            "trades_count": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "average_win": round(average_win, 2),
            "average_loss": round(average_loss, 2),
            "period_days": days,
            "trades": trades_list
        }
        
    except Exception as e:
        print(f"Error getting realized P&L summary: {e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()

def get_comprehensive_pnl_report(stock_symbol: str = None, days: int = 30) -> Dict:
    """Get comprehensive P&L report combining realized and unrealized"""
    try:
        # Get realized P&L
        realized_pnl = get_realized_pnl_summary(stock_symbol, days)
        
        # Get unrealized P&L
        unrealized_pnl = calculate_unrealized_pnl(stock_symbol)
        
        if 'error' in realized_pnl or 'error' in unrealized_pnl:
            return {"error": "Failed to calculate comprehensive P&L"}
        
        total_pnl = realized_pnl['total_realized_pnl'] + unrealized_pnl['unrealized_pnl']
        
        return {
            "summary": {
                "total_pnl": round(total_pnl, 2),
                "realized_pnl": realized_pnl['total_realized_pnl'],
                "unrealized_pnl": unrealized_pnl['unrealized_pnl'],
                "total_market_value": unrealized_pnl['total_market_value'],
                "total_cost_basis": unrealized_pnl['total_cost_basis']
            },
            "realized": realized_pnl,
            "unrealized": unrealized_pnl,
            "report_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "period_days": days
        }
        
    except Exception as e:
        print(f"Error generating comprehensive P&L report: {e}")
        return {"error": str(e)}

def update_unrealized_pnl_history():
    """Update unrealized P&L history in profit_and_loss table (for tracking over time)"""
    db = None
    try:
        db = get_db_connection()
        if not db:
            return False
        
        cursor = db.cursor(dictionary=True)
        
        # Get current unrealized P&L for all holdings
        unrealized_data = calculate_unrealized_pnl()
        
        if 'error' in unrealized_data:
            return False
        
        # Record unrealized P&L for each holding
        for holding in unrealized_data['holdings']:
            cursor.execute("""
                INSERT INTO profit_and_loss (stock_symbol, trade_id, unrealized_pnl, calculation_date)
                VALUES (%s, %s, %s, %s)
            """, (holding['symbol'], None, holding['unrealized_pnl'], datetime.datetime.now()))
        
        db.commit()
        print(f"Updated unrealized P&L history for {len(unrealized_data['holdings'])} holdings")
        return True
        
    except Exception as e:
        print(f"Error updating unrealized P&L history: {e}")
        return False
    finally:
        if db:
            db.close()
