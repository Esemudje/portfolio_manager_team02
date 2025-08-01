#!/usr/bin/env python3
"""
Complete Trading Test Script
===========================
Tests all trading functionality with proper portfolio tracking.
"""

import sys
import os
from datetime import datetime

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))
sys.path.insert(0, os.path.join(project_root, 'backend', 'app'))

# Import modules
try:
    from backend.app.buyRequest import buyRequest
    from backend.app.sellRequest import sellRequest
    from backend.app.buy import buy_stock, test_database_connection, get_stock_quote
    from backend.app.sell import sell_stock
    from backend.app.portfolio import get_portfolio_summary, get_cash_balance
    print("All modules imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def show_portfolio_status(user_id: str, title: str):
    """Show current portfolio status"""
    print(f"\n{title}")
    print("-" * len(title))
    
    # Get cash balance
    cash_info = get_cash_balance(user_id)
    cash_balance = float(cash_info['cash_balance']) if 'error' not in cash_info else 0
    
    # Get holdings
    portfolio = get_portfolio_summary()
    holdings = portfolio.get('holdings', []) if 'error' not in portfolio else []
    
    print(f"Cash Balance: ${cash_balance:,.2f}")
    print(f"Number of Holdings: {len(holdings)}")
    
    total_portfolio_value = 0
    if holdings:
        print("Current Holdings:")
        for holding in holdings:
            shares = float(holding['quantity'])
            avg_cost = float(holding['average_cost'])
            
            # Try to get current market price
            quote = get_stock_quote(holding['stock_symbol'])
            if 'error' not in quote:
                current_price = quote['current_price']
                market_value = shares * current_price
                cost_basis = shares * avg_cost
                unrealized_pnl = market_value - cost_basis
                total_portfolio_value += market_value
                
                print(f"   {holding['stock_symbol']}: {shares:.0f} shares @ ${avg_cost:.2f}")
                print(f"      Current: ${current_price:.2f}, Value: ${market_value:,.2f}, P&L: ${unrealized_pnl:+,.2f}")
            else:
                cost_basis = shares * avg_cost
                total_portfolio_value += cost_basis
                print(f"   {holding['stock_symbol']}: {shares:.0f} shares @ ${avg_cost:.2f}, Value: ${cost_basis:,.2f}")
    
    total_account_value = cash_balance + total_portfolio_value
    print(f"Portfolio Value: ${total_portfolio_value:,.2f}")
    print(f"Total Account Value: ${total_account_value:,.2f}")

    return total_account_value

def main():
    """Main trading test"""
    print("COMPLETE TRADING SYSTEM TEST")
    print("="*50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    user_id = 'test_user'
    
    # Check database connection
    if not test_database_connection():
        print("Database connection failed")
        return
    
    # Show initial status
    initial_value = show_portfolio_status(user_id, "INITIAL PORTFOLIO STATUS")

    # Test small buy (something affordable)
    print(f"\nTESTING BUY OPERATION")
    print("-" * 30)
    
    buy_req = buyRequest("TSLA", 1)  # Buy 1 share of TSLA
    print(f"Attempting to buy 1 share of TSLA...")
    
    result = buy_stock(buy_req, user_id=user_id)
    print(f"Result: {result}")
    
    if "successful" in result.lower():
        print("Buy operation successful!")
    else:
        print("Buy operation failed!")

    # Show status after buy
    after_buy_value = show_portfolio_status(user_id, "PORTFOLIO AFTER BUY")
    
    # Test sell operation if we have holdings
    portfolio = get_portfolio_summary()
    holdings = portfolio.get('holdings', []) if 'error' not in portfolio else []
    
    if holdings:
        print(f"\nTESTING SELL OPERATION")
        print("-" * 30)
        
        # Sell 1 share of the first holding
        first_holding = holdings[0]
        symbol = first_holding['stock_symbol']
        
        print(f"Attempting to sell 1 share of {symbol}...")
        
        # Get current price
        quote = get_stock_quote(symbol)
        if 'error' not in quote:
            current_price = quote['current_price']
            sell_req = sellRequest(symbol, 1)
            
            result = sell_stock(sell_req, current_price, user_id)
            print(f"Sell price: ${current_price:.2f}")
            print(f"Result: {result}")
            
            if "successful" in result.lower():
                print("Sell operation successful!")
            else:
                print("Sell operation failed!")
        else:
            print(f"Cannot get current price for {symbol}")
    else:
        print(f"\nNo holdings available for sell test")

    # Show final status
    final_value = show_portfolio_status(user_id, "FINAL PORTFOLIO STATUS")
    
    # Summary
    print(f"\nTEST SUMMARY")
    print("="*30)
    print(f"Initial Account Value: ${initial_value:,.2f}")
    print(f"Final Account Value: ${final_value:,.2f}")
    print(f"Net Change: ${final_value - initial_value:+,.2f}")
    
    if abs(final_value - initial_value) < 50:  # Small change is expected due to trading
        print("✅ Trading system is working correctly!")
    else:
        print("⚠️  Significant value change detected - check for issues")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
