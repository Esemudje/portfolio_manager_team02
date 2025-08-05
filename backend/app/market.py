import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np

def get_quote(symbol: str) -> Dict:
    """Get real-time stock quote data using yFinance"""
    print(f"Fetching quote data for {symbol} using yFinance...")
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current quote info
        info = ticker.info
        hist = ticker.history(period="2d")  # Get last 2 days for change calculation
        
        if hist.empty or len(hist) < 1:
            print(f"No data found for symbol: {symbol}")
            return {}
        
        # Get current and previous close prices
        current_price = float(hist['Close'].iloc[-1])
        previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
        
        # Calculate change
        change_amount = current_price - previous_close
        change_percent = (change_amount / previous_close * 100) if previous_close != 0 else 0
        
        # Get other data from the latest day
        latest_data = hist.iloc[-1]
        open_price = float(latest_data['Open'])
        high_price = float(latest_data['High'])
        low_price = float(latest_data['Low'])
        volume = int(latest_data['Volume'])
        
        # Get the latest trading day
        latest_trading_day = hist.index[-1].strftime('%Y-%m-%d')
        
        # Format data to match Alpha Vantage format for compatibility
        result = {
            "01. symbol": symbol.upper(),
            "02. open": str(open_price),
            "03. high": str(high_price),
            "04. low": str(low_price),
            "05. price": str(current_price),
            "06. volume": str(volume),
            "07. latest trading day": latest_trading_day,
            "08. previous close": str(previous_close),
            "09. change": str(change_amount),
            "10. change percent": f"{change_percent:.2f}%"
        }
        
        print(f"Quote data retrieved for {symbol}: ${current_price:.2f}")
        return result
        
    except Exception as e:
        print(f"Error fetching quote for {symbol}: {str(e)}")
        return {}

def get_stock_overview(symbol: str) -> Dict:
    """Get essential company overview and key fundamentals using yFinance"""
    print(f"Fetching company overview for {symbol} using yFinance...")
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Helper function to format large numbers
        def format_large_number(value):
            if value is None or value == "N/A":
                return "N/A"
            try:
                num = float(value)
                if num >= 1e12:
                    return f"{num/1e12:.2f}T"
                elif num >= 1e9:
                    return f"{num/1e9:.2f}B"
                elif num >= 1e6:
                    return f"{num/1e6:.2f}M"
                else:
                    return f"{num:,.0f}"
            except (ValueError, TypeError):
                return "N/A"
        
        # Helper function to format percentage
        def format_percentage(value):
            if value is None or value == "N/A":
                return "N/A"
            try:
                num = float(value)
                return f"{num*100:.2f}%" if num < 1 else f"{num:.2f}%"
            except (ValueError, TypeError):
                return "N/A"
        
        # Helper function to format decimal values
        def format_decimal(value, decimals=2):
            if value is None or value == "N/A":
                return "N/A"
            try:
                return f"{float(value):.{decimals}f}"
            except (ValueError, TypeError):
                return "N/A"
        
        # Helper function to truncate description
        def truncate_description(description):
            if description == "N/A" or description is None:
                return "N/A"
            return description[:500] + "..." if len(description) > 500 else description
        
        # Return only essential information for display
        overview = {
            # Basic Company Info
            "Symbol": info.get("symbol", symbol.upper()),
            "Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Exchange": info.get("exchange", "N/A"),
            "Currency": info.get("currency", "USD"),
            "Country": info.get("country", "N/A"),
            
            # Key Financial Metrics
            "MarketCapitalization": format_large_number(info.get("marketCap")),
            "PERatio": format_decimal(info.get("trailingPE")),
            "EPS": format_decimal(info.get("trailingEps")),
            "Beta": format_decimal(info.get("beta")),
            
            # Dividend Information
            "DividendYield": format_percentage(info.get("dividendYield")),
            "DividendPerShare": format_decimal(info.get("dividendRate")),
            
            # Price Ranges
            "52WeekHigh": format_decimal(info.get("fiftyTwoWeekHigh")),
            "52WeekLow": format_decimal(info.get("fiftyTwoWeekLow")),
            
            # Valuation Metrics
            "PriceToBookRatio": format_decimal(info.get("priceToBook")),
            "ProfitMargin": format_percentage(info.get("profitMargins")),
            
            # Volume and Shares
            "SharesOutstanding": format_large_number(info.get("sharesOutstanding")),
            "FullTimeEmployees": format_large_number(info.get("fullTimeEmployees")),
            
            # Business Description (truncated for display)
            "Description": truncate_description(info.get("longBusinessSummary", "N/A"))
        }
        
        print(f"Company overview retrieved for {symbol}")
        return overview
        
    except Exception as e:
        print(f"Error fetching overview for {symbol}: {str(e)}")
        return {}

