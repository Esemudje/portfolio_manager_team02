from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    print("Starting Portfolio Manager API Server...")
    print("="*50)
    print("Server will be available at: http://localhost:8084")
    print("API endpoints:")
    print("   • GET /api/stocks/<symbol> - Real-time quote")
    print("   • GET /api/stocks/<symbol>/overview - Company overview")
    print("   • GET /api/stocks/<symbol>/intraday - Intraday data")
    print("   • GET /api/stocks/<symbol>/daily - Daily data")
    print("   • GET /api/stocks/<symbol>/news - News & sentiment")
    print("   • GET /api/stocks/<symbol>/earnings - Earnings data")
    print("   • GET /api/test-connection - Test API connection")
    print("="*50)
    
    # Check for API keys
    api_keys_str = os.getenv("ALPHA_VANTAGE_KEY")
    if not api_keys_str:
        print("WARNING: ALPHA_VANTAGE_KEY not found in environment!")
        print("   Please set your API key(s) in .env file")
    else:
        api_keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
        print(f"Alpha Vantage API key(s) configured: {len(api_keys)} key(s)")
        if len(api_keys) > 1:
            print("   Multiple keys detected - rotation will be used on rate limits")


    print("\nStarting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=8084)
