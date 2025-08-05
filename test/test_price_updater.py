#!/usr/bin/env python3
"""
Price Updater Test Script
========================
Test the background price updater functionality.
"""

import sys
import os
from datetime import datetime

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))
sys.path.insert(0, os.path.join(project_root, 'backend', 'app'))

try:
    from backend.app.price_updater import (
        get_owned_symbols, 
        update_single_stock_price, 
        manual_price_update
    )
    from backend.app.buy import test_database_connection
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_price_updater():
    """Test the price updater functionality"""
    print("PRICE UPDATER TEST")
    print("="*50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check database connection
    if not test_database_connection():
        print("❌ Database connection failed")
        return
    print("✅ Database connection successful")
    
    # Test getting owned symbols
    print("\n1. Testing get_owned_symbols()...")
    owned_symbols = get_owned_symbols()
    print(f"   Found {len(owned_symbols)} owned symbols: {owned_symbols}")
    
    if not owned_symbols:
        print("⚠️  No owned stocks found. Buy some stocks first to test price updates.")
        return
    
    # Test updating a single stock
    print(f"\n2. Testing single stock update for {owned_symbols[0]}...")
    test_symbol = owned_symbols[0]
    success = update_single_stock_price(test_symbol)
    if success:
        print(f"✅ Successfully updated {test_symbol}")
    else:
        print(f"❌ Failed to update {test_symbol}")
    
    # Test updating all owned stocks
    print(f"\n3. Testing update_all_owned_prices()...")
    results = manual_price_update()
    
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    print(f"   Results: {successful}/{total} successful updates")
    
    for symbol, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {symbol}")
    
    if successful == total and total > 0:
        print("\n🎉 All price updates successful!")
    elif successful > 0:
        print(f"\n⚠️  Partial success: {successful}/{total} updates completed")
    else:
        print("\n❌ All price updates failed")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_price_updater()
