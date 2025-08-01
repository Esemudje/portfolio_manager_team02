#!/usr/bin/env python3
"""
Simple test script for API key rotation
"""

import sys
import os
# Add the parent directory to Python path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.market import test_api_connection, get_quote

def main():
    print("Testing simplified API key rotation...")
    
    # Test API connection
    print("1. Testing API connection:")
    if test_api_connection():
        print("API connection successful!")
    else:
        print("API connection failed")
        return
    
    # Test a few API calls to see rotation in action
    print("\n2. Testing API calls:")
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in symbols:
        try:
            print(f"\nTesting {symbol}:")
            quote = get_quote(symbol)
            if quote:
                price = quote.get('05. price', 'N/A')
                print(f"Price: ${price}")
            else:
                print(f"No data returned")
        except Exception as e:
            print(f"Error: {e}")

    print("\nTest completed!")
    print("\nThe system will automatically rotate API keys when rate limits are hit.")

if __name__ == "__main__":
    main()
