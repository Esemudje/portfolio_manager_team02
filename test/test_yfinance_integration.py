#!/usr/bin/env python3
"""
Test script to verify yFinance integration is working properly
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))
sys.path.insert(0, os.path.join(project_root, 'backend', 'app'))


from backend.app.market import (
    test_api_connection,
    get_quote,
    get_stock_overview,
    get_intraday_data,
    get_daily_data,
    get_news_sentiment,
    get_company_earnings
)

def test_yfinance_functions():
    """Test all yFinance functions"""
    print("="*60)
    print("TESTING YFINANCE INTEGRATION")
    print("="*60)
    
    # Test API connection
    print("\n1. Testing API Connection...")
    connection_ok = test_api_connection()
    print(f"   Result: {'SUCCESS' if connection_ok else 'FAILED'}")
    
    if not connection_ok:
        print("yFinance connection failed. Exiting tests.")
        return
    
    symbol = "TSLA"
    print(f"\n2. Testing Stock Quote for {symbol}...")
    try:
        quote = get_quote(symbol)
        if quote and '05. price' in quote:
            price = quote['05. price']
            change = quote.get('09. change', 'N/A')
            print(f" Price: ${price}")
            print(f" Change: {change}")
            print(f" Symbol: {quote.get('01. symbol', 'N/A')}")
        else:
            print(" No quote data received")
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"\n3. Testing Company Overview for {symbol}...")
    try:
        overview = get_stock_overview(symbol)
        if overview:
            print(f" Company: {overview.get('Name', 'N/A')}")
            print(f" Sector: {overview.get('Sector', 'N/A')}")
            print(f" Market Cap: {overview.get('MarketCapitalization', 'N/A')}")
        else:
            print("  No overview data received")
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"\n4. Testing Intraday Data for {symbol}...")
    try:
        intraday = get_intraday_data(symbol, "5min")
        if intraday and 'Time Series (5min)' in intraday:
            data_points = len(intraday['Time Series (5min)'])
            print(f"   Received {data_points} intraday data points")
        else:
            print("   No intraday data received")
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"\n5. Testing Daily Data for {symbol}...")
    try:
        daily = get_daily_data(symbol)
        if daily and 'Time Series (Daily)' in daily:
            data_points = len(daily['Time Series (Daily)'])
            print(f"   Received {data_points} daily data points")
        else:
            print("   No daily data received")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    test_yfinance_functions()
