import requests
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHA_VANTAGE_KEY")

def get_quote(symbol: str) -> Dict:
    """Get real-time stock quote data"""
    print(f"Fetching quote data for {symbol}...")
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("Global Quote", {})
    print(f"Quote data retrieved for {symbol}")
    return data

def get_stock_overview(symbol: str) -> Dict:
    """Get comprehensive company overview and fundamentals"""
    print(f"Fetching company overview for {symbol}...")
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    print(f"Company overview retrieved for {symbol}")
    return data

def get_intraday_data(symbol: str, interval: str = "5min") -> Dict:
    """Get intraday stock data with specified interval"""
    print(f"Fetching intraday data for {symbol} ({interval} intervals)...")
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    print(f"Intraday data retrieved for {symbol}")
    return data

def get_daily_data(symbol: str) -> Dict:
    """Get daily stock data"""
    print(f"Fetching daily data for {symbol}...")
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    print(f"Daily data retrieved for {symbol}")
    return data

def get_news_sentiment(symbol: str, topics: Optional[str] = None) -> Dict:
    """Get news and sentiment data for a stock"""
    print(f"Fetching news and sentiment for {symbol}...")
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "apikey": API_KEY,
    }
    if topics:
        params["topics"] = topics
    
    r = requests.get(BASE_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    print(f"News and sentiment data retrieved for {symbol}")
    return data

def get_company_earnings(symbol: str) -> Dict:
    """Get company earnings data"""
    print(f"Fetching earnings data for {symbol}...")
    params = {
        "function": "EARNINGS",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    print(f"Earnings data retrieved for {symbol}")
    return data

def test_api_connection() -> bool:
    """Test if API connection is working"""
    print("Testing API connection...")
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": "AAPL",
            "apikey": API_KEY,
        }
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            print("API connection successful!")
            return True
        else:
            print("API connection failed - Invalid response")
            return False
    except Exception as e:
        print(f"API connection failed: {str(e)}")
        return False
