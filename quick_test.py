#!/usr/bin/env python3
"""
Quick API Test Script
====================
A simple script to test basic API functionality without external dependencies.
Run this after starting the Flask server to verify everything is working.
"""

import urllib.request
import urllib.parse
import json
import os
from datetime import datetime

def test_endpoint(url, description):
    """Test a single endpoint with basic urllib"""
    print(f"\nTesting: {description}")
    print(f"URL: {url}")

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                print(f"Success! Status: {response.getcode()}")
                
                # Print some basic info about the response
                if isinstance(data, dict):
                    print(f"Response has {len(data)} fields")

                    # For quote data
                    if "Global Quote" in data:
                        quote = data["Global Quote"]
                        symbol = quote.get("01. symbol", "N/A")
                        price = quote.get("05. price", "N/A")
                        print(f"Symbol: {symbol}")
                        print(f"Price: ${price}")
                    
                    # For overview data
                    elif "Symbol" in data:
                        symbol = data.get("Symbol", "N/A")
                        name = data.get("Name", "N/A")
                        print(f"Symbol: {symbol}")
                        print(f"Company: {name}")

                    # For news data
                    elif "feed" in data:
                        feed = data.get("feed", [])
                        print(f"News articles: {len(feed)}")

                return True
            else:
                print(f"Failed with status: {response.getcode()}")
                return False
                
    except urllib.error.URLError as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run basic API tests"""
    print("Portfolio Manager API Quick Test")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    base_url = "http://localhost:5000"
    test_symbol = "TSLA"
    
    tests = [
        (f"{base_url}/", "Server health check"),
        (f"{base_url}/api/test-connection", "API connection test"),
        (f"{base_url}/api/stocks/{test_symbol}", f"Stock quote for {test_symbol}"),
        (f"{base_url}/api/stocks/{test_symbol}/overview", f"Company overview for {test_symbol}"),
    ]
    
    passed = 0
    total = len(tests)
    
    for url, description in tests:
        if test_endpoint(url, description):
            passed += 1
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("All tests passed! Your API is working!")
    else:
        print("Some tests failed. Check server logs for details.")

    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
