import mysql.connector
from .utils import get_db_connection
from typing import List, Dict, Optional

def get_sector_emoji(sector: str) -> str:
    """Return emoji based on sector"""
    sector_emojis = {
        'Technology': '💻',
        'Health Care': '🏥', 
        'Finance': '💰',
        'Consumer Discretionary': '🛍️',
        'Consumer Staples': '🛒',
        'Industrials': '🏭',
        'Basic Materials': '⚗️',
        'Energy': '⚡',
        'Real Estate': '🏠',
        'Utilities': '⚙️',
        'Communication Services': '📡',
        'Telecommunications': '📞'
    }
    return sector_emojis.get(sector, '📈')

def format_market_cap(market_cap: int) -> str:
    """Format market cap in readable format"""
    if market_cap == 0:
        return "N/A"
    elif market_cap >= 1_000_000_000_000:  # Trillion
        return f"${market_cap / 1_000_000_000_000:.1f}T"
    elif market_cap >= 1_000_000_000:  # Billion
        return f"${market_cap / 1_000_000_000:.1f}B"
    elif market_cap >= 1_000_000:  # Million
        return f"${market_cap / 1_000_000:.1f}M"
    else:
        return f"${market_cap:,}"

def search_stocks_by_name(query: str, limit: int = 20) -> List[Dict]:
    """
    Search for stocks by company name or symbol
    Returns results ordered by market cap (descending)
    """
    if not query or len(query.strip()) < 2:
        return []
    
    db = get_db_connection()
    if not db:
        return []
    
    try:
        cursor = db.cursor(dictionary=True)
        
        # Search both by name and symbol, prioritizing exact symbol matches
        search_term = f"%{query.strip()}%"
        
        search_query = """
        SELECT Symbol, Name, Sector, MarketCap,
               CASE 
                   WHEN Symbol = %s THEN 1  -- Exact symbol match gets highest priority
                   WHEN Symbol LIKE %s THEN 2  -- Symbol starts with query
                   WHEN Name LIKE %s THEN 3   -- Name contains query
                   ELSE 4
               END as priority
        FROM nasdaq_companies 
        WHERE Symbol LIKE %s 
           OR Name LIKE %s
        ORDER BY priority ASC, MarketCap DESC
        LIMIT %s
        """
        
        cursor.execute(search_query, (
            query.upper().strip(),  # For exact symbol match
            f"{query.upper().strip()}%",  # For symbol starts with
            search_term,  # For name contains
            f"%{query.upper().strip()}%",  # For symbol contains
            search_term,  # For name contains (duplicate for WHERE clause)
            limit
        ))
        
        results = cursor.fetchall()
        
        # Format results with emojis and readable market cap
        formatted_results = []
        for row in results:
            formatted_results.append({
                'symbol': row['Symbol'],
                'name': row['Name'],
                'sector': row['Sector'] or 'Other',
                'market_cap': row['MarketCap'] or 0,
                'market_cap_formatted': format_market_cap(row['MarketCap'] or 0),
                'sector_emoji': get_sector_emoji(row['Sector'] or 'Other'),
                'display_name': f"{get_sector_emoji(row['Sector'] or 'Other')} {row['Name']}"
            })
        
        return formatted_results
        
    except Exception as e:
        print(f"Error searching stocks: {e}")
        return []
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()

def get_stock_details_by_symbol(symbol: str) -> Optional[Dict]:
    """
    Get detailed information for a specific stock symbol
    """
    if not symbol:
        return None
    
    db = get_db_connection()
    if not db:
        return None
    
    try:
        cursor = db.cursor(dictionary=True)
        
        query = """
        SELECT Symbol, Name, Sector, MarketCap
        FROM nasdaq_companies 
        WHERE Symbol = %s
        """
        
        cursor.execute(query, (symbol.upper(),))
        result = cursor.fetchone()
        
        if result:
            return {
                'symbol': result['Symbol'],
                'name': result['Name'],
                'sector': result['Sector'] or 'Other',
                'market_cap': result['MarketCap'] or 0,
                'market_cap_formatted': format_market_cap(result['MarketCap'] or 0),
                'sector_emoji': get_sector_emoji(result['Sector'] or 'Other'),
                'display_name': f"{get_sector_emoji(result['Sector'] or 'Other')} {result['Name']}"
            }
        
        return None
        
    except Exception as e:
        print(f"Error getting stock details: {e}")
        return None
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()

def get_top_stocks_by_sector(sector: str = None, limit: int = 10) -> List[Dict]:
    """
    Get top stocks by market cap, optionally filtered by sector
    """
    db = get_db_connection()
    if not db:
        return []
    
    try:
        cursor = db.cursor(dictionary=True)
        
        if sector:
            query = """
            SELECT Symbol, Name, Sector, MarketCap
            FROM nasdaq_companies 
            WHERE Sector = %s AND MarketCap > 0
            ORDER BY MarketCap DESC
            LIMIT %s
            """
            cursor.execute(query, (sector, limit))
        else:
            query = """
            SELECT Symbol, Name, Sector, MarketCap
            FROM nasdaq_companies 
            WHERE MarketCap > 0
            ORDER BY MarketCap DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
        
        results = cursor.fetchall()
        
        # Format results
        formatted_results = []
        for row in results:
            formatted_results.append({
                'symbol': row['Symbol'],
                'name': row['Name'],
                'sector': row['Sector'] or 'Other',
                'market_cap': row['MarketCap'] or 0,
                'market_cap_formatted': format_market_cap(row['MarketCap'] or 0),
                'sector_emoji': get_sector_emoji(row['Sector'] or 'Other'),
                'display_name': f"{get_sector_emoji(row['Sector'] or 'Other')} {row['Name']}"
            })
        
        return formatted_results
        
    except Exception as e:
        print(f"Error getting top stocks: {e}")
        return []
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()

def get_all_sectors() -> List[str]:
    """
    Get all unique sectors from nasdaq companies
    """
    db = get_db_connection()
    if not db:
        return []
    
    try:
        cursor = db.cursor()
        
        query = """
        SELECT DISTINCT Sector 
        FROM nasdaq_companies 
        WHERE Sector IS NOT NULL 
        ORDER BY Sector
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        return [row[0] for row in results if row[0]]
        
    except Exception as e:
        print(f"Error getting sectors: {e}")
        return []
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()
