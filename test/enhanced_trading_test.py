#!/usr/bin/env python3
"""
Test script for enhanced trading system with database-first, API-fallback price fetching
"""

import sys
import os

# Add the backend directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))
sys.path.insert(0, os.path.join(project_root, 'backend', 'app'))

from backend.app.buy import buy_stock, get_current_price
from backend.app.sell import sell_stock
from backend.app.buyRequest import buyRequest
from backend.app.sellRequest import sellRequest
from backend.app.portfolio import get_cash_balance, get_portfolio_summary

def test_price_fetching():
    """Test the enhanced price fetching logic"""
    print("=" * 60)
    print("🧪 TESTING ENHANCED PRICE FETCHING")
    print("=" * 60)
    
    # Test symbols - mix of ones in database and new ones
    test_symbols = ['AAPL', 'MSFT', 'GME']  
    
    for symbol in test_symbols:
        print(f"\n📊 Testing price fetching for {symbol}:")
        price_data = get_current_price(symbol)
        
        if 'error' in price_data:
            print(f"❌ Error: {price_data['error']}")
        else:
            print(f"✅ Price: ${price_data['current_price']:.2f}")
            print(f"📍 Source: {price_data['source']}")
            print(f"🕐 Last updated: {price_data['last_updated']}")

def test_enhanced_buy():
    """Test buy operation with enhanced price fetching"""
    print("\n" + "=" * 60)
    print("🛒 TESTING ENHANCED BUY OPERATION")
    print("=" * 60)
    
    # Test buying a stock that should be in database
    print(f"\n💰 Current cash balance:")
    cash_result = get_cash_balance('default_user')
    print(f"Cash: ${cash_result.get('cash_balance', 0):.2f}")
    
    print(f"\n🛒 Attempting to buy 5 shares of AAPL:")
    buy_req = buyRequest('AAPL', 5)
    result = buy_stock(buy_req, user_id='default_user')
    print(f"Result: {result}")
    
    # Test buying a stock that might not be in database
    print(f"\n🛒 Attempting to buy 1 share of GOOGL (testing API fallback):")
    buy_req = buyRequest('GOOGL', 1)
    result = buy_stock(buy_req, user_id='default_user')
    print(f"Result: {result}")

def test_enhanced_sell():
    """Test sell operation with enhanced price fetching"""
    print("\n" + "=" * 60)
    print("💸 TESTING ENHANCED SELL OPERATION")
    print("=" * 60)
    
    # Show current holdings
    print(f"\n📊 Current portfolio:")
    portfolio = get_portfolio_summary()
    if 'holdings' in portfolio:
        for holding in portfolio['holdings']:
            print(f"  {holding['stock_symbol']}: {holding['quantity']} shares @ ${holding['average_cost']:.2f}")
    
    print(f"\n💸 Attempting to sell 2 shares of AAPL:")
    sell_req = sellRequest('AAPL', 2)
    result = sell_stock(sell_req, user_id='default_user')
    print(f"Result: {result}")

def test_complete_workflow():
    """Test complete trading workflow"""
    print("\n" + "=" * 60)
    print("🔄 TESTING COMPLETE WORKFLOW")
    print("=" * 60)
    
    # 1. Check initial cash
    print(f"\n💰 Step 1: Initial cash balance")
    cash_result = get_cash_balance('default_user')
    initial_cash = cash_result.get('cash_balance', 0)
    print(f"Initial cash: ${initial_cash:.2f}")
    
    # 2. Buy some shares
    print(f"\n🛒 Step 2: Buy 3 shares of MSFT")
    buy_req = buyRequest('MSFT', 3)
    buy_result = buy_stock(buy_req, user_id='default_user')
    print(f"Buy result: {buy_result}")
    
    # 3. Check portfolio
    print(f"\n📊 Step 3: Check portfolio after buy")
    portfolio = get_portfolio_summary()
    print(f"Portfolio value: ${portfolio.get('total_value', 0):.2f}")
    
    # 4. Sell some shares
    print(f"\n💸 Step 4: Sell 1 share of MSFT")
    sell_req = sellRequest('MSFT', 1)
    sell_result = sell_stock(sell_req, user_id='default_user')
    print(f"Sell result: {sell_result}")
    
    # 5. Final cash balance
    print(f"\n💰 Step 5: Final cash balance")
    cash_result = get_cash_balance('default_user')
    final_cash = cash_result.get('cash_balance', 0)
    print(f"Final cash: ${final_cash:.2f}")
    print(f"Cash change: ${final_cash - initial_cash:.2f}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Trading System Tests")
    print("=" * 60)
    
    try:
        # Test 1: Price fetching logic
        test_price_fetching()
        
        # Test 2: Enhanced buy operation
        test_enhanced_buy()
        
        # Test 3: Enhanced sell operation
        test_enhanced_sell()
        
        # Test 4: Complete workflow
        test_complete_workflow()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