def get_intraday_data(symbol: str, interval: str = "5min") -> Dict:
    """Get intraday stock data with specified interval using yFinance"""
    print(f"Fetching intraday data for {symbol} ({interval} intervals) using yFinance...")
    try:
        ticker = yf.Ticker(symbol)
        
        # Map interval to yFinance format
        yf_interval_map = {
            "1min": "1m",
            "5min": "5m",
            "15min": "15m",
            "30min": "30m",
            "60min": "1h"
        }
        
        yf_interval = yf_interval_map.get(interval, "5m")
        
        # Get intraday data for the last 7 days (yFinance limit for minute data)
        hist = ticker.history(period="7d", interval=yf_interval)
        
        if hist.empty:
            print(f"No intraday data found for symbol: {symbol}")
            return {}
        
        # Convert to Alpha Vantage format
        time_series = {}
        for timestamp, row in hist.iterrows():
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            time_series[time_str] = {
                "1. open": str(float(row['Open'])),
                "2. high": str(float(row['High'])),
                "3. low": str(float(row['Low'])),
                "4. close": str(float(row['Close'])),
                "5. volume": str(int(row['Volume']))
            }
        
        result = {
            f"Time Series ({interval})": time_series,
            "Meta Data": {
                "1. Information": f"Intraday ({interval}) open, high, low, close prices and volume",
                "2. Symbol": symbol.upper(),
                "3. Last Refreshed": hist.index[-1].strftime('%Y-%m-%d %H:%M:%S'),
                "4. Interval": interval,
                "5. Output Size": "Compact",
                "6. Time Zone": "US/Eastern"
            }
        }
        
        print(f"Intraday data retrieved for {symbol}")
        return result
        
    except Exception as e:
        print(f"Error fetching intraday data for {symbol}: {str(e)}")
        return {}

def get_daily_data(symbol: str) -> Dict:
    """Get daily stock data using yFinance"""
    print(f"Fetching daily data for {symbol} using yFinance...")
    try:
        ticker = yf.Ticker(symbol)
        
        # Get daily data for the last year
        hist = ticker.history(period="1y", interval="1d")
        
        if hist.empty:
            print(f"No daily data found for symbol: {symbol}")
            return {}
        
        # Convert to Alpha Vantage format
        time_series = {}
        for date, row in hist.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            time_series[date_str] = {
                "1. open": str(float(row['Open'])),
                "2. high": str(float(row['High'])),
                "3. low": str(float(row['Low'])),
                "4. close": str(float(row['Close'])),
                "5. volume": str(int(row['Volume']))
            }
        
        result = {
            "Time Series (Daily)": time_series,
            "Meta Data": {
                "1. Information": "Daily Prices (open, high, low, close) and Volume",
                "2. Symbol": symbol.upper(),
                "3. Last Refreshed": hist.index[-1].strftime('%Y-%m-%d'),
                "4. Output Size": "Compact",
                "5. Time Zone": "US/Eastern"
            }
        }
        
        print(f"Daily data retrieved for {symbol}")
        return result
        
    except Exception as e:
        print(f"Error fetching daily data for {symbol}: {str(e)}")
        return {}


def test_api_connection() -> bool:
    """Test if yFinance is working"""
    print("Testing yFinance connection...")
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            print("yFinance connection successful!")
            return True
        else:
            print("yFinance connection failed - No data returned")
            return False
    except Exception as e:
        print(f"yFinance connection failed: {str(e)}")
        return False
