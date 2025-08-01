import requests
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://www.alphavantage.co/query"

# Simple API Key rotation
API_KEYS = [key.strip() for key in os.getenv("ALPHA_VANTAGE_KEY", "").split(",") if key.strip()]
current_key_index = 0

def get_next_api_key():
    """Get next API key in rotation"""
    global current_key_index
    if not API_KEYS:
        raise ValueError("No API keys configured")
    
    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return key

def make_api_request(params: Dict) -> Dict:
    """Make API request with simple key rotation on failure"""
    max_attempts = len(API_KEYS) if API_KEYS else 1
    
    for attempt in range(max_attempts):
        try:
            params["apikey"] = get_next_api_key()
            r = requests.get(BASE_URL, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            # Check for rate limit in response
            if "Error Message" in data and "rate limit" in data["Error Message"].lower():
                print(f"Rate limit hit, trying next key... (attempt {attempt + 1})")
                continue
            if "Note" in data and "rate limit" in data["Note"].lower():
                print(f"Rate limit hit, trying next key... (attempt {attempt + 1})")
                continue
                
            return data
            
        except Exception as e:
            print(f"API call failed (attempt {attempt + 1}): {e}")
            if attempt == max_attempts - 1:
                raise e
    
    raise Exception("All API keys failed")

def get_quote(symbol: str) -> Dict:
    """Get real-time stock quote data"""
    print(f"Fetching quote data for {symbol}...")
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
    }
    data = make_api_request(params)
    result = data.get("Global Quote", {})
    print(f"Quote data retrieved for {symbol}")
    return result

def get_stock_overview(symbol: str) -> Dict:
    """Get comprehensive company overview and fundamentals"""
    print(f"Fetching company overview for {symbol}...")
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
    }
    data = make_api_request(params)
    print(f"Company overview retrieved for {symbol}")
    return data

def get_intraday_data(symbol: str, interval: str = "5min") -> Dict:
    """Get intraday stock data with specified interval"""
    print(f"Fetching intraday data for {symbol} ({interval} intervals)...")
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
    }
    data = make_api_request(params)
    print(f"Intraday data retrieved for {symbol}")
    return data

def get_daily_data(symbol: str) -> Dict:
    """Get daily stock data"""
    print(f"Fetching daily data for {symbol}...")
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
    }
    data = make_api_request(params)
    print(f"Daily data retrieved for {symbol}")
    return data

def get_news_sentiment(symbol: str, topics: Optional[str] = None) -> Dict:
    """Get news and sentiment data for a stock"""
    print(f"Fetching news and sentiment for {symbol}...")
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
    }
    if topics:
        params["topics"] = topics
    
    data = make_api_request(params)
    print(f"News and sentiment data retrieved for {symbol}")
    return data

def get_company_earnings(symbol: str) -> Dict:
    """Get company earnings data"""
    print(f"Fetching earnings data for {symbol}...")
    params = {
        "function": "EARNINGS",
        "symbol": symbol,
    }
    data = make_api_request(params)
    print(f"Earnings data retrieved for {symbol}")
    return data

def test_api_connection() -> bool:
    """Test if API connection is working"""
    print("Testing API connection...")
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": "AAPL",
        }
        data = make_api_request(params)
        
        if "Global Quote" in data and data["Global Quote"]:
            print("API connection successful!")
            return True
        else:
            print("API connection failed - Invalid response")
            return False
    except Exception as e:
        print(f"API connection failed: {str(e)}")
        return False
