from app import create_app
from app.order_service import start_order_service, stop_order_service
import os
import atexit

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
    print("   • POST /api/orders - Place enhanced orders")
    print("   • GET /api/orders - Get pending orders")
    print("   • DELETE /api/orders/<id> - Cancel order")
    print("="*50)
    
    # Start the order execution service
    print("Starting order execution service...")
    start_order_service()
    
    # Register cleanup function
    atexit.register(stop_order_service)

    print("\nStarting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=8084)
